#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Content generator for creating multi-platform marketing content.
"""

import autogen
from marketgenius.utils.logger import get_logger
from marketgenius.content.text import TextGenerator
from marketgenius.content.image import ImageGenerator
from marketgenius.content.video import VideoGenerator
from marketgenius.content.adapter import PlatformAdapter

logger = get_logger(__name__)


class ContentGenerationPipeline:
    """Pipeline for generating marketing content."""
    
    def __init__(self, agents, brand_model, config):
        """
        Initialize the content generation pipeline.
        
        Args:
            agents: Dictionary of agent instances
            brand_model: Brand language model instance
            config: Configuration dictionary
        """
        self.agents = agents
        self.brand_model = brand_model
        self.config = config
        
        # Initialize content generators
        self.text_generator = TextGenerator(config.get("text_generation", {}))
        self.image_generator = ImageGenerator(config.get("image_generation", {}))
        self.video_generator = VideoGenerator(config.get("video_generation", {}))
        self.platform_adapter = PlatformAdapter()
        
        # Initialize group chat manager
        self._setup_group_chat()
    
    def _setup_group_chat(self):
        """Set up the agent group chat for content generation."""
        logger.info("Setting up agent group chat for content generation")
        
        # Create agent list for the group chat
        agent_list = [
            self.agents["coordinator"],
            self.agents["researcher"],
            self.agents["writer"],
            self.agents["designer"],
            self.agents["editor"],
            self.agents["analyst"]
        ]
        
        # Create the group chat
        self.groupchat = autogen.GroupChat(
            agents=agent_list,
            messages=[],
            max_round=self.config.get("max_rounds", 15)
        )
        
        # Create the group chat manager
        self.manager = autogen.GroupChatManager(
            groupchat=self.groupchat,
            llm_config=self.agents["coordinator"].llm_config
        )
    
    def generate_content(self, business_info, content_request):
        """
        Generate marketing content based on business info and content request.
        
        Args:
            business_info: Dictionary with business information
            content_request: Dictionary specifying content requirements
            
        Returns:
            Dictionary with generated content
        """
        logger.info(f"Generating content for business: {business_info.get('name')}")
        
        # Prepare the initial message for the group chat
        initial_message = self._prepare_content_request(business_info, content_request)
        
        # Start the group chat
        self.agents["coordinator"].initiate_chat(
            self.manager,
            message=initial_message
        )
        
        # Extract results from the group chat
        raw_content = self._extract_results_from_chat()
        
        # Apply platform-specific adaptation
        platforms = content_request.get("platforms", ["instagram"])
        adapted_content = {}
        
        for platform in platforms:
            adapted_content[platform] = self.platform_adapter.adapt_content(
                raw_content, 
                platform, 
                business_info
            )
        
        logger.info(f"Content generation completed for platforms: {platforms}")
        return adapted_content
    
    def _prepare_content_request(self, business_info, content_request):
        """Prepare the content request message for the agents."""
        # Extract brand voice parameters
        brand_voice = self.brand_model.get_brand_voice_parameters(business_info.get("name", ""))
        
        # Build the initial message
        message = f"""
        # Content Generation Request
        
        ## Business Information
        - Name: {business_info.get('name', '')}
        - Description: {business_info.get('description', '')}
        - Industry: {business_info.get('industry', '')}
        - Target audience: {business_info.get('target_audience', '')}
        
        ## Brand Voice Parameters
        {self._format_brand_voice(brand_voice)}
        
        ## Content Request
        - Content type: {content_request.get('content_type', 'post')}
        - Platforms: {', '.join(content_request.get('platforms', ['instagram']))}
        - Goal: {content_request.get('goal', 'engagement')}
        - Topic: {content_request.get('topic', '')}
        - Key messages: {content_request.get('key_messages', '')}
        - Call to action: {content_request.get('call_to_action', '')}
        
        ## Additional Requirements
        {content_request.get('additional_requirements', '')}
        
        Please collaborate to create high-quality marketing content that aligns with the brand voice and meets the specified requirements.
        """
        return message
    
    def _format_brand_voice(self, brand_voice):
        """Format brand voice parameters for the content request."""
        if not brand_voice:
            return "No brand voice parameters available."
            
        formatted = "```\n"
        for key, value in brand_voice.items():
            if isinstance(value, dict):
                formatted += f"{key}:\n"
                for subkey, subvalue in value.items():
                    formatted += f"  - {subkey}: {subvalue}\n"
            elif isinstance(value, list):
                formatted += f"{key}: {', '.join(value)}\n"
            else:
                formatted += f"{key}: {value}\n"
        formatted += "```"
        
        return formatted
    
    def _extract_results_from_chat(self):
        """Extract the generated content from the group chat."""
        # Get the chat history
        chat_history = self.groupchat.messages
        
        # Find the last message from the editor agent
        editor_messages = [
            msg for msg in chat_history 
            if msg.get("role") == "assistant" and 
               msg.get("name") == self.agents["editor"].name
        ]
        
        if not editor_messages:
            logger.warning("No editor messages found in chat history")
            return {"error": "No content generated"}
        
        # Get the last message from the editor
        last_editor_message = editor_messages[-1].get("content", "")
        
        # Parse the content (assuming it's in a structured format)
        try:
            content = self._parse_editor_content(last_editor_message)
            return content
        except Exception as e:
            logger.error(f"Error parsing editor content: {e}")
            return {"error": f"Failed to parse content: {e}", "raw_content": last_editor_message}
    
    def _parse_editor_content(self, message):
        """Parse the content from the editor's message."""
        # Simple parsing logic - would be more sophisticated in production
        lines = message.split("\n")
        content = {}
        
        current_section = None
        section_content = []
        
        for line in lines:
            if line.startswith("## "):
                # Save previous section if it exists
                if current_section:
                    content[current_section] = "\n".join(section_content).strip()
                    section_content = []
                
                # Start new section
                current_section = line[3:].strip().lower().replace(" ", "_")
            elif current_section:
                section_content.append(line)
        
        # Save the last section
        if current_section and section_content:
            content[current_section] = "\n".join(section_content).strip()
        
        return content