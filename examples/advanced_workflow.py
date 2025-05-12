#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MarketGenius 進階工作流程示例。
展示 MarketGenius 的更複雜用例，包括品牌風格分析、
多平台內容生成，以及使用代理系統協作創建行銷活動。
"""

import os
import asyncio
from pathlib import Path
from typing import List, Dict, Any

from marketgenius.data.store import data_store
from marketgenius.data.loader import data_loader
from marketgenius.data.schemas import BrandModel, ContentType, Platform, ContentTone
from marketgenius.brand.analyzer import BrandAnalyzer
from marketgenius.brand.modeler import BrandLanguageModel
from marketgenius.brand.voice_keeper import BrandStyleKeeper
from marketgenius.content.generator import ContentGenerator
from marketgenius.content.text import TextGenerator
from marketgenius.content.image import ImageGenerator
from marketgenius.content.video import VideoGenerator
from marketgenius.platforms.facebook import facebook_adapter
from marketgenius.platforms.instagram import instagram_adapter
from marketgenius.platforms.linkedin import linkedin_adapter
from marketgenius.platforms.youtube import youtube_adapter
from marketgenius.agents.coordinator import CoordinatorAgent


class MarketingCampaignOrchestrator:
    """行銷活動協調器，展示 MarketGenius 進階使用。"""
    
    def __init__(self):
        """初始化協調器。"""
        # 設置 API 密鑰（實際使用中應從安全來源獲取）
        os.environ["OPENAI_API_KEY"] = "your-api-key-here"
        
        # 初始化組件
        self.content_generator = ContentGenerator()
        self.text_generator = TextGenerator()
        self.image_generator = ImageGenerator()
        self.video_generator = VideoGenerator()
        self.brand_analyzer = BrandAnalyzer()
        self.brand_style_keeper = BrandStyleKeeper()
        
        # 平台適配器
        self.adapters = {
            Platform.FACEBOOK: facebook_adapter,
            Platform.INSTAGRAM: instagram_adapter,
            Platform.LINKEDIN: linkedin_adapter,
            Platform.YOUTUBE: youtube_adapter
        }
        
        # 初始化協調代理
        self.coordinator = CoordinatorAgent()
    
    async def analyze_brand_from_samples(self, brand_name: str, samples_dir: str) -> BrandModel:
        """
        從樣本內容分析品牌風格。
        
        Args:
            brand_name: 品牌名稱
            samples_dir: 包含品牌內容樣本的目錄
        
        Returns:
            品牌模型
        """
        print(f"\n分析品牌: {brand_name}")
        print("-" * 30)
        
        # 加載品牌樣本
        samples = []
        samples_path = Path(samples_dir)
        if samples_path.exists() and samples_path.is_dir():
            for file_path in samples_path.glob("*.txt"):
                with open(file_path, "r", encoding="utf-8") as f:
                    samples.append(f.read())
            
            print(f"已加載 {len(samples)} 個品牌內容樣本")
        else:
            # 如果樣本目錄不存在，使用一些模擬樣本
            print(f"樣本目錄 {samples_dir} 不存在，使用模擬樣本")
            samples = [
                f"{brand_name} 致力於為客戶提供最高品質的產品和服務。我們的使命是...",
                f"在 {brand_name}，我們相信創新和品質是成功的關鍵。我們的團隊致力於...",
                f"歡迎了解 {brand_name} 的故事。自成立以來，我們一直堅持..."
            ]
        
        # 分析品牌風格
        brand_attributes = await self.brand_analyzer.analyze_content(samples)
        
        # 創建品牌模型
        brand_model = BrandModel(
            id=brand_name.lower().replace(" ", "-"),
            name=brand_name,
            description=brand_attributes.get("description", f"{brand_name} - 創新企業"),
            industry=brand_attributes.get("industry", "一般企業"),
            target_audience=brand_attributes.get("target_audience", ["一般消費者"]),
            keywords=brand_attributes.get("keywords", [brand_name.lower(), "品質", "服務"])
        )
        
        # 創建品牌語言模型
        brand_language_model = BrandLanguageModel()
        await brand_language_model.train_on_samples(samples, brand_name)
        
        # 設置品牌風格保持器
        self.brand_style_keeper.set_brand_model(brand_model)
        self.brand_style_keeper.set_language_model(brand_language_model)
        
        # 保存品牌模型
        data_store.save_json(brand_model.dict(), f"brands/{brand_model.id}.json")
        
        print(f"品牌分析完成，ID: {brand_model.id}")
        print(f"描述: {brand_model.description}")
        print(f"關鍵詞: {', '.join(brand_model.keywords)}")
        
        return brand_model
    
    async def create_multi_platform_campaign(
        self, 
        brand_model: BrandModel, 
        campaign_name: str,
        main_topic: str,
        platforms: List[Platform]
    ) -> Dict[str, Any]:
        """
        為多個平台創建完整的行銷活動。
        
        Args:
            brand_model: 品牌模型
            campaign_name: 活動名稱
            main_topic: 主要主題
            platforms: 目標平台列表
        
        Returns:
            活動內容
        """
        print(f"\n創建多平台行銷活動: {campaign_name}")
        print(f"主題: {main_topic}")
        print(f"目標平台: {', '.join([p.value for p in platforms])}")
        print("-" * 30)
        
        # 初始化協調代理
        await self.coordinator.initialize(
            brand_model=brand_model,
            campaign_name=campaign_name,
            main_topic=main_topic
        )
        
        # 啟動協作流程
        campaign_plan = await self.coordinator.create_campaign_plan(platforms)
        print("\n活動計劃概要:")
        for platform, plan in campaign_plan.items():
            print(f"- {platform}: {plan['content_types']}")
        
        # 為每個平台生成內容
        campaign_content = {}
        
        for platform in platforms:
            platform_content = {}
            platform_name = platform.value
            
            print(f"\n為 {platform_name} 生成內容...")
            
            # 生成文本內容
            if ContentType.TEXT in campaign_plan[platform_name]["content_types"]:
                text_result = await self.generate_platform_text(
                    brand_model, 
                    main_topic, 
                    platform, 
                    campaign_plan[platform_name]["tone"]
                )
                platform_content["text"] = text_result
                print(f"✓ 已生成文本內容 ({len(text_result['content'].text_content.text)} 字元)")
            
            # 生成圖像內容
            if ContentType.IMAGE in campaign_plan[platform_name]["content_types"]:
                image_result = await self.generate_platform_image(
                    brand_model,
                    main_topic,
                    platform,
                    text_content=platform_content.get("text", {}).get("content", None)
                )
                platform_content["image"] = image_result
                print("✓ 已生成圖像內容")
            
            # 生成影片內容
            if ContentType.VIDEO in campaign_plan[platform_name]["content_types"]:
                video_result = await self.generate_platform_video(
                    brand_model,
                    main_topic,
                    platform,
                    campaign_plan[platform_name]["duration_seconds"]
                )
                platform_content["video"] = video_result
                print(f"✓ 已生成影片內容 (時長: {video_result['content'].video_content.duration_seconds}秒)")
            
            # 使用平台適配器優化內容
            for content_type, content_data in platform_content.items():
                if content_data and content_data.get("content"):
                    adapter_result = self.adapters[platform].adapt_content(content_data["content"])
                    platform_content[content_type]["adapted"] = adapter_result
                    print(f"✓ 已優化 {content_type} 內容，符合 {platform_name} 平台要求")
            
            campaign_content[platform_name] = platform_content
        
        # 保存活動內容
        campaign_data = {
            "name": campaign_name,
            "topic": main_topic,
            "brand": brand_model.id,
            "platforms": [p.value for p in platforms],
            "content": campaign_content
        }
        
        data_store.save_json(campaign_data, f"campaigns/{campaign_name.lower().replace(' ', '_')}.json")
        print(f"\n活動 '{campaign_name}' 已創建並保存")
        
        return campaign_content
    
    async def generate_platform_text(
        self, 
        brand_model: BrandModel, 
        topic: str, 
        platform: Platform,
        tone: ContentTone = None
    ) -> Dict[str, Any]:
        """生成適合特定平台的文本內容。"""
        return await self.content_generator.generate_content(
            topic=topic,
            brand_model=brand_model,
            platform=platform,
            content_type=ContentType.TEXT,
            tone=tone,
            include_hashtags=platform in [Platform.INSTAGRAM, Platform.FACEBOOK],
            include_cta=True,
            brand_style_keeper=self.brand_style_keeper
        )
    
    async def generate_platform_image(
        self,
        brand_model: BrandModel,
        topic: str,
        platform: Platform,
        text_content=None
    ) -> Dict[str, Any]:
        """生成適合特定平台的圖像內容。"""
        # 先生成圖像提示詞
        prompt_result = await self.content_generator.generate_image_prompt(
            topic=topic,
            brand_model=brand_model,
            platform=platform,
            reference_text=text_content.text_content.text if text_content else None
        )
        
        # 使用提示詞生成圖像內容
        return await self.content_generator.generate_content(
            topic=topic,
            brand_model=brand_model,
            platform=platform,
            content_type=ContentType.IMAGE,
            image_prompt=prompt_result["prompt"]
        )
    
    async def generate_platform_video(
        self,
        brand_model: BrandModel,
        topic: str,
        platform: Platform,
        duration_seconds: int = 60
    ) -> Dict[str, Any]:
        """生成適合特定平台的影片內容。"""
        return await self.content_generator.generate_content(
            topic=topic,
            brand_model=brand_model,
            platform=platform,
            content_type=ContentType.VIDEO,
            duration_seconds=duration_seconds
        )


async def main():
    """演示 MarketGenius 的進階工作流程。"""
    print("MarketGenius 進階工作流程示例")
    print("=" * 50)
    
    # 初始化協調器
    orchestrator = MarketingCampaignOrchestrator()
    
    # 1. 分析品牌風格
    brand_model = await orchestrator.analyze_brand_from_samples(
        brand_name="創新科技",
        samples_dir="examples/brand_samples"
    )
    
    # 2. 創建多平台行銷活動
    campaign_content = await orchestrator.create_multi_platform_campaign(
        brand_model=brand_model,
        campaign_name="2025年夏季科技創新活動",
        main_topic="人工智能如何改變生活方式",
        platforms=[Platform.FACEBOOK, Platform.INSTAGRAM, Platform.LINKEDIN]
    )
    
    # 3. 展示部分生成內容
    print("\n生成內容示例:")
    print("-" * 30)
    
    # 展示 Facebook 文本內容
    if "FACEBOOK" in campaign_content and "text" in campaign_content["FACEBOOK"]:
        fb_text = campaign_content["FACEBOOK"]["text"]["content"].text_content.text
        print("\nFacebook 貼文預覽:")
        print(f"\n{fb_text[:200]}...")
    
    # 展示 LinkedIn 文本內容
    if "LINKEDIN" in campaign_content and "text" in campaign_content["LINKEDIN"]:
        li_text = campaign_content["LINKEDIN"]["text"]["content"].text_content.text
        print("\nLinkedIn 貼文預覽:")
        print(f"\n{li_text[:200]}...")
    
    print("\n進階示例完成!")
    print("=" * 50)


if __name__ == "__main__":
    # 執行非同步主函數
    asyncio.run(main())
