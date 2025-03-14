#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Image generator module for creating visual content.
"""

import os
import io
import requests
import base64
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from marketgenius.utils.logger import get_logger

logger = get_logger(__name__)


class ImageGenerator:
    """Generator for creating visual content for marketing."""
    
    def __init__(self, config):
        """
        Initialize the image generator.
        
        Args:
            config: Configuration dictionary for image generation
        """
        self.config = config
        self.api_key = config.get("api_key")
        self.default_model = config.get("model", "stable-diffusion-v1-5")
        self.default_size = config.get("default_size", "1024x1024")
        
        # Cache for storing generated images to avoid redundant API calls
        self.cache = {}
    
    def generate_image(self, prompt, size=None, model=None, brand_colors=None):
        """
        Generate an image based on the provided prompt.
        
        Args:
            prompt: Text description of the image to generate
            size: Size of the image (default from config)
            model: Model to use for generation (default from config)
            brand_colors: List of brand colors to incorporate
            
        Returns:
            PIL Image object or path to saved image
        """
        size = size or self.default_size
        model = model or self.default_model
        
        # Check cache
        cache_key = f"{prompt}_{size}_{model}"
        if cache_key in self.cache:
            logger.info(f"Using cached image for prompt: {prompt[:30]}...")
            return self.cache[cache_key]
        
        # Enhance prompt with brand colors if provided
        enhanced_prompt = self._enhance_prompt_with_brand_colors(prompt, brand_colors)
        
        logger.info(f"Generating image with prompt: {enhanced_prompt[:50]}...")
        
        try:
            # Try multiple image generation methods until one succeeds
            image = None
            
            # Try Stable Diffusion API if configured
            if self.config.get("use_stable_diffusion") and self.api_key:
                image = self._generate_with_stable_diffusion(enhanced_prompt, size, model)
            
            # Fallback to Hugging Face if configured
            if image is None and self.config.get("use_huggingface"):
                image = self._generate_with_huggingface(enhanced_prompt, size)
            
            # Last resort: generate a placeholder image
            if image is None:
                logger.warning("Falling back to placeholder image generation")
                image = self._generate_placeholder(enhanced_prompt, size)
            
            # Cache the result
            self.cache[cache_key] = image
            return image
            
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return self._generate_error_image(str(e), size)
    
    def _enhance_prompt_with_brand_colors(self, prompt, brand_colors):
        """Enhance the image prompt with brand colors."""
        if not brand_colors:
            return prompt
            
        # Convert color names to hex if they're not already
        color_specs = []
        for color in brand_colors:
            if color.startswith('#'):
                color_specs.append(color)
            else:
                color_specs.append(color)
        
        # Add color information to the prompt
        color_text = ", ".join(color_specs)
        enhanced_prompt = f"{prompt}. Use the following brand colors: {color_text}."
        
        return enhanced_prompt
    
    def _generate_with_stable_diffusion(self, prompt, size, model):
        """Generate image using Stable Diffusion API."""
        width, height = self._parse_size(size)
        
        url = "https://api.stability.ai/v1/generation/stable-diffusion-v1-5/text-to-image"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "text_prompts": [{"text": prompt}],
            "cfg_scale": 7,
            "height": height,
            "width": width,
            "samples": 1,
            "steps": 30,
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                image_data = base64.b64decode(data["artifacts"][0]["base64"])
                image = Image.open(io.BytesIO(image_data))
                return image
            else:
                logger.error(f"Stable Diffusion API error: {response.status_code}, {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error with Stable Diffusion: {e}")
            return None
    
    def _generate_with_huggingface(self, prompt, size):
        """Generate image using Hugging Face Inference API."""
        # This would use the Hugging Face Inference API
        # Implement as needed based on your API access
        # For now, return None to indicate this method failed
        logger.warning("Hugging Face image generation not implemented")
        return None
    
    def _generate_placeholder(self, prompt, size):
        """Generate a placeholder image with the prompt text."""
        width, height = self._parse_size(size)
        
        # Create a blank image
        image = Image.new('RGB', (width, height), color=(240, 240, 240))
        draw = ImageDraw.Draw(image)
        
        # Add background pattern
        self._add_background_pattern(image, draw)
        
        # Add text
        self._add_text_to_image(image, draw, prompt)
        
        return image
    
    def _generate_error_image(self, error_message, size):
        """Generate an error image with the error message."""
        width, height = self._parse_size(size)
        
        # Create a blank image
        image = Image.new('RGB', (width, height), color=(255, 200, 200))
        draw = ImageDraw.Draw(image)
        
        # Add error text
        self._add_text_to_image(image, draw, f"Error: {error_message}", fill=(200, 0, 0))
        
        return image
    
    def _add_background_pattern(self, image, draw):
        """Add a background pattern to the image."""
        width, height = image.size
        
        # Draw some random shapes for visual interest
        for _ in range(20):
            x1 = np.random.randint(0, width)
            y1 = np.random.randint(0, height)
            x2 = np.random.randint(0, width)
            y2 = np.random.randint(0, height)
            color = (
                np.random.randint(200, 240),
                np.random.randint(200, 240)
            )
            draw.ellipse([x1, y1, x2, y2], fill=color, outline=None)
    
    def _add_text_to_image(self, image, draw, text, fill=(100, 100, 100)):
        """Add text to the image."""
        width, height = image.size
        
        # Try to load a font, fall back to default if not available
        try:
            font = ImageFont.truetype("Arial.ttf", 20)
        except IOError:
            font = ImageFont.load_default()
        
        # Wrap text to fit the image width
        max_width = int(width * 0.8)
        lines = self._wrap_text(text, font, max_width)
        
        # Calculate text dimensions
        line_height = font.getsize("A")[1] + 5
        text_height = line_height * len(lines)
        
        # Position text in the center of the image
        y_position = (height - text_height) // 2
        
        # Draw each line of text
        for line in lines:
            line_width = font.getsize(line)[0]
            x_position = (width - line_width) // 2
            draw.text((x_position, y_position), line, font=font, fill=fill)
            y_position += line_height
    
    def _wrap_text(self, text, font, max_width):
        """Wrap text to fit within a specified width."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            # Try adding the word to the current line
            test_line = " ".join(current_line + [word])
            line_width = font.getsize(test_line)[0]
            
            if line_width <= max_width:
                current_line.append(word)
            else:
                # Start a new line
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
        
        # Add the last line
        if current_line:
            lines.append(" ".join(current_line))
        
        return lines
    
    def _parse_size(self, size):
        """Parse the size string into width and height."""
        if isinstance(size, str) and "x" in size:
            width, height = map(int, size.split("x"))
        elif isinstance(size, tuple) and len(size) == 2:
            width, height = size
        else:
            width, height = 512, 512  # Default size
            
        return width, height
    
    def add_text_overlay(self, image, text, position="center", color=(255, 255, 255)):
        """
        Add text overlay to an image.
        
        Args:
            image: PIL Image object
            text: Text to add
            position: Position of the text (center, top, bottom)
            color: Text color
            
        Returns:
            PIL Image with text overlay
        """
        # Create a copy of the image to avoid modifying the original
        img_copy = image.copy()
        draw = ImageDraw.Draw(img_copy)
        
        width, height = img_copy.size
        
        # Try to load a font, fall back to default if not available
        try:
            # Try different font sizes based on image size
            font_size = int(min(width, height) / 15)
            font = ImageFont.truetype("Arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()
        
        # Wrap text to fit the image width
        max_width = int(width * 0.8)
        lines = self._wrap_text(text, font, max_width)
        
        # Calculate text dimensions
        line_height = font.getsize("A")[1] + 5
        text_height = line_height * len(lines)
        
        # Determine text position
        if position == "top":
            y_position = 20
        elif position == "bottom":
            y_position = height - text_height - 20
        else:  # center
            y_position = (height - text_height) // 2
        
        # Add a semi-transparent background for text readability
        for line in lines:
            line_width = font.getsize(line)[0]
            x_position = (width - line_width) // 2
            
            # Draw background rectangle
            padding = 10
            draw.rectangle(
                [(x_position - padding, y_position - padding),
                 (x_position + line_width + padding, y_position + line_height)],
                fill=(0, 0, 0, 128)
            )
            
            # Draw text
            draw.text((x_position, y_position), line, font=font, fill=color)
            y_position += line_height
        
        return img_copy