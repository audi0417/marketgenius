#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Writer agent responsible for creating compelling marketing copy.
"""

import autogen
from marketgenius.utils.logger import get_logger

logger = get_logger(__name__)


class WriterAgent:
    """Agent responsible for creating marketing content text."""
    
    def __init__(self, llm_config):
        """
        Initialize the writer agent.
        
        Args:
            llm_config: Language model configuration dictionary
        """
        self.name = "writer"
        self.llm_config = llm_config
        
        # Define writing-specific functions
        self.writing_functions = {
            "create_content": {
                "name": "create_content",
                "description": "Create marketing content based on research and brand guidelines",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content_type": {
                            "type": "string",
                            "description": "Type of content to create",
                            "enum": ["social_post", "ad_copy", "email", "blog_post", "product_description"],
                        },
                        "brand_voice": {
                            "type": "object",
                            "description": "Brand voice parameters to follow",
                        },
                        "research": {
                            "type": "string",
                            "description": "Research material to base content on",
                        },
                        "target_audience": {
                            "type": "string",
                            "description": "Description of the target audience",
                        },
                        "goal": {
                            "type": "string",
                            "description": "Marketing goal of the content",
                        },
                        "key_messages": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "Key messages to include in the content",
                        },
                        "call_to_action": {
                            "type": "string",
                            "description": "Call to action for the content",
                        },
                        "platform": {
                            "type": "string",
                            "description": "Platform where the content will be published",
                        },
                        "length": {
                            "type": "string",
                            "description": "Desired length of the content",
                            "enum": ["short", "medium", "long"],
                        }
                    },
                    "required": ["content_type", "goal"],
                }
            },
            "generate_variations": {
                "name": "generate_variations",
                "description": "Generate variations of marketing content",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "original_content": {
                            "type": "string",
                            "description": "Original content to create variations of",
                        },
                        "variation_count": {
                            "type": "integer",
                            "description": "Number of variations to generate",
                        },
                        "variation_type": {
                            "type": "string",
                            "description": "Type of variation to generate",
                            "enum": ["tone", "length", "emphasis", "audience"],
                        }
                    },
                    "required": ["original_content", "variation_count"],
                }
            },
            "create_headline_options": {
                "name": "create_headline_options",
                "description": "Generate multiple headline options for content",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "Topic for the headlines",
                        },
                        "count": {
                            "type": "integer",
                            "description": "Number of headline options to generate",
                        },
                        "style": {
                            "type": "string",
                            "description": "Style for the headlines",
                            "enum": ["direct", "question", "how-to", "list", "emotional"],
                        }
                    },
                    "required": ["topic"],
                }
            }
        }
        
        # Add writing functions to llm config
        self._setup_functions()
        
        # Create the agent instance
        self.agent = self._create_agent()
    
    def _setup_functions(self):
        """Configure functions for the LLM."""
        if "functions" not in self.llm_config:
            self.llm_config["functions"] = []
        
        # Add writing-specific functions
        for func in self.writing_functions.values():
            self.llm_config["functions"].append(func)
    
    def _create_agent(self):
        """Create and return the writer agent instance."""
        system_message = """You are an expert marketing copywriter specializing in creating compelling, on-brand content across different platforms and formats.

Your responsibilities:
1. Create persuasive marketing content that aligns with brand voice and guidelines
2. Craft content optimized for specific platforms (Instagram, Facebook, LinkedIn, etc.)
3. Develop content that achieves specific marketing goals (awareness, engagement, conversion)
4. Incorporate key messages and research in a natural, engaging way
5. Generate multiple content variations and headline options
6. Ensure all content has clear, compelling calls to action
7. Adapt writing style to reach different target audiences

When creating content, focus on:
- Capturing the unique voice and personality of the brand
- Writing in a clear, concise, and compelling manner
- Crafting hooks that grab attention immediately
- Structuring content for maximum impact on the specific platform
- Using language that resonates with the target audience
- Creating strong calls to action that drive desired behaviors
- Incorporating SEO and platform-specific best practices

