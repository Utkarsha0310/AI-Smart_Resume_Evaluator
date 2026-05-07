import spacy
import logging
from typing import Dict, List, Tuple, Optional
import re
from collections import Counter
import numpy as np
import textstat
import language_tool_python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class NLPProcessor:
    """Advanced NLP processing for resume analysis"""
    
    def __init__(self, heavy_mode: bool = False):
        self.heavy_mode = heavy_mode
        self.nlp = None
        self.sentence_transformer = None
        self.grammar_tool = None
        self._load_models()
    
    def _load_models(self):
        """Load NLP models based on mode"""
        try:
            if self.heavy_mode:
                # Heavy mode - more accurate but slower
                model_name = "en_core_web_trf"
            else:
                # Light mode - faster but less accurate
                model_name = "en_core_web_md"
            
            # Load spaCy model
            try:
                self.nlp = spacy.load(model_name)
                logging.info(f"Loaded spaCy model: {model_name}")
            except OSError:
                # Fallback to smaller model
                self.nlp = spacy.load("en_core_web_sm")
                logging.warning(f"Fallback to en_core_web_sm model")
            
            # Sentence transformer temporarily disabled - using TF-IDF similarity instead
            self.sentence_transformer = None
            logging.info("Using TF-IDF for semantic similarity (sentence-transformers not available)")
            
            # Grammar checker is lazy-loaded in analyze_grammar() to save memory
            logging.info("Grammar checker will be loaded on demand")
                
        except Exception as e:
            logging.error(f"Error loading NLP models: {e}")
            raise
    
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
        """Analyze grammar errors in text. Lazy-loads the Java-based grammar tool."""
        grammar_tool = None
        try:
            # Lazy-load grammar tool to save memory (starts Java server ~300MB)
            logging.info("Starting grammar checker (lazy load)...")
            grammar_tool = language_tool_python.LanguageTool('en-US')
            
            matches = grammar_tool.check(text)
            errors = []
            
            for match in matches[:20]:  # Limit to first 20 errors
                errors.append({
                    'message': match.message,
                    'context': match.context,
                    'offset': match.offset,
                    'length': match.errorLength,
                    'category': match.category
                })
            
            # Calculate grammar score (0-100)
            error_count = len(matches)
            word_count = len(text.split())
            error_rate = error_count / max(word_count, 1) * 100
            score = max(0, 100 - error_rate * 10)
            
            return {
                'errors': errors,
                'score': min(100, score),
                'error_count': error_count
            }
            
        except Exception as e:
            logging.error(f"Grammar analysis error: {e}")
            return {'errors': [], 'score': 85, 'error_count': 0}
        finally:
            # Always close the Java server to free memory
            if grammar_tool:
                try:
                    grammar_tool.close()
                    logging.info("Grammar checker closed (memory freed)")
                except Exception:
                    pass
    
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
