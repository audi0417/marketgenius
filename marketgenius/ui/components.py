#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UI components for the MarketGenius Gradio interface.
"""

import os
import gradio as gr
import numpy as np
from marketgenius.utils.logger import get_logger

logger = get_logger(__name__)


def create_brand_tab(brand_model, state):
    """
    Create the brand management tab.
    
    Args:
        brand_model: BrandLanguageModel instance
        state: Application state dictionary
    """
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 品牌聲音分析")
            
            brand_name = gr.Textbox(label="品牌名稱")
            
            brand_content = gr.Textbox(
                label="品牌內容範例 (多個範例請用三個連字符號 --- 分隔)",
                placeholder="粘貼貴公司既有的市場內容，如社群媒體帖子、品牌描述、行銷文案等...",
                lines=10
            )
            
            analyze_button = gr.Button("分析品牌聲音")
            
            brand_voice_output = gr.JSON(label="品牌聲音分析結果")
            
            @analyze_button.click(inputs=[brand_name, brand_content], outputs=[brand_voice_output])
            def analyze_brand_voice(name, content):
                if not name or not content:
                    return {"error": "品牌名稱和內容不能為空"}
                
                # Split content by triple dash separator
                content_items = [item.strip() for item in content.split("---") if item.strip()]
                
                if not content_items:
                    return {"error": "請提供有效的內容範例"}
                
                try:
                    # Create or update brand model
                    model = brand_model.create_brand_model(name, content_items)
                    
                    # Update state
                    state["brands"][name] = {"loaded": True}
                    
                    return model["voice_parameters"]
                except Exception as e:
                    logger.error(f"Error analyzing brand voice: {e}")
                    return {"error": f"分析過程中出錯: {str(e)}"}
        
        with gr.Column():
            gr.Markdown("### 品牌管理")
            
            # Dropdown for selecting existing brands
            existing_brands = gr.Dropdown(
                label="選擇現有品牌",
                choices=list(state["brands"].keys()),
                interactive=True
            )
            
            refresh_brands_button = gr.Button("刷新品牌列表")
            
            @refresh_brands_button.click(outputs=[existing_brands])
            def refresh_brands():
                return gr.update(choices=list(state["brands"].keys()))
            
            selected_brand_info = gr.JSON(label="品牌聲音資料")
            
            @existing_brands.change(inputs=[existing_brands], outputs=[selected_brand_info])
            def load_brand_info(brand_name):
                if not brand_name:
                    return {}
                
                model = brand_model.get_brand_model(brand_name)
                if model:
                    return model
                return {"error": "無法載入品牌資料"}


def create_content_tab(content_pipeline, brand_model, state):
    """
    Create the content generation tab.
    
    Args:
        content_pipeline: ContentGenerationPipeline instance
        brand_model: BrandLanguageModel instance
        state: Application state dictionary
    """
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 內容生成")
            
            # Brand selection
            brand_dropdown = gr.Dropdown(
                label="選擇品牌",
                choices=list(state["brands"].keys()),
                interactive=True
            )
            
            refresh_brands_button = gr.Button("刷新品牌列表")
            
            @refresh_brands_button.click(outputs=[brand_dropdown])
            def refresh_brands():
                return gr.update(choices=list(state["brands"].keys()))
            
            # Content type
            content_type = gr.Radio(
                label="內容類型",
                choices=["社群貼文", "圖片輪播", "短影片腳本", "廣告文案"],
                value="社群貼文"
            )
            
            # Platforms
            platforms = gr.CheckboxGroup(
                label="發布平台",
                choices=["Instagram", "Facebook", "LinkedIn", "YouTube"],
                value=["Instagram"]
            )
            
            # Content goal
            content_goal = gr.Radio(
                label="內容目標",
                choices=["提高品牌知名度", "推廣產品/服務", "用戶互動", "教育用戶", "建立權威"],
                value="提高品牌知名度"
            )
            
            # Topic and key messages
            topic = gr.Textbox(label="主題", placeholder="例如: 夏季新品發布")
            key_messages = gr.Textbox(
                label="關鍵訊息",
                placeholder="列出您希望在內容中傳達的關鍵訊息，每行一個",
                lines=3
            )
            
            # Call to action
            call_to_action = gr.Textbox(
                label="行動召喚",
                placeholder="例如: 立即購買、註冊試用、分享留言等"
            )
            
            # Additional requirements
            additional_requirements = gr.Textbox(
                label="其他要求",
                placeholder="其他特殊要求或指示",
                lines=2
            )
            
            # Generate button
            generate_button = gr.Button("生成內容")
    
    with gr.Row():
        with gr.Column():
            # Output area
            output_tabs = gr.Tabs()
            
            with output_tabs:
                for platform in ["Instagram", "Facebook", "LinkedIn", "YouTube"]:
                    with gr.Tab(platform):
                        with gr.Box():
                            gr.Markdown(f"### {platform} 內容")
                            
                            content_text = gr.Textbox(
                                label="文字內容",
                                lines=5,
                                interactive=True
                            )
                            
                            content_image = gr.Image(
                                label="生成圖片",
                                type="pil"
                            )
                            
                            download_button = gr.Button(f"下載 {platform} 內容")
            
            # Function to generate content
            @generate_button.click(
                inputs=[
                    brand_dropdown, content_type, platforms, content_goal,
                    topic, key_messages, call_to_action, additional_requirements
                ],
                outputs=[content_text, content_image]  # This is simplified; in practice you'd output to all platform tabs
            )
            def generate_content(
                brand_name, content_type, platforms, goal,
                topic, key_messages, call_to_action, additional_requirements
            ):
                if not brand_name:
                    return "請選擇品牌", None
                
                if not topic:
                    return "請提供內容主題", None
                
                try:
                    # Prepare business info
                    business_info = {
                        "name": brand_name,
                        "description": "Brand description would go here",  # Would come from a database in a real app
                        "industry": "Generic industry",  # Would come from a database in a real app
                        "target_audience": "Generic audience"  # Would come from a database in a real app
                    }
                    
                    # Prepare content request
                    content_request = {
                        "content_type": content_type,
                        "platforms": platforms,
                        "goal": goal,
                        "topic": topic,
                        "key_messages": key_messages,
                        "call_to_action": call_to_action,
                        "additional_requirements": additional_requirements
                    }
                    
                    # This is a simplified version - in a real app you'd actually call the pipeline
                    # adapted_content = content_pipeline.generate_content(business_info, content_request)
                    
                    # For demo purposes, return dummy content
                    dummy_text = f"這是為 {brand_name} 生成的 {content_type} 內容，主題為 {topic}。\n\n"
                    dummy_text += f"我們想要傳達的關鍵訊息是：{key_messages}\n\n"
                    dummy_text += f"行動召喚：{call_to_action}"
                    
                    # Create a dummy image
                    dummy_image = np.ones((400, 400, 3), dtype=np.uint8) * 200
                    
                    return dummy_text, dummy_image
                    
                except Exception as e:
                    logger.error(f"Error generating content: {e}")
                    return f"生成內容時出錯: {str(e)}", None


def create_analytics_tab(engagement_analyzer, state):
    """
    Create the analytics tab.
    
    Args:
        engagement_analyzer: EngagementAnalyzer instance
        state: Application state dictionary
    """
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 內容效果分析")
            
            # Select content to analyze
            content_dropdown = gr.Dropdown(
                label="選擇內容",
                choices=list(state.get("generated_content", {}).keys()),
                interactive=True
            )
            
            # Engagement metrics
            engagement_metrics = gr.Textbox(
                label="互動數據",
                placeholder="粘貼互動數據或連結到社群媒體帳號",
                lines=5
            )
            
            analyze_button = gr.Button("分析效果")
            
            # Results
            analysis_results = gr.JSON(label="分析結果")
            
            optimization_suggestions = gr.Textbox(
                label="優化建議",
                lines=3,
                interactive=False
            )
            
            @analyze_button.click(
                inputs=[content_dropdown, engagement_metrics],
                outputs=[analysis_results, optimization_suggestions]
            )
            def analyze_engagement(content_id, metrics_data):
                if not content_id:
                    return {"error": "請選擇內容"}, "請選擇內容進行分析"
                
                if not metrics_data:
                    return {"error": "請提供互動數據"}, "請提供互動數據進行分析"
                
                try:
                    # This is a placeholder - in a real app you'd call the engagement analyzer
                    # results = engagement_analyzer.analyze(content_id, metrics_data)
                    
                    # Dummy results for demo
                    dummy_results = {
                        "engagement_rate": 3.5,
                        "likes": 120,
                        "comments": 15,
                        "shares": 8,
                        "reach": 1500,
                        "impressions": 2000,
                        "click_through_rate": 2.1
                    }
                    
                    dummy_suggestions = (
                        "根據分析結果，建議在下次內容中加入更多互動元素，例如問題或投票。"
                        "內容發佈時間可以調整到傍晚6-8點，以獲得更好的觸及率。"
                    )
                    
                    return dummy_results, dummy_suggestions
                    
                except Exception as e:
                    logger.error(f"Error analyzing engagement: {e}")
                    return {"error": f"分析過程中出錯: {str(e)}"}, "分析過程中出錯"


def create_settings_tab(config):
    """
    Create the settings tab.
    
    Args:
        config: Application configuration
    """
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 系統設置")
            
            # API Keys
            openai_api_key = gr.Textbox(
                label="OpenAI API Key",
                placeholder="sk-...",
                type="password",
                value=config.get("api", {}).get("openai_api_key", "")
            )
            
            stability_api_key = gr.Textbox(
                label="Stability AI API Key",
                placeholder="sk-...",
                type="password",
                value=config.get("api", {}).get("stability_api_key", "")
            )
            
            # Model settings
            model_selection = gr.Dropdown(
                label="主要文本模型",
                choices=["gpt-4", "gpt-3.5-turbo", "claude-3-opus", "claude-3-sonnet", "llama-3"],
                value=config.get("models", {}).get("main_model", "gpt-4")
            )
            
            temperature_slider = gr.Slider(
                minimum=0,
                maximum=1,
                step=0.1,
                label="創意度 (Temperature)",
                value=config.get("models", {}).get("temperature", 0.7)
            )
            
            # Save settings button
            save_settings_button = gr.Button("保存設置")
            
            settings_status = gr.Textbox(
                label="狀態",
                interactive=False
            )
            
            @save_settings_button.click(
                inputs=[openai_api_key, stability_api_key, model_selection, temperature_slider],
                outputs=[settings_status]
            )
            def save_settings(openai_key, stability_key, model, temperature):
                try:
                    # In a real app, you'd update the config file here
                    # For demo purposes, just show a success message
                    
                    # Validate API keys
                    if not openai_key:
                        return "OpenAI API Key不能為空"
                    
                    # Update config values
                    config["api"] = config.get("api", {})
                    config["api"]["openai_api_key"] = openai_key
                    config["api"]["stability_api_key"] = stability_key
                    
                    config["models"] = config.get("models", {})
                    config["models"]["main_model"] = model
                    config["models"]["temperature"] = temperature
                    
                    return "設置已成功保存"
                except Exception as e:
                    return f"保存設置時出錯: {str(e)}"