Your goal is to create content that engages the target audience, communicates key messages effectively, and drives desired actions, all while maintaining the brand's unique voice.
"""
        
        logger.info(f"Creating writer agent with name: {self.name}")
        return autogen.AssistantAgent(
            name=self.name,
            system_message=system_message,
            llm_config=self.llm_config
        )
    
    def create_content(self, content_type, goal, brand_voice=None, research=None, 
                       target_audience=None, key_messages=None, call_to_action=None, 
                       platform=None, length="medium"):
        """
        Create marketing content based on research and brand guidelines.
        
        Args:
            content_type: Type of content to create
            goal: Marketing goal of the content
            brand_voice: Brand voice parameters to follow
            research: Research material to base content on
            target_audience: Description of the target audience
            key_messages: Key messages to include in the content
            call_to_action: Call to action for the content
            platform: Platform where the content will be published
            length: Desired length of the content
            
        Returns:
            Generated content
        """
        logger.info(f"Creating {content_type} content for {platform} with goal: {goal}")
        
        # In a real implementation, this would use LLM to generate content
        # For now, we'll return a placeholder
        
        key_msg_str = ", ".join(key_messages) if key_messages else "key brand messages"
        audience_str = target_audience if target_audience else "general audience"
        
        # Create a simple template content based on inputs
        content = f"[{content_type.upper()} for {platform}]\n\n"
        content += f"TARGET: {audience_str}\n"
        content += f"GOAL: {goal}\n\n"
        content += f"This is a placeholder for compelling marketing content about {key_msg_str}.\n\n"
        
        if call_to_action:
            content += f"CALL TO ACTION: {call_to_action}\n"
        
        return {
            "content": content,
            "content_type": content_type,
            "platform": platform,
            "length": length,
            "word_count": len(content.split())
        }
    
    def generate_variations(self, original_content, variation_count=3, variation_type="tone"):
        """
        Generate variations of marketing content.
        
        Args:
            original_content: Original content to create variations of
            variation_count: Number of variations to generate
            variation_type: Type of variation to generate
            
        Returns:
            List of content variations
        """
        logger.info(f"Generating {variation_count} {variation_type} variations")
        
        # In a real implementation, this would use LLM to generate variations
        # For now, we'll return placeholder variations
        
        variations = []
        for i in range(variation_count):
            variation = f"Variation {i+1} ({variation_type}):\n\n"
            variation += original_content
            variation += f"\n\n[This would be a unique {variation_type} variation in production]"
            variations.append(variation)
        
        return {
            "original_content": original_content,
            "variation_type": variation_type,
            "variations": variations
        }
    
    def create_headline_options(self, topic, count=5, style="direct"):
        """
        Generate multiple headline options for content.
        
        Args:
            topic: Topic for the headlines
            count: Number of headline options to generate
            style: Style for the headlines
            
        Returns:
            List of headline options
        """
        logger.info(f"Creating {count} {style} headline options for topic: {topic}")
        
        # In a real implementation, this would use LLM to generate headlines
        # For now, we'll return placeholder headlines based on style
        
        headlines = []
        
        style_templates = {
            "direct": [f"Introducing: {topic}", f"New: {topic} Breakthrough", f"Experience {topic} Today"],
            "question": [f"Are You Ready For {topic}?", f"What If {topic} Could Change Everything?", f"Why {topic} Matters"],
            "how-to": [f"How to Master {topic}", f"5 Ways to Leverage {topic}", f"The Ultimate Guide to {topic}"],
            "list": [f"10 Reasons {topic} Is Essential", f"7 {topic} Secrets Revealed", f"Top 5 {topic} Strategies"],
            "emotional": [f"Transform Your Life With {topic}", f"Never Worry About {topic} Again", f"Fall in Love with {topic}"]
        }
        
        # Get templates for the requested style, or use direct if not found
        templates = style_templates.get(style, style_templates["direct"])
        
        # Use templates first, then generate generic headlines if more are needed
        for i in range(count):
            if i < len(templates):
                headlines.append(templates[i])
            else:
                headlines.append(f"{style.capitalize()} Headline {i+1} for {topic}")
        
        return {
            "topic": topic,
            "style": style,
            "headlines": headlines
        }