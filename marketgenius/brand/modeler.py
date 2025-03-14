#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Brand voice modeler for capturing and representing a brand's unique voice.
"""

import os
import json
import numpy as np
from marketgenius.utils.logger import get_logger
from marketgenius.brand.analyzer import BrandAnalyzer

logger = get_logger(__name__)


class BrandLanguageModel:
    """Model for capturing and representing a brand's unique voice."""
    
    def __init__(self, config=None):
        """
        Initialize the brand language model.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.models_dir = self.config.get("models_dir", "models/brands")
        self.analyzer = BrandAnalyzer()
        
        # Ensure models directory exists
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Cache for brand models
        self.brand_models = {}
    
    def create_brand_model(self, brand_name, content_items):
        """
        Create a brand language model from content items.
        
        Args:
            brand_name: Name of the brand
            content_items: List of text content representing the brand's voice
            
        Returns:
            Dictionary with brand voice parameters
        """
        logger.info(f"Creating brand model for: {brand_name}")
        
        # Analyze brand voice
        brand_voice = self.analyzer.analyze_brand_voice(content_items)
        
        # Create the model
        model = {
            "brand_name": brand_name,
            "voice_parameters": brand_voice,
            "content_examples": content_items[:5] if len(content_items) > 5 else content_items
        }
        
        # Save the model
        self._save_brand_model(brand_name, model)
        
        # Cache the model
        self.brand_models[brand_name] = model
        
        logger.info(f"Brand model created for: {brand_name}")
        return model
    
    def update_brand_model(self, brand_name, new_content_items):
        """
        Update an existing brand language model with new content.
        
        Args:
            brand_name: Name of the brand
            new_content_items: New content items to add to the model
            
        Returns:
            Updated brand model
        """
        # Load existing model
        model = self.get_brand_model(brand_name)
        
        if not model:
            logger.warning(f"No existing model found for {brand_name}. Creating new model.")
            return self.create_brand_model(brand_name, new_content_items)
        
        # Get existing content examples
        existing_examples = model.get("content_examples", [])
        
        # Combine existing and new content
        all_content = existing_examples + new_content_items
        
        # Re-analyze brand voice
        brand_voice = self.analyzer.analyze_brand_voice(all_content)
        
        # Update the model
        model["voice_parameters"] = brand_voice
        model["content_examples"] = all_content[:10]  # Keep up to 10 examples
        
        # Save the updated model
        self._save_brand_model(brand_name, model)
        
        # Update cache
        self.brand_models[brand_name] = model
        
        logger.info(f"Brand model updated for: {brand_name}")
        return model
    
    def get_brand_model(self, brand_name):
        """
        Get the brand language model for a specific brand.
        
        Args:
            brand_name: Name of the brand
            
        Returns:
            Brand model dictionary or None if not found
        """
        # Check cache first
        if brand_name in self.brand_models:
            return self.brand_models[brand_name]
        
        # Try to load from file
        model_path = os.path.join(self.models_dir, f"{self._sanitize_filename(brand_name)}.json")
        
        if os.path.exists(model_path):
            try:
                with open(model_path, 'r', encoding='utf-8') as f:
                    model = json.load(f)
                    
                # Cache the model
                self.brand_models[brand_name] = model
                
                logger.info(f"Brand model loaded for: {brand_name}")
                return model
            except Exception as e:
                logger.error(f"Error loading brand model for {brand_name}: {e}")
                return None
        else:
            logger.warning(f"No brand model found for: {brand_name}")
            return None
    
    def get_brand_voice_parameters(self, brand_name):
        """
        Get just the voice parameters for a brand.
        
        Args:
            brand_name: Name of the brand
            
        Returns:
            Brand voice parameters or empty dict if not found
        """
        model = self.get_brand_model(brand_name)
        if model:
            return model.get("voice_parameters", {})
        return {}
    
    def generate_brand_prompt(self, brand_name, base_prompt):
        """
        Generate a prompt that incorporates brand voice parameters.
        
        Args:
            brand_name: Name of the brand
            base_prompt: Base prompt to enhance with brand voice
            
        Returns:
            Enhanced prompt with brand voice instructions
        """
        voice_params = self.get_brand_voice_parameters(brand_name)
        
        if not voice_params:
            return base_prompt
        
        # Extract key parameters
        key_phrases = voice_params.get("key_phrases", [])
        tone = voice_params.get("tone", {})
        avg_sentence_length = voice_params.get("average_sentence_length", 0)
        
        # Determine dominant tone
        dominant_tone = max(tone.items(), key=lambda x: x[1])[0] if tone else None
        
        # Create brand voice instructions
        brand_instructions = "Write in the following brand voice:\n"
        
        if dominant_tone:
            brand_instructions += f"- Use a {dominant_tone} tone\n"
            
        if avg_sentence_length > 0:
            if avg_sentence_length < 10:
                brand_instructions += "- Use short, concise sentences\n"
            elif avg_sentence_length > 20:
                brand_instructions += "- Use longer, more detailed sentences\n"
        
        if key_phrases:
            phrases_to_use = ", ".join(key_phrases[:5])  # Use up to 5 key phrases
            brand_instructions += f"- Try to incorporate these phrases or similar ones: {phrases_to_use}\n"
        
        # Add examples if available
        model = self.get_brand_model(brand_name)
        if model and "content_examples" in model and model["content_examples"]:
            example = model["content_examples"][0]
            brand_instructions += f"\nExample of brand voice:\n\"{example}\"\n"
        
        # Combine with base prompt
        enhanced_prompt = f"{base_prompt}\n\n{brand_instructions}"
        
        return enhanced_prompt
    
    def _save_brand_model(self, brand_name, model):
        """Save a brand model to disk."""
        filename = self._sanitize_filename(brand_name)
        model_path = os.path.join(self.models_dir, f"{filename}.json")
        
        try:
            with open(model_path, 'w', encoding='utf-8') as f:
                json.dump(model, f, indent=2, ensure_ascii=False)
            logger.info(f"Brand model saved to: {model_path}")
        except Exception as e:
            logger.error(f"Error saving brand model: {e}")
    
    @staticmethod
    def _sanitize_filename(filename):
        """Sanitize a string to be used as a filename."""
        # Replace spaces with underscores and remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')
        return filename.replace(' ', '_').lower()