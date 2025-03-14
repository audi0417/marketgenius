#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Brand analyzer module for processing and extracting brand voice characteristics.
"""

import re
import nltk
import numpy as np
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from marketgenius.utils.logger import get_logger

logger = get_logger(__name__)

# Ensure NLTK resources are available
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')


class BrandAnalyzer:
    """Analyzes brand content to extract voice characteristics."""
    
    def __init__(self):
        """Initialize the brand analyzer."""
        self.stopwords = set(nltk.corpus.stopwords.words('english'))
        self.tfidf = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 3)
        )
        
    def preprocess_text(self, text):
        """Preprocess text for analysis."""
        # Convert to lowercase
        text = text.lower()
        # Remove URLs
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        # Remove punctuation
        text = re.sub(r'[^\w\s]', '', text)
        # Remove numbers
        text = re.sub(r'\d+', '', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_key_phrases(self, texts, top_n=20):
        """Extract key phrases from a collection of texts."""
        if not texts:
            logger.warning("No texts provided for key phrase extraction")
            return []
            
        # Preprocess texts
        processed_texts = [self.preprocess_text(text) for text in texts]
        
        # Extract TF-IDF features
        try:
            tfidf_matrix = self.tfidf.fit_transform(processed_texts)
            feature_names = self.tfidf.get_feature_names_out()
            
            # Sum TF-IDF scores across all documents
            tfidf_sum = np.sum(tfidf_matrix.toarray(), axis=0)
            
            # Get top phrases
            top_indices = tfidf_sum.argsort()[-top_n:][::-1]
            top_phrases = [feature_names[i] for i in top_indices]
            
            logger.info(f"Extracted {len(top_phrases)} key phrases from content")
            return top_phrases
            
        except Exception as e:
            logger.error(f"Error extracting key phrases: {e}")
            return []
    
    def analyze_tone(self, texts):
        """Analyze the tone of the brand's content."""
        # Simple wordlists for tone analysis - would use more sophisticated NLP in production
        formal_words = set(['therefore', 'consequently', 'furthermore', 'moreover', 'thus', 'hence'])
        casual_words = set(['awesome', 'cool', 'yeah', 'amazing', 'wow', 'super'])
        technical_words = set(['algorithm', 'interface', 'system', 'process', 'module', 'functionality'])
        emotional_words = set(['love', 'hate', 'excited', 'thrilled', 'sad', 'happy', 'passionate'])
        
        formal_count = 0
        casual_count = 0
        technical_count = 0
        emotional_count = 0
        total_words = 0
        
        for text in texts:
            text = self.preprocess_text(text)
            words = nltk.word_tokenize(text)
            words = [word for word in words if word not in self.stopwords]
            
            formal_count += sum(1 for word in words if word in formal_words)
            casual_count += sum(1 for word in words if word in casual_words)
            technical_count += sum(1 for word in words if word in technical_words)
            emotional_count += sum(1 for word in words if word in emotional_words)
            total_words += len(words)
        
        # Avoid division by zero
        if total_words == 0:
            return {
                "formal": 0,
                "casual": 0,
                "technical": 0,
                "emotional": 0
            }
            
        tone_analysis = {
            "formal": formal_count / total_words,
            "casual": casual_count / total_words,
            "technical": technical_count / total_words,
            "emotional": emotional_count / total_words
        }
        
        logger.info(f"Tone analysis completed: {tone_analysis}")
        return tone_analysis
    
    def analyze_brand_voice(self, content_items):
        """
        Analyze the brand voice from a collection of content items.
        
        Args:
            content_items: List of text content representing the brand's voice
            
        Returns:
            A dictionary with brand voice characteristics
        """
        if not content_items:
            logger.warning("No content provided for brand voice analysis")
            return {
                "key_phrases": [],
                "tone": {},
                "average_sentence_length": 0,
                "vocabulary_richness": 0
            }
            
        # Extract texts from content items
        texts = [item for item in content_items if isinstance(item, str)]
        
        # Extract key phrases
        key_phrases = self.extract_key_phrases(texts)
        
        # Analyze tone
        tone = self.analyze_tone(texts)
        
        # Analyze sentence structure
        sentence_lengths = []
        all_words = []
        
        for text in texts:
            sentences = nltk.sent_tokenize(text)
            for sentence in sentences:
                words = nltk.word_tokenize(sentence)
                words = [word for word in words if word.isalpha()]
                sentence_lengths.append(len(words))
                all_words.extend(words)
        
        average_sentence_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
        
        # Calculate vocabulary richness (type-token ratio)
        unique_words = set(all_words)
        vocabulary_richness = len(unique_words) / len(all_words) if all_words else 0
        
        brand_voice = {
            "key_phrases": key_phrases,
            "tone": tone,
            "average_sentence_length": average_sentence_length,
            "vocabulary_richness": vocabulary_richness
        }
        
        logger.info(f"Brand voice analysis completed")
        return brand_voice