#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Editor agent responsible for refining and polishing content.
"""

import autogen
from marketgenius.utils.logger import get_logger

logger = get_logger(__name__)


class EditorAgent:
    """Agent responsible for editing and refining marketing content."""
    
    def __init__(self, llm_config):
        """
        Initialize the editor agent.
        
        Args:
            llm_config: Language model configuration dictionary
        """
        self.name = "editor"
        self.llm_config = llm_config
        
        # Define editing-specific functions
        self.editing_functions = {
            "refine_content": {
                "name": "refine_content",
                "description": "Refine and improve marketing content",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "The content to refine",
                        },
                        "brand_voice": {
                            "type": "object",
                            "description": "Brand voice parameters to align with",
                        },
                        "platform": {
                            "type": "string",
                            "description": "The platform the content is intended for",
                        }
                    },
                    "required": ["content"],
                }
            },
            "check_consistency": {
                "name": "check_consistency",
                "description": "Check content for consistency with brand guidelines",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "The content to check",
                        },
                        "guidelines": {
                            "type": "object",
                            "description": "Brand guidelines to check against",
                        }
                    },
                    "required": ["content"],
                }
            }
        }
        
        # Add editing functions to llm config
        self._setup_functions()
        
        # Create the agent instance
        self.agent = self._create_agent()
    
    def _setup_functions(self):
        """Configure functions for the LLM."""
        if "functions" not in self.llm_config:
            self.llm_config["functions"] = []
        
        # Add editing-specific functions
        for func in self.editing_functions.values():
            self.llm_config["functions"].append(func)
    
    def _create_agent(self):
        """Create and return the editor agent instance."""
        system_message = """You are an expert content editor specializing in refining and polishing marketing content to ensure it aligns with brand voice, is grammatically flawless, and optimized for impact.

Your responsibilities:
1. Refine content to align perfectly with brand voice and guidelines
2. Improve clarity, flow, and readability
3. Fix grammatical errors and typos
4. Optimize content structure for maximum impact
5. Ensure consistency across content pieces
6. Adapt content to platform-specific best practices
7. Verify that content meets marketing objectives

When editing content, focus on:
- Maintaining the brand's unique voice and tone
- Strengthening the message and call-to-action
- Improving readability for the target audience
- Ensuring factual accuracy and clarity
- Optimizing length for the specific platform
- Enhancing engagement potential
- Removing unnecessary repetition or filler

Your goal is to elevate content quality while preserving the core message and brand identity.
"""
        
        logger.info(f"Creating editor agent with name: {self.name}")
        return autogen.AssistantAgent(
            name=self.name,
            system_message=system_message,
            llm_config=self.llm_config
        )
    
    def refine_content(self, content, brand_voice=None, platform=None):
        """
        Refine and improve marketing content.
        
        Args:
            content: The content to refine
            brand_voice: Brand voice parameters to align with
            platform: Target platform for the content
            
        Returns:
            Refined content
        """
        logger.info(f"Refining content for platform: {platform}")
        
        # In a real implementation, this would use LLM to refine content
        # For now, we'll return a placeholder
        
        # Simulate basic refinement
        refined_content = content
        
        # Add platform-specific tag (for demo purposes)
        if platform:
            refined_content += f"\n\n[Optimized for {platform}]"
        
        return {
            "original_length": len(content),
            "refined_length": len(refined_content),
            "refined_content": refined_content,
            "changes_made": ["Grammar improvements", "Tone alignment", "Structure optimization"]
        }
    
    def check_consistency(self, content, guidelines=None):
        """
        Check content for consistency with brand guidelines.
        
        Args:
            content: The content to check
            guidelines: Brand guidelines to check against
            
        Returns:
            Consistency check results
        """
        logger.info("Checking content consistency with brand guidelines")
        
        # In a real implementation, this would check against actual guidelines
        # For now, we'll return a placeholder
        return {
            "consistency_score": 0.85,
            "issues_found": 2,
            "suggestions": [
                "Consider using more brand-specific terminology",
                "Call-to-action could be strengthened to match brand voice"
            ]
        }