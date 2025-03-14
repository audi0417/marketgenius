#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Coordinator agent responsible for managing the multi-agent workflow.
"""

import autogen
from marketgenius.utils.logger import get_logger

logger = get_logger(__name__)


class CoordinatorAgent:
    """Agent responsible for coordinating the workflow between different agents."""
    
    def __init__(self, llm_config):
        """
        Initialize the coordinator agent.
        
        Args:
            llm_config: Language model configuration dictionary
        """
        self.name = "coordinator"
        self.llm_config = llm_config
        
        # Define coordination-specific functions
        self.coordination_functions = {
            "assign_task": {
                "name": "assign_task",
                "description": "Assign a task to a specific agent",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "agent": {
                            "type": "string",
                            "description": "The agent to assign the task to",
                            "enum": ["researcher", "writer", "designer", "editor", "analyst"],
                        },
                        "task": {
                            "type": "string",
                            "description": "The task to assign",
                        },
                        "priority": {
                            "type": "string",
                            "description": "The priority of the task",
                            "enum": ["low", "medium", "high"],
                        }
                    },
                    "required": ["agent", "task"],
                }
            },
            "track_progress": {
                "name": "track_progress",
                "description": "Track the progress of the content creation workflow",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "workflow_id": {
                            "type": "string",
                            "description": "The ID of the workflow to track",
                        }
                    },
                    "required": ["workflow_id"],
                }
            }
        }
        
        # Add coordination functions to llm config
        self._setup_functions()
        
        # Create the agent instance
        self.agent = self._create_agent()
    
    def _setup_functions(self):
        """Configure functions for the LLM."""
        if "functions" not in self.llm_config:
            self.llm_config["functions"] = []
        
        # Add coordination-specific functions
        for func in self.coordination_functions.values():
            self.llm_config["functions"].append(func)
    
    def _create_agent(self):
        """Create and return the coordinator agent instance."""
        system_message = """You are the coordinator of a multi-agent marketing content creation team. Your role is to manage the workflow and ensure efficient collaboration between different specialized agents.

Your team consists of:
1. Researcher - Gathers information and market data
2. Writer - Creates text content following brand guidelines
3. Designer - Creates visual elements and designs
4. Editor - Reviews and refines content for quality and consistency
5. Analyst - Evaluates content performance and suggests improvements

Your responsibilities:
1. Break down content requests into specific tasks for each agent
2. Coordinate the workflow and handoffs between agents
3. Ensure all requirements are addressed in the final content
4. Maintain brand consistency throughout the process
5. Track progress and handle dependencies between tasks
6. Synthesize the final content from contributions of different agents

When coordinating a content creation request:
1. First, understand the overall requirements and goals
2. Assign initial research to the Researcher agent
3. Direct the Writer to create draft content based on research and brand voice
4. Have the Designer create visual elements that complement the text
5. Ask the Editor to review and refine the complete content package
6. If needed, request the Analyst to evaluate and suggest optimizations
7. Compile the final content and ensure it meets all requirements

Always ensure that the process follows a logical order and dependencies are respected.
"""
        
        logger.info(f"Creating coordinator agent with name: {self.name}")
        return autogen.AssistantAgent(
            name=self.name,
            system_message=system_message,
            llm_config=self.llm_config
        )
    
    def initiate_chat(self, manager, message, clear_history=True):
        """
        Initiate a conversation with the group chat manager.
        
        Args:
            manager: GroupChatManager instance
            message: Initial message to start the conversation
            clear_history: Whether to clear chat history before starting
            
        Returns:
            None
        """
        logger.info("Initiating group chat")
        
        self.agent.initiate_chat(
            manager,
            message=message,
            clear_history=clear_history
        )
    
    def assign_task(self, agent, task, priority="medium"):
        """
        Assign a task to a specific agent.
        
        Args:
            agent: Name of the agent to assign the task to
            task: Description of the task
            priority: Task priority (low, medium, high)
            
        Returns:
            Task assignment status
        """
        logger.info(f"Assigning task to {agent} with priority {priority}")
        
        # In a real implementation, this would communicate with other agents
        # For now, we'll return a placeholder
        return {
            "agent": agent,
            "task": task,
            "priority": priority,
            "status": "assigned",
            "task_id": "task_123"
        }
    
    def track_progress(self, workflow_id):
        """
        Track the progress of a content creation workflow.
        
        Args:
            workflow_id: The ID of the workflow to track
            
        Returns:
            Workflow progress status
        """
        logger.info(f"Tracking progress for workflow: {workflow_id}")
        
        # In a real implementation, this would check actual workflow status
        # For now, we'll return a placeholder
        return {
            "workflow_id": workflow_id,
            "status": "in_progress",
            "complete_tasks": 2,
            "total_tasks": 5,
            "current_agent": "writer"
        }