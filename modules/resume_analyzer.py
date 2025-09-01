import os
import logging
import json
import pickle
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import fitz  # PyMuPDF
from datetime import datetime
import re

from .nlp_processor import NLPProcessor
from .data_processor import DataProcessor

class ResumeAnalyzer:
    """Main resume analysis engine"""
    
    def __init__(self):
        self.data_processor = DataProcessor()
        self.exemplar_clusters = None
        self.cluster_model = None
        self.scaler = None
        self._load_exemplars()
    
    def _load_exemplars(self):
        """Load and prepare exemplar resumes from dataset"""
        try:
            # Check if processed exemplars exist
            exemplar_path = 'data/exemplar_clusters.pkl'
            if os.path.exists(exemplar_path):
                with open(exemplar_path, 'rb') as f:
                    data = pickle.load(f)
                    self.exemplar_clusters = data['clusters']
                    self.cluster_model = data['model']
                    self.scaler = data['scaler']
                logging.info("Loaded cached exemplar clusters")
                return
            
            # Process dataset and create exemplars
            dataset_path = 'data/Resume.csv'
            if os.path.exists(dataset_path):
                logging.info("Processing resume dataset for exemplars...")
                self.exemplar_clusters = self.data_processor.process_dataset(dataset_path)
                
                # Save processed data
                os.makedirs('data', exist_ok=True)
                with open(exemplar_path, 'wb') as f:
                    pickle.dump({
                        'clusters': self.exemplar_clusters,
                        'model': self.cluster_model,
                        'scaler': self.scaler
                    }, f)
                logging.info("Cached exemplar clusters")
            else:
                logging.warning("Resume dataset not found. Using fallback exemplars.")
                self._create_fallback_exemplars()
                
        except Exception as e:
            logging.error(f"Error loading exemplars: {e}")
            self._create_fallback_exemplars()
    
    def _create_fallback_exemplars(self):
        """Create fallback exemplars when dataset is not available"""
        self.exemplar_clusters = {
            'technology': {
                'keywords': ['python', 'java', 'javascript', 'sql', 'aws', 'docker', 'kubernetes'],
                'skills': ['programming', 'software development', 'web development', 'database'],
                'score_thresholds': {'formatting': 85, 'grammar': 90, 'keywords': 95, 'readability': 80, 'ats': 90}
            },
            'business': {
                'keywords': ['management', 'strategy', 'analysis', 'operations', 'leadership'],
                'skills': ['project management', 'business analysis', 'team leadership'],
                'score_thresholds': {'formatting': 80, 'grammar': 85, 'keywords': 85, 'readability': 85, 'ats': 85}
            },
            'marketing': {
                'keywords': ['marketing', 'digital', 'social media', 'campaigns', 'analytics'],
                'skills': ['digital marketing', 'content creation', 'analytics', 'branding'],
                'score_thresholds': {'formatting': 80, 'grammar': 85, 'keywords': 90, 'readability': 80, 'ats': 85}
            }
        }
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using PyMuPDF"""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text()
            
            doc.close()
            
            # Clean extracted text
            text = re.sub(r'\s+', ' ', text)  # Replace multiple whitespaces
            text = text.strip()
            
            if not text:
                raise ValueError("No text could be extracted from the PDF")
            
            return text
            
        except Exception as e:
            logging.error(f"PDF text extraction error: {e}")
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    
    def analyze_resume(self, file_path: str, heavy_mode: bool = False) -> Dict:
        """Main analysis function"""
        try:
            # Extract text from PDF
            text = self.extract_text_from_pdf(file_path)
            
            # Initialize NLP processor
            nlp_processor = NLPProcessor(heavy_mode=heavy_mode)
            
            # Perform various analyses
            results = {
                'timestamp': datetime.now().isoformat(),
                'heavy_mode': heavy_mode,
                'text_length': len(text),
                'word_count': len(text.split()),
                'original_text': text[:1000] + "..." if len(text) > 1000 else text  # Store first 1000 chars
            }
            
            # 1. Grammar Analysis
            logging.info("Analyzing grammar...")
            grammar_analysis = nlp_processor.analyze_grammar(text)
            results['grammar'] = grammar_analysis
            
            # 2. Readability Analysis
            logging.info("Analyzing readability...")
            readability_analysis = nlp_processor.calculate_readability(text)
            results['readability'] = readability_analysis
            
            # 3. Keyword Analysis
            logging.info("Extracting keywords...")
            keywords = nlp_processor.extract_keywords(text)
            results['keywords'] = {
                'extracted': keywords,
                'count': len(keywords),
                'top_10': keywords[:10]
            }
            
            # 4. Structure Analysis
            logging.info("Analyzing structure...")
            structure_analysis = nlp_processor.analyze_structure(text)
            results['structure'] = structure_analysis
            
            # 5. ATS Compatibility
            logging.info("Analyzing ATS compatibility...")
            ats_analysis = nlp_processor.calculate_ats_compatibility(text)
            results['ats'] = ats_analysis
            
            # 6. Action Verbs Analysis
            logging.info("Analyzing action verbs...")
            action_verbs = nlp_processor.analyze_action_verbs(text)
            results['action_verbs'] = action_verbs
            
            # 7. Entity Extraction
            logging.info("Extracting entities...")
            entities = nlp_processor.extract_entities(text)
            results['entities'] = entities
            
            # 8. Calculate overall scores
            results['scores'] = self._calculate_scores(results)
            
            # 9. Compare with exemplars
            logging.info("Comparing with exemplars...")
            exemplar_comparison = self._compare_with_exemplars(text, results, nlp_processor)
            results['exemplar_comparison'] = exemplar_comparison
            
            # 10. Generate recommendations
            logging.info("Generating recommendations...")
            recommendations = self._generate_recommendations(results)
            results['recommendations'] = recommendations
            
            # 11. Predict job roles
            logging.info("Predicting job roles...")
            job_predictions = self._predict_job_roles(text, results)
            results['job_predictions'] = job_predictions
            
            logging.info("Resume analysis completed successfully")
            return results
            
        except Exception as e:
            logging.error(f"Resume analysis error: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _calculate_scores(self, results: Dict) -> Dict:
        """Calculate individual and composite scores"""
        scores = {}
        
        # Grammar Score (0-100)
        scores['grammar'] = results['grammar']['score']
        
        # Readability Score (0-100)
        scores['readability'] = results['readability']['score']
        
        # Structure/Formatting Score (0-100)
        scores['formatting'] = results['structure']['score']
        
        # ATS Compatibility Score (0-100)
        scores['ats'] = results['ats']['score']
        
        # Keyword Strength Score (0-100)
        keyword_count = results['keywords']['count']
        keyword_score = min(100, keyword_count * 5)  # 5 points per keyword, max 100
        scores['keywords'] = keyword_score
        
        # Calculate composite score (weighted average)
        weights = {
            'grammar': 0.2,
            'readability': 0.15,
            'formatting': 0.25,
            'ats': 0.25,
            'keywords': 0.15
        }
        
        composite_score = sum(scores[category] * weights[category] for category in weights)
        scores['composite'] = round(composite_score, 1)
        
        # Add performance tier
        if scores['composite'] >= 80:
            scores['tier'] = 'Excellent'
            scores['tier_color'] = '#22C55E'
        elif scores['composite'] >= 70:
            scores['tier'] = 'Good'
            scores['tier_color'] = '#3B82F6'
        elif scores['composite'] >= 60:
            scores['tier'] = 'Average'
            scores['tier_color'] = '#F59E0B'
        else:
            scores['tier'] = 'Needs Improvement'
            scores['tier_color'] = '#EF4444'
        
        return scores
    
    def _compare_with_exemplars(self, text: str, results: Dict, nlp_processor: NLPProcessor) -> Dict:
        """Compare resume with exemplar clusters"""
        if not self.exemplar_clusters:
            return {'error': 'No exemplar clusters available'}
        
        comparison = {}
        
        # Find best matching cluster
        best_match = None
        best_score = 0
        
        text_lower = text.lower()
        user_keywords = [kw[0] for kw in results['keywords']['extracted'][:20]]
        
        for cluster_name, cluster_data in self.exemplar_clusters.items():
            # Calculate keyword overlap
            cluster_keywords = cluster_data.get('keywords', [])
            overlap = len(set(user_keywords) & set(cluster_keywords))
            match_score = overlap / max(len(cluster_keywords), 1) * 100
            
            if match_score > best_score:
                best_score = match_score
                best_match = cluster_name
        
        comparison['best_match'] = best_match
        comparison['match_score'] = best_score
        
        if best_match:
            cluster_data = self.exemplar_clusters[best_match]
            comparison['cluster_info'] = cluster_data
            
            # Compare scores with cluster thresholds
            thresholds = cluster_data.get('score_thresholds', {})
            score_gaps = {}
            
            for category, threshold in thresholds.items():
                user_score = results['scores'].get(category, 0)
                gap = threshold - user_score
                score_gaps[category] = {
                    'user_score': user_score,
                    'threshold': threshold,
                    'gap': gap,
                    'meets_threshold': gap <= 0
                }
            
            comparison['score_gaps'] = score_gaps
            
            # Identify missing skills
            cluster_skills = set(cluster_data.get('skills', []))
            user_text_lower = text_lower
            found_skills = [skill for skill in cluster_skills if skill in user_text_lower]
            missing_skills = list(cluster_skills - set(found_skills))
            
            comparison['missing_skills'] = missing_skills
            comparison['found_skills'] = found_skills
        
        return comparison
    
    def _generate_recommendations(self, results: Dict) -> List[Dict]:
        """Generate actionable improvement recommendations"""
        recommendations = []
        scores = results['scores']
        
        # Grammar recommendations
        if scores['grammar'] < 85:
            recommendations.append({
                'category': 'Grammar',
                'priority': 'High',
                'issue': f"Grammar score is {scores['grammar']}/100",
                'recommendation': "Review and fix grammar errors. Consider using tools like Grammarly.",
                'impact': 'High - Grammar errors create negative first impressions'
            })
        
        # Formatting recommendations
        if scores['formatting'] < 75:
            recommendations.append({
                'category': 'Formatting',
                'priority': 'High',
                'issue': f"Structure score is {scores['formatting']}/100",
                'recommendation': "Ensure your resume includes essential sections: Contact, Summary, Experience, Education, Skills.",
                'impact': 'High - Poor structure makes resume hard to scan'
            })
        
        # Keyword recommendations
        if scores['keywords'] < 70:
            recommendations.append({
                'category': 'Keywords',
                'priority': 'Medium',
                'issue': f"Keyword strength is {scores['keywords']}/100",
                'recommendation': "Include more industry-specific keywords and technical skills relevant to your target role.",
                'impact': 'Medium - Keywords help with ATS filtering and relevance'
            })
        
        # ATS recommendations
        if scores['ats'] < 80:
            ats_issues = results['ats'].get('issues', [])
            for issue in ats_issues:
                recommendations.append({
                    'category': 'ATS Compatibility',
                    'priority': 'Medium',
                    'issue': issue,
                    'recommendation': "Address ATS compatibility issues to ensure your resume passes automated screening.",
                    'impact': 'Medium - ATS compatibility affects initial screening'
                })
        
        # Readability recommendations
        if scores['readability'] < 70:
            recommendations.append({
                'category': 'Readability',
                'priority': 'Low',
                'issue': f"Readability score is {scores['readability']}/100",
                'recommendation': "Use shorter sentences and simpler language to improve readability.",
                'impact': 'Low - Better readability improves user experience'
            })
        
        # Action verbs recommendations
        action_verb_score = results.get('action_verbs', {}).get('score', 50)
        if action_verb_score < 60:
            recommendations.append({
                'category': 'Content Quality',
                'priority': 'Medium',
                'issue': "Limited use of action verbs",
                'recommendation': "Start bullet points with strong action verbs (achieved, developed, led, etc.).",
                'impact': 'Medium - Action verbs make accomplishments more impactful'
            })
        
        # Sort by priority
        priority_order = {'High': 3, 'Medium': 2, 'Low': 1}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 0), reverse=True)
        
        return recommendations
    
    def _predict_job_roles(self, text: str, results: Dict) -> List[Dict]:
        """Predict suitable job roles based on resume content"""
        predictions = []
        
        # Define role patterns and keywords
        role_patterns = {
            'Software Engineer': {
                'keywords': ['python', 'java', 'javascript', 'programming', 'software', 'development', 'code'],
                'weight': 1.0
            },
            'Data Scientist': {
                'keywords': ['python', 'r', 'machine learning', 'data analysis', 'statistics', 'sql'],
                'weight': 0.9
            },
            'Product Manager': {
                'keywords': ['product', 'management', 'strategy', 'roadmap', 'stakeholder', 'agile'],
                'weight': 0.8
            },
            'Marketing Specialist': {
                'keywords': ['marketing', 'digital', 'social media', 'campaigns', 'analytics', 'content'],
                'weight': 0.7
            },
            'Business Analyst': {
                'keywords': ['analysis', 'business', 'requirements', 'process', 'stakeholder', 'documentation'],
                'weight': 0.8
            },
            'Project Manager': {
                'keywords': ['project', 'management', 'agile', 'scrum', 'timeline', 'coordination'],
                'weight': 0.7
            }
        }
        
        text_lower = text.lower()
        user_keywords = [kw[0] for kw in results['keywords']['extracted']]
        
        for role, role_data in role_patterns.items():
            # Calculate match score
            role_keywords = role_data['keywords']
            matches = sum(1 for keyword in role_keywords if keyword in text_lower)
            match_score = (matches / len(role_keywords)) * 100 * role_data['weight']
            
            if match_score > 20:  # Only include roles with >20% match
                predictions.append({
                    'role': role,
                    'match_score': round(match_score, 1),
                    'matched_keywords': [kw for kw in role_keywords if kw in text_lower],
                    'confidence': 'High' if match_score > 60 else 'Medium' if match_score > 40 else 'Low'
                })
        
        # Sort by match score
        predictions.sort(key=lambda x: x['match_score'], reverse=True)
        
        return predictions[:5]  # Return top 5 predictions
    
    def get_chart_data(self, results: Dict, chart_type: str) -> Dict:
        """Generate data for various chart types"""
        try:
            if chart_type == 'scores_radar':
                return {
                    'labels': ['Grammar', 'Readability', 'Formatting', 'ATS', 'Keywords'],
                    'data': [
                        results['scores']['grammar'],
                        results['scores']['readability'],
                        results['scores']['formatting'],
                        results['scores']['ats'],
                        results['scores']['keywords']
                    ]
                }
            
            elif chart_type == 'keyword_frequency':
                keywords = results['keywords']['top_10']
                return {
                    'labels': [kw[0] for kw in keywords],
                    'data': [kw[1] for kw in keywords]
                }
            
            elif chart_type == 'section_coverage':
                sections = results['structure']['sections']
                return {
                    'labels': list(sections.keys()),
                    'data': [1 if count > 0 else 0 for count in sections.values()]
                }
            
            elif chart_type == 'job_predictions':
                predictions = results.get('job_predictions', [])
                return {
                    'labels': [pred['role'] for pred in predictions],
                    'data': [pred['match_score'] for pred in predictions]
                }
            
            elif chart_type == 'improvement_priority':
                recommendations = results.get('recommendations', [])
                priority_counts = {'High': 0, 'Medium': 0, 'Low': 0}
                for rec in recommendations:
                    priority_counts[rec['priority']] += 1
                
                return {
                    'labels': list(priority_counts.keys()),
                    'data': list(priority_counts.values())
                }
            
            else:
                return {'error': 'Unknown chart type'}
                
        except Exception as e:
            logging.error(f"Chart data generation error: {e}")
            return {'error': str(e)}
