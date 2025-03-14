#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Designer agent responsible for creating visual content and designs.
"""

import autogen
from marketgenius.utils.logger import get_logger

logger = get_logger(__name__)


class DesignerAgent:
    """Agent responsible for creating visual designs and graphics."""
    
    def __init__(self, llm_config):
        """
        Initialize the designer agent.
        
        Args:
            llm_config: Language model configuration dictionary
        """
        self.name = "designer"
        self.llm_config = llm_config
        
        # Define design-specific functions
        self.design_functions = {
            "create_image_prompt": {
                "name": "create_image_prompt",
                "description": "Create a detailed prompt for image generation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "Description of the desired image",
                        },
                        "style": {
                            "type": "string",
                            "description": "Visual style for the image",
                        },
                        "colors": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "List of brand colors to incorporate",
                        }
                    },
                    "required": ["description"],
                }
            },
            "design_layout": {
                "name": "design_layout",
                "description": "Design layout specifications for content",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "platform": {
                            "type": "string",
                            "description": "The platform the design is for",
                        },
                        "content_type": {
                            "type": "string",
                            "description": "Type of content (post, story, carousel, etc.)",
                        },
                        "elements": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "List of content elements to include in the layout",
                        }
                    },
                    "required": ["platform", "content_type"],
                }
            }
        }
        
        # Add design functions to llm config
        self._setup_functions()
        
        # Create the agent instance
        self.agent = self._create_agent()
    
    def _setup_functions(self):
        """Configure functions for the LLM."""
        if "functions" not in self.llm_config:
            self.llm_config["functions"] = []
        
        # Add design-specific functions
        for func in self.design_functions.values():
            self.llm_config["functions"].append(func)
    
    def _create_agent(self):
        """Create and return the designer agent instance."""
        system_message = """You are a visual design specialist focusing on creating compelling visuals for marketing content.

Your responsibilities:
1. Create detailed prompts for image generation that align with brand guidelines
2. Design layouts for different content types and platforms
3. Ensure visual consistency with the brand identity
4. Optimize designs for different platforms and formats
5. Suggest visual enhancements for marketing content
6. Balance aesthetics with message clarity and brand guidelines

When creating image prompts, specify:
- Subject matter and composition details
- Style and mood
- Color palette (with emphasis on brand colors)
- Lighting and atmosphere
- Relevant details to include or exclude
- Text placement considerations

When designing layouts, consider:
- Platform-specific best practices and dimensions
- Content hierarchy and flow
- Balance between text and visual elements
- Brand elements placement
- Call-to-action visibility
- Mobile vs. desktop viewing experience

Your goal is to create visually appealing designs that enhance the marketing message while maintaining brand consistency.
"""
        
        logger.info(f"Creating designer agent with name: {self.name}")
        return autogen.AssistantAgent(
            name=self.name,
            system_message=system_message,
            llm_config=self.llm_config
        )
    
    def create_image_prompt(self, description, style=None, colors=None):
        """
        Create a detailed prompt for image generation.
        
        Args:
            description: Description of the desired image
            style: Visual style for the image
            colors: List of brand colors to incorporate
            
        Returns:
            Detailed image generation prompt
        """
        logger.info(f"Creating image prompt for style: {style}")
        
        # In a real implementation, this would generate an optimized prompt
        # For now, we'll return a placeholder
        color_str = ", ".join(colors) if colors else "brand colors"
        style_str = style if style else "modern professional"
        
        prompt = f"Create an image with the following characteristics: {description}. "
        prompt += f"Use a {style_str} style with {color_str} as the primary color palette. "
        prompt += "Ensure the image is high quality, visually appealing, and suitable for marketing purposes."
        
        return {
            "prompt": prompt,
            "description": description,
            "style": style,
            "colors": colors
        }
    
    def design_layout(self, platform, content_type, elements=None):
        """
        Design layout specifications for content.
        
        Args:
            platform: Target platform (instagram, facebook, etc.)
            content_type: Type of content (post, story, carousel, etc.)
            elements: Content elements to include
            
        Returns:
            Layout design specifications
        """
        logger.info(f"Designing layout for {platform} {content_type}")
        
        elements = elements or ["image", "headline", "body_text", "cta"]
        
        # In a real implementation, this would generate platform-specific layouts
        # For now, we'll return a placeholder with common dimensions
        dimensions = {
            "instagram": {
                "post": "1080x1080px",
                "story": "1080x1920px",
                "carousel": "1080x1080px (multiple slides)"
            },
            "facebook": {
                "post": "1200x630px",
                "story": "1080x1920px",
                "carousel": "1080x1080px (multiple items)"
            },
            "linkedin": {
                "post": "1200x627px",
                "article": "1200x627px (cover)",
                "carousel": "1080x1080px (multiple slides)"
            }
        }
        
        platform_dims = dimensions.get(platform, {"default": "1200x628px"})
        content_dims = platform_dims.get(content_type, platform_dims.get("default", "1200x628px"))
        
        return {
            "platform": platform,
            "content_type": content_type,
            "dimensions": content_dims,
            "elements": elements,
            "element_placement": {elem: "auto" for elem in elements}
        }