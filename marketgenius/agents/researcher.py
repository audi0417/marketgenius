#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Researcher agent responsible for gathering information and market research data.
"""

import autogen
from marketgenius.utils.logger import get_logger

logger = get_logger(__name__)


class ResearcherAgent:
    """Agent responsible for researching topics and gathering information."""
    
    def __init__(self, llm_config):
        """
        Initialize the researcher agent.
        
        Args:
            llm_config: Language model configuration dictionary
        """
        self.name = "researcher"
        self.llm_config = llm_config
        
        # Define research-specific functions
        self.research_functions = {
            "search_topic": {
                "name": "search_topic",
                "description": "Search for information about a specific topic",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "The topic to research",
                        },
                        "depth": {
                            "type": "string", 
                            "enum": ["basic", "detailed", "comprehensive"],
                            "description": "How deep the research should go",
                        }
                    },
                    "required": ["topic"],
                }
            },
            "analyze_trends": {
                "name": "analyze_trends",
                "description": "Analyze current trends related to a specific domain",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "domain": {
                            "type": "string",
                            "description": "The domain to analyze trends for",
                        },
                        "time_period": {
                            "type": "string",
                            "description": "The time period to analyze trends for (e.g., '30d', '3m', '1y')",
                        }
                    },
                    "required": ["domain"],
                }
            }
        }
        
        # Add research functions to llm config
        self._setup_functions()
        
        # Create the agent instance
        self.agent = self._create_agent()
    
    def _setup_functions(self):
        """Configure functions for the LLM."""
        if "functions" not in self.llm_config:
            self.llm_config["functions"] = []
        
        # Add research-specific functions
        for func in self.research_functions.values():
            self.llm_config["functions"].append(func)
    
    def _create_agent(self):
        """Create and return the researcher agent instance."""
        system_message = """You are a research specialist focusing on gathering accurate, relevant, and comprehensive information for marketing content creation.

Your responsibilities:
1. Research topics thoroughly before providing information
2. Find relevant facts, statistics, and trends related to the topic
3. Identify audience pain points and interests
4. Gather competitor information and market positioning
5. Provide research in a structured, easy-to-use format
6. Always cite sources when providing factual information
7. Identify trending hashtags and keywords related to the topic

When asked to research a topic, provide:
- Key facts and statistics with their sources
- Current trends and insights
- Audience interests and pain points
- Competitor approaches
- Relevant keywords and hashtags
- Content opportunities based on research findings

Your goal is to provide the writer and other team members with a solid foundation of information to create compelling, accurate, and relevant marketing content.
"""
        
        logger.info(f"Creating researcher agent with name: {self.name}")
        return autogen.AssistantAgent(
            name=self.name,
            system_message=system_message,
            llm_config=self.llm_config
        )
    
    def search_topic(self, topic, depth="detailed"):
        """
        Search for information about a topic.
        
        Args:
            topic: The topic to research
            depth: How detailed the research should be (basic, detailed, comprehensive)
            
        Returns:
            Research results as a structured dictionary
        """
        logger.info(f"Researching topic: {topic} with depth: {depth}")
        
        # In a real implementation, this would call external APIs or services
        # For now, we'll return a placeholder
        return {
            "topic": topic,
            "depth": depth,
            "status": "completed",
            "message": f"Research on {topic} has been simulated"
        }
    
    def analyze_trends(self, domain, time_period="30d"):
        """
        Analyze current trends in a domain.
        
        Args:
            domain: The domain to analyze trends for
            time_period: Time period for trend analysis
            
        Returns:
            Trend analysis results
        """
        logger.info(f"Analyzing trends for domain: {domain} over period: {time_period}")
        
        # In a real implementation, this would call trend analysis APIs
        # For now, we'll return a placeholder
        return {
            "domain": domain,
            "time_period": time_period,
            "status": "completed",
            "message": f"Trend analysis for {domain} has been simulated"
        }