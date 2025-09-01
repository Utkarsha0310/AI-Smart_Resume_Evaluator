import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pickle
import os

class DataProcessor:
    """Process the Kaggle Resume Dataset for exemplar creation"""
    
    def __init__(self):
        self.vectorizer = None
        self.cluster_model = None
        self.scaler = None
    
    def load_dataset(self, csv_path: str) -> Optional[pd.DataFrame]:
        """Load the resume dataset"""
        try:
            df = pd.read_csv(csv_path)
            logging.info(f"Loaded dataset with {len(df)} resumes")
            return df
        except Exception as e:
            logging.error(f"Error loading dataset: {e}")
            return None
    
    def clean_text(self, text: str) -> str:
        """Clean resume text"""
        if pd.isna(text):
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', str(text))
        
        # Remove special characters but keep letters, numbers, and basic punctuation
        text = re.sub(r'[^\w\s.,;:!?()-]', ' ', text)
        
        # Replace multiple whitespaces with single space
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract features from resume text"""
        features_df = df.copy()
        
        # Clean text
        features_df['cleaned_text'] = features_df['Resume_str'].apply(self.clean_text)
        
        # Basic text features
        features_df['word_count'] = features_df['cleaned_text'].apply(lambda x: len(x.split()))
        features_df['char_count'] = features_df['cleaned_text'].apply(len)
        features_df['sentence_count'] = features_df['cleaned_text'].apply(lambda x: len(x.split('.')))
        
        # Average word length
        features_df['avg_word_length'] = features_df['cleaned_text'].apply(
            lambda x: np.mean([len(word) for word in x.split()]) if x.split() else 0
        )
        
        # Check for common sections
        features_df['has_email'] = features_df['cleaned_text'].apply(
            lambda x: 1 if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', x) else 0
        )
        
        features_df['has_phone'] = features_df['cleaned_text'].apply(
            lambda x: 1 if re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', x) else 0
        )
        
        # Education indicators
        education_keywords = ['education', 'degree', 'university', 'college', 'bachelor', 'master', 'phd']
        features_df['education_mentions'] = features_df['cleaned_text'].apply(
            lambda x: sum(1 for keyword in education_keywords if keyword.lower() in x.lower())
        )
        
        # Experience indicators
        experience_keywords = ['experience', 'work', 'job', 'position', 'role', 'company']
        features_df['experience_mentions'] = features_df['cleaned_text'].apply(
            lambda x: sum(1 for keyword in experience_keywords if keyword.lower() in x.lower())
        )
        
        # Skills indicators
        skills_keywords = ['skills', 'technical', 'programming', 'software', 'tools', 'technologies']
        features_df['skills_mentions'] = features_df['cleaned_text'].apply(
            lambda x: sum(1 for keyword in skills_keywords if keyword.lower() in x.lower())
        )
        
        return features_df
    
    def create_tfidf_features(self, texts: List[str], max_features: int = 1000) -> np.ndarray:
        """Create TF-IDF features from text"""
        try:
            self.vectorizer = TfidfVectorizer(
                max_features=max_features,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.8
            )
            
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            return tfidf_matrix.toarray()
            
        except Exception as e:
            logging.error(f"TF-IDF feature creation error: {e}")
            return np.array([])
    
    def cluster_resumes(self, features: np.ndarray, n_clusters: int = 5) -> np.ndarray:
        """Cluster resumes based on features"""
        try:
            # Standardize features
            self.scaler = StandardScaler()
            scaled_features = self.scaler.fit_transform(features)
            
            # Perform clustering
            self.cluster_model = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
            clusters = self.cluster_model.fit_predict(scaled_features)
            
            return clusters
            
        except Exception as e:
            logging.error(f"Clustering error: {e}")
            return np.array([])
    
    def analyze_clusters(self, df: pd.DataFrame, clusters: np.ndarray) -> Dict:
        """Analyze cluster characteristics"""
        cluster_analysis = {}
        
        for cluster_id in np.unique(clusters):
            cluster_mask = clusters == cluster_id
            cluster_resumes = df[cluster_mask]
            
            # Get category distribution
            if 'Category' in cluster_resumes.columns:
                category_dist = cluster_resumes['Category'].value_counts().to_dict()
                mode_values = cluster_resumes['Category'].mode()
                dominant_category = mode_values.iloc[0] if len(mode_values) > 0 else 'Unknown'
            else:
                category_dist = {}
                dominant_category = f'Cluster_{cluster_id}'
            
            # Extract common keywords
            cluster_texts = cluster_resumes['cleaned_text'].tolist()
            all_text = ' '.join(cluster_texts).lower()
            
            # Simple keyword extraction
            words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text)
            word_freq = {}
            for word in words:
                if word not in ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use']:
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Get top keywords
            top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:15]
            
            # Calculate average features
            avg_word_count = cluster_resumes['word_count'].mean() if 'word_count' in cluster_resumes.columns else 0
            avg_education = cluster_resumes['education_mentions'].mean() if 'education_mentions' in cluster_resumes.columns else 0
            avg_experience = cluster_resumes['experience_mentions'].mean() if 'experience_mentions' in cluster_resumes.columns else 0
            avg_skills = cluster_resumes['skills_mentions'].mean() if 'skills_mentions' in cluster_resumes.columns else 0
            
            # Define score thresholds based on cluster characteristics
            if avg_word_count > 500:
                formatting_threshold = 85
            elif avg_word_count > 300:
                formatting_threshold = 80
            else:
                formatting_threshold = 75
            
            grammar_threshold = 85 + min(10, len(top_keywords) * 0.5)
            keyword_threshold = 80 + min(15, len(top_keywords) * 0.7)
            ats_threshold = 80 + (5 if cluster_resumes['has_email'].mean() > 0.8 else 0)
            readability_threshold = 80
            
            cluster_analysis[dominant_category.lower().replace(' ', '_')] = {
                'size': len(cluster_resumes),
                'category_distribution': category_dist,
                'keywords': [kw[0] for kw in top_keywords],
                'skills': self._extract_skills(top_keywords),
                'avg_word_count': avg_word_count,
                'avg_education_mentions': avg_education,
                'avg_experience_mentions': avg_experience,
                'avg_skills_mentions': avg_skills,
                'score_thresholds': {
                    'formatting': formatting_threshold,
                    'grammar': grammar_threshold,
                    'keywords': keyword_threshold,
                    'readability': readability_threshold,
                    'ats': ats_threshold
                }
            }
        
        return cluster_analysis
    
    def _extract_skills(self, top_keywords: List[Tuple[str, int]]) -> List[str]:
        """Extract skills from top keywords"""
        skill_patterns = [
            'python', 'java', 'javascript', 'sql', 'programming', 'software', 'development',
            'management', 'leadership', 'analysis', 'marketing', 'design', 'engineering',
            'project', 'business', 'communication', 'problem', 'team', 'technical'
        ]
        
        skills = []
        for keyword, freq in top_keywords:
            if any(pattern in keyword.lower() for pattern in skill_patterns):
                skills.append(keyword)
        
        return skills[:10]  # Return top 10 skills
    
    def process_dataset(self, csv_path: str) -> Dict:
        """Main processing function"""
        try:
            # Load dataset
            df = self.load_dataset(csv_path)
            if df is None:
                return {}
            
            # Sample dataset if too large (for performance)
            if len(df) > 5000:
                df = df.sample(n=5000, random_state=42)
                logging.info("Sampled 5000 resumes for processing")
            
            # Extract features
            df = self.extract_features(df)
            
            # Create TF-IDF features
            tfidf_features = self.create_tfidf_features(df['cleaned_text'].tolist())
            
            if tfidf_features.size == 0:
                logging.error("Failed to create TF-IDF features")
                return {}
            
            # Combine with numerical features
            numerical_features = df[['word_count', 'char_count', 'sentence_count', 
                                   'avg_word_length', 'has_email', 'has_phone',
                                   'education_mentions', 'experience_mentions', 
                                   'skills_mentions']].values
            
            # Combine features
            all_features = np.hstack([tfidf_features, numerical_features])
            
            # Cluster resumes
            clusters = self.cluster_resumes(all_features, n_clusters=5)
            
            if clusters.size == 0:
                logging.error("Failed to cluster resumes")
                return {}
            
            # Add cluster labels to dataframe
            df['cluster'] = clusters
            
            # Analyze clusters
            cluster_analysis = self.analyze_clusters(df, clusters)
            
            logging.info(f"Created {len(cluster_analysis)} exemplar clusters")
            return cluster_analysis
            
        except Exception as e:
            logging.error(f"Dataset processing error: {e}")
            return {}
