#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Agent factory for creating and configuring different agents in the system.
"""

import autogen
from marketgenius.utils.logger import get_logger
from marketgenius.agents.researcher import ResearcherAgent
from marketgenius.agents.writer import WriterAgent
from marketgenius.agents.designer import DesignerAgent
from marketgenius.agents.editor import EditorAgent
from marketgenius.agents.analyst import AnalystAgent
from marketgenius.agents.coordinator import CoordinatorAgent

logger = get_logger(__name__)


class AgentFactory:
    """Factory class for creating and configuring agents."""
    
    def __init__(self, config):
        """Initialize the agent factory with configuration."""
        self.config = config
        self.llm_config = self._prepare_llm_config()
        
    def _prepare_llm_config(self):
        """Prepare the LLM configuration based on the global config."""
        api_config = self.config.get("api", {})
        model_config = self.config.get("models", {})
        
        config_list = [
            {
                "model": model_config.get("main_model", "gpt-4-turbo"),
                "api_key": api_config.get("openai_api_key"),
                "api_type": api_config.get("api_type", "openai"),
            }
        ]
        
        if api_config.get("azure_api_key"):
            config_list.append({
                "model": model_config.get("azure_model", "gpt-4"),
                "api_key": api_config.get("azure_api_key"),
                "base_url": api_config.get("azure_endpoint"),
                "api_type": "azure",
                "api_version": api_config.get("azure_api_version", "2023-07-01-preview"),
            })
            
        return {
            "temperature": model_config.get("temperature", 0.7),
            "seed": model_config.get("seed", None),
            "config_list": config_list,
        }
    
    def create_researcher(self):
        """Create and configure a researcher agent."""
        logger.info("Creating researcher agent")
        return ResearcherAgent(self.llm_config)
    
    def create_writer(self):
        """Create and configure a writer agent."""
        logger.info("Creating writer agent")
        return WriterAgent(self.llm_config)
    
    def create_designer(self):
        """Create and configure a designer agent."""
        logger.info("Creating designer agent")
        return DesignerAgent(self.llm_config)
    
    def create_editor(self):
        """Create and configure an editor agent."""
        logger.info("Creating editor agent")
        return EditorAgent(self.llm_config)
    
    def create_analyst(self):
        """Create and configure an analyst agent."""
        logger.info("Creating analyst agent")
        return AnalystAgent(self.llm_config)
    
    def create_coordinator(self):
        """Create and configure a coordinator agent."""
        logger.info("Creating coordinator agent")
        return CoordinatorAgent(self.llm_config)
    
    def create_all_agents(self):
        """Create and return all agents for the system."""
        logger.info("Creating all agents")
        return {
            "researcher": self.create_researcher(),
            "writer": self.create_writer(),
            "designer": self.create_designer(),
            "editor": self.create_editor(),
            "analyst": self.create_analyst(),
            "coordinator": self.create_coordinator(),
        }