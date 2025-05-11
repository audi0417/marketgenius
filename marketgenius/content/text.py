#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MarketGenius 文本生成模組。
負責生成各類文本內容，並按照品牌風格調整。
"""

import os
import re
import random
import logging
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

import openai
from tenacity import retry, stop_after_attempt, wait_random_exponential

from marketgenius.brand.modeler import BrandLanguageModel
from marketgenius.brand.voice_keeper import BrandStyleKeeper
from marketgenius.data.schemas import ContentType, Platform, ContentTone, BrandModel

logger = logging.getLogger(__name__)


class TextGenerator:
    """文本內容生成器。"""
    
    def __init__(self, api_key: Optional[str] = None, 
                 brand_style_keeper: Optional[BrandStyleKeeper] = None):
        """
        初始化文本生成器。
        
        Args:
            api_key: OpenAI API 密鑰（如果未提供，則從環境變量獲取）
            brand_style_keeper: 品牌風格保持器實例
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key
        else:
            logger.warning("未提供 OpenAI API 密鑰，文本生成可能無法正常工作")
        
        self.brand_style_keeper = brand_style_keeper
        self.model = "gpt-4-turbo"  # 默認使用的語言模型
    
    def set_brand_style_keeper(self, keeper: BrandStyleKeeper) -> None:
        """
        設置品牌風格保持器。
        
        Args:
            keeper: 品牌風格保持器實例
        """
        self.brand_style_keeper = keeper
        logger.debug("已設置品牌風格保持器")
    
    def set_model(self, model_name: str) -> None:
        """
        設置使用的語言模型。
        
        Args:
            model_name: 模型名稱（例如 'gpt-4-turbo'）
        """
        self.model = model_name
        logger.debug(f"已設置文本生成模型: {model_name}")
    
    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(3))
    async def generate_text(self, 
                          topic: str, 
                          brand_model: BrandModel,
                          platform: Platform,
                          content_type: ContentType,
                          tone: Optional[ContentTone] = None,
                          target_length: Optional[int] = None,
                          include_hashtags: bool = False,
                          include_emoji: bool = False,
                          include_call_to_action: bool = False,
                          reference_content: Optional[str] = None,
                          additional_instructions: Optional[str] = None) -> Dict[str, Any]:
        """
        生成文本內容。
        
        Args:
            topic: 內容主題
            brand_model: 品牌模型
            platform: 目標平台
            content_type: 內容類型
            tone: 內容語調
            target_length: 目標字數/詞數
            include_hashtags: 是否包含主題標籤
            include_emoji: 是否包含表情符號
            include_call_to_action: 是否包含號召性用語
            reference_content: 參考內容
            additional_instructions: 額外指示
            
        Returns:
            生成的文本內容
        """
        if not self.api_key:
            logger.error("未設置 API 密鑰，無法生成文本內容")
            return {
                "success": False,
                "error": "API 密鑰未設置",
                "text": ""
            }
        
        # 準備提示詞
        system_prompt = self._create_system_prompt(brand_model, platform, content_type)
        user_prompt = self._create_user_prompt(
            topic, 
            brand_model,
            platform, 
            content_type, 
            tone, 
            target_length, 
            include_hashtags, 
            include_emoji, 
            include_call_to_action,
            reference_content,
            additional_instructions
        )
        
        try:
            # 調用 API 生成文本
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1500,
                n=1
            )
            
            # 提取生成的文本
            generated_text = response.choices[0].message.content.strip()
            
            # 使用品牌風格保持器增強一致性（如果可用）
            if self.brand_style_keeper:
                consistency_check = self.brand_style_keeper.check_consistency(
                    generated_text, content_type
                )
                
                # 如果一致性得分較低，嘗試增強
                if consistency_check["consistency_score"] < 0.7:
                    logger.debug(f"品牌風格一致性較低 ({consistency_check['consistency_score']}), 嘗試增強")
                    enhanced_text = self.brand_style_keeper.enhance_consistency(generated_text, content_type)
                    if len(enhanced_text) > 10:  # 確保增強後的文本有效
                        generated_text = enhanced_text
            
            # 提取主題標籤（如果有）
            hashtags = self._extract_hashtags(generated_text) if include_hashtags else []
            
            # 提取表情符號（如果有）
            emoji_count = self._count_emoji(generated_text) if include_emoji else 0
            
            # 提供結果
            result = {
                "success": True,
                "text": generated_text,
                "word_count": len(generated_text.split()),
                "char_count": len(generated_text),
                "hashtags": hashtags,
                "emoji_count": emoji_count,
                "platform": platform.value,
                "content_type": content_type.value,
                "tone": tone.value if tone else None,
                "timestamp": datetime.now().isoformat()
            }
            
            if self.brand_style_keeper:
                result["style_consistency"] = consistency_check["consistency_score"]
                result["style_suggestions"] = consistency_check["suggestions"]
            
            return result
            
        except Exception as e:
            logger.error(f"生成文本時出錯: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": ""
            }
    
    def _create_system_prompt(self, brand_model: BrandModel, platform: Platform, 
                             content_type: ContentType) -> str:
        """
        創建系統提示詞。
        
        Args:
            brand_model: 品牌模型
            platform: 目標平台
            content_type: 內容類型
            
        Returns:
            系統提示詞
        """
        # 品牌說明
        brand_description = f"你是 {brand_model.name} 的內容創作專家。"
        
        if brand_model.description:
            brand_description += f" {brand_model.description}"
        
        if brand_model.industry:
            brand_description += f" 品牌所在行業: {brand_model.industry}。"
        
        # 品牌風格屬性
        style_instructions = "品牌風格特徵:\n"
        if brand_model.style_attributes:
            for attr in brand_model.style_attributes:
                style_instructions += f"- {attr.name}: {attr.value:.1f}/1.0"
                if attr.description:
                    style_instructions += f" ({attr.description})"
                style_instructions += "\n"
        else:
            style_instructions += "- 未指定特定風格屬性，請保持專業、清晰的風格。\n"
        
        # 目標受眾
        audience_info = ""
        if brand_model.target_audience:
            audience_info = f"目標受眾: {', '.join(brand_model.target_audience)}。\n"
        
        # 平台特定指南
        platform_guidelines = self._get_platform_guidelines(platform, content_type)
        
        # 組合系統提示詞
        system_prompt = f"""
{brand_description}

{audience_info}

{style_instructions}

關鍵詞和主題:
{', '.join(brand_model.keywords) if brand_model.keywords else '未提供特定關鍵詞'}

{platform_guidelines}

你的任務是創建與品牌風格一致的{platform.value}平台{content_type.value}內容。確保內容:
1. 準確反映品牌風格和語調
2. 針對{platform.value}平台進行優化
3. 引人入勝並具有高分享價值
4. 專業且無語法或拼寫錯誤
5. 格式正確且易於閱讀
        """
        
        return system_prompt.strip()
    
    def _create_user_prompt(self, 
                           topic: str, 
                           brand_model: BrandModel,
                           platform: Platform, 
                           content_type: ContentType, 
                           tone: Optional[ContentTone] = None,
                           target_length: Optional[int] = None,
                           include_hashtags: bool = False,
                           include_emoji: bool = False,
                           include_call_to_action: bool = False,
                           reference_content: Optional[str] = None,
                           additional_instructions: Optional[str] = None) -> str:
        """
        創建用戶提示詞。
        
        Args:
            [與generate_text相同的參數]
            
        Returns:
            用戶提示詞
        """
        # 基本要求
        user_prompt = f"請為 {brand_model.name} 創建一個關於「{topic}」的{platform.value}內容。"
        
        # 內容類型
        user_prompt += f"\n\n內容類型: {content_type.value}"
        
        # 語調
        if tone:
            user_prompt += f"\n語調: {tone.value}"
        
        # 長度要求
        if target_length:
            user_prompt += f"\n目標長度: 約 {target_length} 字"
        
        # 參考內容
        if reference_content:
            user_prompt += f"\n\n參考材料:\n{reference_content}"
        
        # 特殊要求
        special_requests = []
        
        if include_hashtags:
            special_requests.append("包含 3-5 個相關且流行的主題標籤")
        
        if include_emoji:
            special_requests.append("適當使用表情符號增強訊息傳達")
        
        if include_call_to_action:
            special_requests.append("加入引人點擊、評論或分享的號召性用語")
        
        if special_requests:
            user_prompt += "\n\n特殊要求:\n" + "\n".join(f"- {req}" for req in special_requests)
        
        # 額外指示
        if additional_instructions:
            user_prompt += f"\n\n額外指示:\n{additional_instructions}"
        
        return user_prompt
    
    def _get_platform_guidelines(self, platform: Platform, content_type: ContentType) -> str:
        """
        獲取平台特定的內容指南。
        
        Args:
            platform: 目標平台
            content_type: 內容類型
            
        Returns:
            平台內容指南
        """
        guidelines = f"{platform.value} 平台指南:\n"
        
        if platform == Platform.FACEBOOK:
            guidelines += """
- 文本內容長度應適中，最佳範圍為 40-80 詞
- 使用引人注目的開頭吸引用戶注意
- 可包含 1-2 個相關表情符號增強傳達效果
- 如使用主題標籤，應限制在 2-3 個，並確保相關性
- 提供有價值的內容，鼓勵互動和分享
- 清晰的號召性用語有助提高互動率
            """
        
        elif platform == Platform.INSTAGRAM:
            guidelines += """
- 內容應簡潔有力，避免冗長
- 充分利用視覺敘事元素，文字應支持圖像/視頻
- 主題標籤應置於內容末尾，可使用 5-10 個相關標籤
- 表情符號可適度使用，增加內容活力
- 鼓勵互動的問題或號召性用語能提高參與度
- 考慮使用獨特且一致的風格，如 @品牌名標記
            """
        
        elif platform == Platform.LINKEDIN:
            guidelines += """
- 內容應專業且富有見解，避免過於隨意的表達
- 最佳文章長度為 1300-2000 字，貼文為 150-250 詞
- 段落簡短，易於掃讀
- 限制使用表情符號，保持專業性
- 主題標籤應相關且精確，限制在 3-5 個
- 引用數據或研究結果增加可信度
- 保持對話專業而不生硬
            """
        
        elif platform == Platform.YOUTUBE:
            guidelines += """
- 標題應引人注目，長度控制在 60 字元以內
- 描述前兩行最為重要，應包含關鍵信息和關鍵詞
- 完整描述應包含內容概述、時間戳、相關鏈接和號召性用語
- 標籤應相關且具體，以幫助視頻被發現
- 字幕或腳本應明確、簡潔，避免過多填充詞
- 鼓勵訂閱、點贊和評論的號召性用語放在視頻開頭和結尾
            """
        
        else:
            guidelines += "- 請遵循一般社交媒體最佳實踐，創建簡潔、引人入勝且與平台適配的內容。"
        
        return guidelines
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """
        從文本中提取主題標籤。
        
        Args:
            text: 文本內容
            
        Returns:
            主題標籤列表
        """
        # 使用正則表達式匹配 # 開頭的標籤
        hashtags = re.findall(r'#(\w+)', text)
        return hashtags
    
    def _count_emoji(self, text: str) -> int:
        """
        計算文本中的表情符號數量。
        
        Args:
            text: 文本內容
            
        Returns:
            表情符號數量
        """
        # 簡化實現 - 實際應使用更完整的表情符號檢測庫
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # 表情符號
            "\U0001F300-\U0001F5FF"  # 符號和象形文字
            "\U0001F680-\U0001F6FF"  # 交通和地圖
            "\U0001F700-\U0001F77F"  # 警告符號
            "\U0001F780-\U0001F7FF"  # 幾何符號
            "\U0001F800-\U0001F8FF"  # 補充符號和象形文字
            "\U0001F900-\U0001F9FF"  # 補充符號和象形文字
            "\U0001FA00-\U0001FA6F"  # 擴展符號和象形文字
            "\U0001FA70-\U0001FAFF"  # 擴展符號和象形文字
            "\U00002702-\U000027B0"  # 雜項符號
            "\U000024C2-\U0001F251" 
            "]+"
        )
        return len(emoji_pattern.findall(text))
    
    def generate_social_media_post(self, 
                                 topic: str, 
                                 brand_model: BrandModel,
                                 platform: Platform,
                                 tone: Optional[ContentTone] = None,
                                 reference_content: Optional[str] = None,
                                 include_hashtags: bool = True,
                                 include_emoji: bool = True) -> Dict[str, Any]:
        """
        生成社交媒體貼文。
        
        Args:
            topic: 貼文主題
            brand_model: 品牌模型
            platform: 目標平台
            tone: 內容語調
            reference_content: 參考內容
            include_hashtags: 是否包含主題標籤
            include_emoji: 是否包含表情符號
            
        Returns:
            生成的貼文內容
        """
        # 根據平台設置適當的默認長度
        target_length = None
        if platform == Platform.FACEBOOK:
            target_length = 80
        elif platform == Platform.INSTAGRAM:
            target_length = 150
        elif platform == Platform.LINKEDIN:
            target_length = 200
        
        return self.generate_text(
            topic=topic,
            brand_model=brand_model,
            platform=platform,
            content_type=ContentType.TEXT,
            tone=tone,
            target_length=target_length,
            include_hashtags=include_hashtags,
            include_emoji=include_emoji,
            include_call_to_action=True,
            reference_content=reference_content
        )
    
    def generate_article(self,
                       topic: str,
                       brand_model: BrandModel,
                       tone: Optional[ContentTone] = None,
                       target_length: int = 800,
                       sections: Optional[List[str]] = None,
                       reference_content: Optional[str] = None) -> Dict[str, Any]:
        """
        生成文章或部落格貼文。
        
        Args:
            topic: 文章主題
            brand_model: 品牌模型
            tone: 內容語調
            target_length: 目標字數
            sections: 指定的文章章節（可選）
            reference_content: 參考內容
            
        Returns:
            生成的文章內容
        """
        additional_instructions = ""
        if sections:
            additional_instructions = f"請使用以下章節結構:\n" + "\n".join(f"- {section}" for section in sections)
        
        return self.generate_text(
            topic=topic,
            brand_model=brand_model,
            platform=Platform.LINKEDIN,  # 使用 LinkedIn 作為文章平台
            content_type=ContentType.TEXT,
            tone=tone,
            target_length=target_length,
            include_hashtags=False,
            include_emoji=False,
            include_call_to_action=True,
            reference_content=reference_content,
            additional_instructions=additional_instructions
        )
    
    def generate_product_description(self,
                                   product_name: str,
                                   product_features: List[str],
                                   brand_model: BrandModel,
                                   tone: Optional[ContentTone] = None,
                                   target_length: int = 300) -> Dict[str, Any]:
        """
        生成產品描述。
        
        Args:
            product_name: 產品名稱
            product_features: 產品特性清單
            brand_model: 品牌模型
            tone: 內容語調
            target_length: 目標字數
            
        Returns:
            生成的產品描述
        """
        features_text = "\n".join(f"- {feature}" for feature in product_features)
        reference_content = f"產品名稱: {product_name}\n\n產品特性:\n{features_text}"
        
        additional_instructions = """
請創建一個引人入勝的產品描述，包含:
1. 引人注目的開場白，突出產品解決的問題
2. 清晰描述主要特性和優勢
3. 技術規格（如適用）
4. 使用場景說明
5. 強烈的號召性用語
        """
        
        return self.generate_text(
            topic=f"{product_name} 產品描述",
            brand_model=brand_model,
            platform=Platform.FACEBOOK,  # 使用通用平台
            content_type=ContentType.TEXT,
            tone=tone or ContentTone.PROMOTIONAL,
            target_length=target_length,
            include_hashtags=False,
            include_emoji=False,
            include_call_to_action=True,
            reference_content=reference_content,
            additional_instructions=additional_instructions
        )
    
    def generate_captions(self,
                        image_description: str,
                        brand_model: BrandModel,
                        platform: Platform,
                        tone: Optional[ContentTone] = None,
                        include_hashtags: bool = True) -> Dict[str, Any]:
        """
        生成圖像說明文字。
        
        Args:
            image_description: 圖像描述
            brand_model: 品牌模型
            platform: 目標平台
            tone: 內容語調
            include_hashtags: 是否包含主題標籤
            
        Returns:
            生成的說明文字
        """
        # 根據平台設置適當的默認長度
        target_length = None
        if platform == Platform.INSTAGRAM:
            target_length = 150
        elif platform == Platform.FACEBOOK:
            target_length = 100
        
        additional_instructions = """
請為所描述的圖像創建具有吸引力的說明文字，應該:
1. 生動描述圖像內容
2. 與觀眾建立情感連接
3. 融入品牌風格和信息
4. 鼓勵互動和參與
        """
        
        return self.generate_text(
            topic=f"圖像說明文字",
            brand_model=brand_model,
            platform=platform,
            content_type=ContentType.TEXT,
            tone=tone,
            target_length=target_length,
            include_hashtags=include_hashtags,
            include_emoji=True,
            include_call_to_action=True,
            reference_content=f"圖像描述:\n{image_description}",
            additional_instructions=additional_instructions
        )


# 全局文本生成器實例
text_generator = TextGenerator()
