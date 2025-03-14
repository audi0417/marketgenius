#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gradio web interface for the MarketGenius application.
"""

import os
import gradio as gr
from marketgenius.utils.logger import get_logger
from marketgenius.ui.components import create_brand_tab, create_content_tab, create_analytics_tab
from marketgenius.brand.modeler import BrandLanguageModel
from marketgenius.content.generator import ContentGenerationPipeline
from marketgenius.agents.agent_factory import AgentFactory
from marketgenius.analytics.metrics import EngagementAnalyzer

logger = get_logger(__name__)


def run_app(config, port=7860, debug=False):
    """
    Run the Gradio web application.
    
    Args:
        config: Application configuration
        port: Port number for the web server
        debug: Enable debug mode
    """
    logger.info("Initializing MarketGenius application")
    
    # Initialize core components
    brand_model = BrandLanguageModel(config.get("brand", {}))
    agent_factory = AgentFactory(config)
    agents = agent_factory.create_all_agents()
    content_pipeline = ContentGenerationPipeline(agents, brand_model, config.get("content", {}))
    engagement_analyzer = EngagementAnalyzer(config.get("analytics", {}))
    
    # Initialize application state
    state = {
        "brands": {},
        "generated_content": {},
        "analytics_data": {}
    }
    
    # Load existing brands if available
    brand_models_dir = config.get("brand", {}).get("models_dir", "models/brands")
    if os.path.exists(brand_models_dir):
        for filename in os.listdir(brand_models_dir):
            if filename.endswith(".json"):
                brand_name = filename[:-5].replace("_", " ").title()
                state["brands"][brand_name] = {"loaded": True}
    
    # Create Gradio interface
    with gr.Blocks(title="MarketGenius") as app:
        gr.Markdown("# MarketGenius")
        gr.Markdown("## AI-Powered Marketing Content Generation System")
        
        with gr.Tabs():
            with gr.Tab("品牌管理"):
                create_brand_tab(brand_model, state)
            
            with gr.Tab("內容生成"):
                create_content_tab(content_pipeline, brand_model, state)
            
            with gr.Tab("效果分析"):
                create_analytics_tab(engagement_analyzer, state)
            
            with gr.Tab("設置"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### 系統設置")
                        gr.Markdown("系統版本: 1.0.0")
                        gr.Markdown("模型: GPT-4, Stable Diffusion v1.5")
                        
                        api_key = gr.Textbox(
                            label="OpenAI API Key",
                            placeholder="sk-...",
                            type="password"
                        )
                        
                        save_button = gr.Button("保存設置")
                        
                        @save_button.click(inputs=[api_key])
                        def save_settings(api_key):
                            if api_key:
                                # Update API key in config
                                # (In a real app, you'd securely store this)
                                return gr.update(value="設置已保存")
                            return gr.update(value="API Key不能為空")
                        
                        status = gr.Textbox(label="狀態", interactive=False)
    
    # Launch the app
    logger.info(f"Starting Gradio server on port {port}")
    app.launch(server_name="0.0.0.0", server_port=port, debug=debug)