#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MarketGenius 基本使用示例。
展示如何使用 MarketGenius 生成簡單的行銷內容。
"""

import os
import asyncio
from marketgenius.data.schemas import BrandModel, ContentType, Platform, ContentTone
from marketgenius.brand.analyzer import BrandAnalyzer
from marketgenius.brand.modeler import BrandLanguageModel
from marketgenius.content.generator import ContentGenerator
from marketgenius.platforms.facebook import facebook_adapter


async def main():
    """演示 MarketGenius 的基本使用。"""
    print("MarketGenius 基本使用示例")
    print("=" * 50)
    
    # 設置 OpenAI API 密鑰（在實際使用中，建議使用環境變量或配置文件）
    os.environ["OPENAI_API_KEY"] = "your-api-key-here"
    
    # 1. 創建一個簡單的品牌模型
    print("\n1. 創建品牌模型")
    print("-" * 30)
    
    # 手動創建品牌模型
    brand_model = BrandModel(
        id="eco-friendly-brand",
        name="綠色生活",
        description="專注於環保和可持續生活方式的品牌",
        industry="生活方式與環保",
        target_audience=["環保愛好者", "25-45歲都市專業人士", "注重健康生活的消費者"],
        keywords=["環保", "可持續", "綠色生活", "零廢棄", "有機", "自然"]
    )
    
    print(f"品牌名稱: {brand_model.name}")
    print(f"行業: {brand_model.industry}")
    print(f"目標受眾: {', '.join(brand_model.target_audience)}")
    print(f"關鍵詞: {', '.join(brand_model.keywords)}")
    
    # 2. 使用 ContentGenerator 生成內容
    print("\n2. 生成社交媒體貼文")
    print("-" * 30)
    
    # 初始化內容生成器
    content_generator = ContentGenerator()
    
    # 生成 Facebook 貼文
    topic = "環保購物袋的 5 個意想不到的用途"
    platform = Platform.FACEBOOK
    tone = ContentTone.EDUCATIONAL
    
    # 非同步生成內容
    result = await content_generator.generate_content(
        topic=topic,
        brand_model=brand_model,
        platform=platform,
        content_type=ContentType.TEXT,
        tone=tone,
        include_hashtags=True,
        include_cta=True  # 包含號召性用語
    )
    
    if result["success"]:
        print(f"為 {platform.value} 平台生成的貼文:")
        print(f"\n{result['content'].text_content.text}\n")
        
        if result["content"].text_content.hashtags:
            print(f"標籤: {', '.join(['#' + tag for tag in result['content'].text_content.hashtags])}")
    else:
        print(f"內容生成失敗: {result.get('error', '未知錯誤')}")
    
    # 3. 使用平台適配器優化內容
    print("\n3. 優化內容以符合平台特性")
    print("-" * 30)
    
    # 使用 Facebook 適配器
    fb_result = facebook_adapter.adapt_content(result["content"])
    
    if fb_result["success"]:
        print("Facebook 優化建議:")
        for i, rec in enumerate(fb_result["metadata"].get("recommendations", []), 1):
            print(f"{i}. {rec}")
    
    # 4. 生成圖像說明
    print("\n4. 生成圖像說明")
    print("-" * 30)
    
    image_description = await content_generator.generate_image_prompt(
        topic=topic,
        brand_model=brand_model,
        platform=platform,
        style="明亮、活潑的風格，展示環保購物袋的創意用途"
    )
    
    if image_description["success"]:
        print("圖像生成提示詞:")
        print(f"\n{image_description['prompt']}\n")
    
    print("\n基本示例完成!")
    print("=" * 50)


if __name__ == "__main__":
    # 執行非同步主函數
    asyncio.run(main())
