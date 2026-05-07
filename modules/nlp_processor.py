import spacy
import logging
from typing import Dict, List, Tuple, Optional
import re
from collections import Counter
import numpy as np
import textstat
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ── Singleton spaCy model (loaded ONCE at startup, shared across requests) ──
_spacy_model = None

def get_spacy_model():
    """Load spaCy model once and reuse across all requests."""
    global _spacy_model
    if _spacy_model is None:
        for model_name in ["en_core_web_sm"]:
            try:
                _spacy_model = spacy.load(model_name)
                logging.info(f"Loaded spaCy model: {model_name}")
                break
            except OSError:
                logging.warning(f"spaCy model {model_name} not found")
        if _spacy_model is None:
            raise RuntimeError("No spaCy model available")
    return _spacy_model


class NLPProcessor:
    """Advanced NLP processing for resume analysis"""
    
    def __init__(self, heavy_mode: bool = False):
        self.heavy_mode = heavy_mode
        self.nlp = get_spacy_model()  # Reuse singleton — no reload
        self.sentence_transformer = None
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text"""
        if not self.nlp:
            return {}
        
        doc = self.nlp(text)
        entities = {}
        
        for ent in doc.ents:
            label = ent.label_
            if label not in entities:
                entities[label] = []
            entities[label].append(ent.text)
        
        return entities
    
    def analyze_grammar(self, text: str) -> Dict[str, any]:
        """Analyze grammar using spaCy + regex rules (pure Python, no Java).
        
        Checks for common grammar issues:
        - Spelling errors (via spaCy's vocab)
        - Sentence structure issues
        - Capitalization errors
        - Punctuation problems
        - Common resume writing mistakes
        """
        errors = []
        
        try:
            doc = self.nlp(text)
            sentences = list(doc.sents)
            
            # 1. Check for sentences not starting with capital letter
            for sent in sentences:
                sent_text = sent.text.strip()
                if sent_text and sent_text[0].islower():
                    errors.append({
                        'message': 'Sentence should start with a capital letter',
                        'context': sent_text[:80],
                        'offset': sent.start_char,
                        'length': 1,
                        'category': 'CAPITALIZATION'
                    })
            
            # 2. Check for repeated words (e.g., "the the")
            repeated = re.finditer(r'\b(\w+)\s+\1\b', text, re.IGNORECASE)
            for match in repeated:
                errors.append({
                    'message': f'Repeated word: "{match.group(1)}"',
                    'context': text[max(0, match.start()-20):match.end()+20],
                    'offset': match.start(),
                    'length': len(match.group()),
                    'category': 'DUPLICATION'
                })
            
            # 3. Check for very long sentences (>40 words) — bad for resumes
            for sent in sentences:
                word_count = len([t for t in sent if not t.is_punct])
                if word_count > 40:
                    errors.append({
                        'message': f'Very long sentence ({word_count} words). Consider breaking it up.',
                        'context': sent.text.strip()[:80] + '...',
                        'offset': sent.start_char,
                        'length': len(sent.text),
                        'category': 'STYLE'
                    })
            
            # 4. Check for passive voice (common resume weakness)
            passive_patterns = re.finditer(
                r'\b(was|were|been|being|is|are|am)\s+([\w]+ed|[\w]+en)\b', 
                text, re.IGNORECASE
            )
            passive_count = 0
            for match in passive_patterns:
                passive_count += 1
                if passive_count <= 5:  # Only report first 5
                    errors.append({
                        'message': f'Possible passive voice: "{match.group()}". Use active voice for stronger impact.',
                        'context': text[max(0, match.start()-20):match.end()+20],
                        'offset': match.start(),
                        'length': len(match.group()),
                        'category': 'STYLE'
                    })
            
            # 5. Check for possible misspellings using spaCy's vocabulary lookup
            # en_core_web_sm doesn't have word vectors, so we use vocab membership
            misspelled_count = 0
            common_words_to_skip = {
                'linkedin', 'github', 'stackoverflow', 'mongodb', 'postgresql',
                'mysql', 'nodejs', 'reactjs', 'vuejs', 'angularjs', 'tensorflow',
                'pytorch', 'kubernetes', 'aws', 'gcp', 'api', 'apis', 'sql',
                'html', 'css', 'php', 'ui', 'ux', 'saas', 'devops', 'ci',
                'cd', 'agile', 'scrum', 'jira', 'figma', 'kanban', 'crm',
                'erp', 'frontend', 'backend', 'fullstack', 'javascript',
                'typescript', 'django', 'flask', 'fastapi', 'nginx', 'redis'
            }
            for token in doc:
                if (not token.is_stop and not token.is_punct and not token.like_num 
                    and not token.is_space and len(token.text) > 2
                    and not token.text.isupper()  # Skip acronyms
                    and token.text.lower() not in common_words_to_skip
                    and not token.ent_type_  # Skip named entities
                    and token.text.isalpha()
                    and token.text.lower() not in self.nlp.vocab):
                    misspelled_count += 1
                    if misspelled_count <= 5:  # Only report first 5
                        errors.append({
                            'message': f'Possible spelling issue: "{token.text}"',
                            'context': text[max(0, token.idx-20):token.idx+len(token.text)+20],
                            'offset': token.idx,
                            'length': len(token.text),
                            'category': 'SPELLING'
                        })
            
            # 6. Check for missing punctuation at end of bullet points/lines
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if len(line) > 20 and line[-1].isalpha() and not line.isupper():
                    # Lines that look like bullet points without ending punctuation
                    if any(line.startswith(prefix) for prefix in ['•', '-', '▪', '●', '*']):
                        pass  # Bullet points without periods are acceptable
            
            # Calculate grammar score (0-100)
            error_count = len(errors)
            word_count = len(text.split())
            
            # Per-error deductions weighted by severity
            score = 100
            for err in errors:
                cat = err.get('category', '')
                if cat == 'SPELLING':
                    score -= 5
                elif cat == 'DUPLICATION':
                    score -= 4
                elif cat == 'CAPITALIZATION':
                    score -= 3
                elif cat == 'STYLE':
                    score -= 2  # Style suggestions are softer
                else:
                    score -= 3
            
            # Bonus for well-structured text
            if len(sentences) > 3 and error_count < 3:
                score = min(100, score + 5)
            
            return {
                'errors': errors[:20],  # Cap at 20 errors for display
                'score': round(min(100, score), 1),
                'error_count': error_count
            }
            
        except Exception as e:
            logging.error(f"Grammar analysis error: {e}")
            return {'errors': [], 'score': 85, 'error_count': 0}
    
    def calculate_readability(self, text: str) -> Dict[str, float]:
        """Calculate readability metrics"""
        try:
            flesch_ease = textstat.flesch_reading_ease(text)
            flesch_grade = textstat.flesch_kincaid_grade(text)
            
            # Normalize to 0-100 scale
            readability_score = max(0, min(100, flesch_ease))
            
            return {
                'flesch_ease': flesch_ease,
                'flesch_grade': flesch_grade,
                'score': readability_score
            }
        except Exception as e:
            logging.error(f"Readability calculation error: {e}")
            return {'flesch_ease': 60, 'flesch_grade': 8, 'score': 60}
    
    def extract_keywords(self, text: str, top_k: int = 20) -> List[Tuple[str, float]]:
        """Extract keywords using TF-IDF"""
        try:
            # Clean text
            cleaned_text = re.sub(r'[^\w\s]', ' ', text.lower())
            
            # Use spaCy for better tokenization if available
            if self.nlp:
                doc = self.nlp(cleaned_text)
                tokens = [token.lemma_ for token in doc 
                         if not token.is_stop and not token.is_punct 
                         and len(token.text) > 2]
                processed_text = ' '.join(tokens)
            else:
                processed_text = cleaned_text
            
            # TF-IDF vectorization
            vectorizer = TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2),
                stop_words='english'
            )
            
            tfidf_matrix = vectorizer.fit_transform([processed_text])
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]
            
            # Get top keywords
            keyword_scores = list(zip(feature_names, scores))
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            
            return keyword_scores[:top_k]
            
        except Exception as e:
            logging.error(f"Keyword extraction error: {e}")
            return []
    
    def analyze_structure(self, text: str) -> Dict[str, any]:
        """Analyze resume structure and sections"""
        sections = {
            'contact': 0,
            'summary': 0,
            'experience': 0,
            'education': 0,
            'skills': 0,
            'projects': 0,
            'certifications': 0
        }
        
        # Common section headers
        section_patterns = {
            'contact': r'(contact|phone|email|address|linkedin)',
            'summary': r'(summary|objective|profile|about)',
            'experience': r'(experience|work|employment|career|professional)',
            'education': r'(education|academic|degree|university|college)',
            'skills': r'(skills|competencies|technical|technologies)',
            'projects': r'(projects|portfolio|accomplishments)',
            'certifications': r'(certifications|certificates|licenses)'
        }
        
        text_lower = text.lower()
        
        for section, pattern in section_patterns.items():
            matches = re.findall(pattern, text_lower)
            sections[section] = len(matches)
        
        # Calculate structure score
        essential_sections = ['contact', 'experience', 'education', 'skills']
        found_essential = sum(1 for section in essential_sections if sections[section] > 0)
        structure_score = (found_essential / len(essential_sections)) * 100
        
        return {
            'sections': sections,
            'score': structure_score,
            'found_sections': found_essential
        }
    
    def calculate_ats_compatibility(self, text: str) -> Dict[str, any]:
        """Calculate ATS compatibility score"""
        score = 100
        issues = []
        
        # Check for common ATS-unfriendly elements
        if len(re.findall(r'[^\x00-\x7F]', text)) > 10:
            score -= 15
            issues.append("Contains special characters that may cause parsing issues")
        
        # Check for proper sections
        structure = self.analyze_structure(text)
        if structure['score'] < 75:
            score -= 20
            issues.append("Missing essential resume sections")
        
        # Check length
        word_count = len(text.split())
        if word_count < 200:
            score -= 25
            issues.append("Resume too short (under 200 words)")
        elif word_count > 1000:
            score -= 10
            issues.append("Resume may be too long for some ATS systems")
        
        # Check for contact information
        if not re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
            score -= 30
            issues.append("No email address found")
        
        if not re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text):
            score -= 15
            issues.append("No phone number found")
        
        return {
            'score': max(0, score),
            'issues': issues,
            'word_count': word_count
        }
    
    def get_text_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get text embedding using sentence transformer"""
        if not self.sentence_transformer:
            return None
        
        try:
            embedding = self.sentence_transformer.encode([text])
            return embedding[0]
        except Exception as e:
            logging.error(f"Embedding generation error: {e}")
            return None
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts"""
        if not self.sentence_transformer:
            return 0.0
        
        try:
            embeddings = self.sentence_transformer.encode([text1, text2])
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            return float(similarity)
        except Exception as e:
            logging.error(f"Similarity calculation error: {e}")
            return 0.0
    
    def analyze_action_verbs(self, text: str) -> Dict[str, any]:
        """Analyze usage of action verbs in resume"""
        action_verbs = [
            'achieved', 'administered', 'analyzed', 'built', 'created', 'designed',
            'developed', 'directed', 'established', 'executed', 'generated',
            'implemented', 'improved', 'increased', 'initiated', 'launched',
            'led', 'managed', 'optimized', 'organized', 'planned', 'produced',
            'reduced', 'resolved', 'streamlined', 'supervised', 'transformed'
        ]
        
        text_lower = text.lower()
        found_verbs = []
        
        for verb in action_verbs:
            if verb in text_lower:
                count = text_lower.count(verb)
                found_verbs.extend([verb] * count)
        
        total_verbs = len(found_verbs)
        unique_verbs = len(set(found_verbs))
        word_count = len(text.split())
        
        # Calculate score based on verb usage
        verb_density = total_verbs / max(word_count, 1) * 100
        score = min(100, verb_density * 20 + unique_verbs * 2)
        
        return {
            'total_verbs': total_verbs,
            'unique_verbs': unique_verbs,
            'verb_density': verb_density,
            'score': score,
            'found_verbs': list(set(found_verbs))
        }
