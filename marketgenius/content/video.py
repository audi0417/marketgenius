#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MarketGenius 影片生成模組。
負責創建影片內容或腳本，並按照品牌風格調整。
"""

import os
import re
import json
import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime

import openai
import requests
from tenacity import retry, stop_after_attempt, wait_random_exponential

from marketgenius.brand.voice_keeper import BrandStyleKeeper
from marketgenius.data.schemas import BrandModel, ContentType, Platform, VideoContent
from marketgenius.content.text import TextGenerator

logger = logging.getLogger(__name__)


class VideoGenerator:
    """影片內容生成器。"""
    
    def __init__(self, api_key: Optional[str] = None,
                text_generator: Optional[TextGenerator] = None,
                brand_style_keeper: Optional[BrandStyleKeeper] = None,
                temp_dir: Optional[str] = None):
        """
        初始化影片生成器。
        
        Args:
            api_key: OpenAI API 密鑰（如果未提供，則從環境變量獲取）
            text_generator: 文本生成器實例
            brand_style_keeper: 品牌風格保持器實例
            temp_dir: 臨時文件目錄
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key
        else:
            logger.warning("未提供 OpenAI API 密鑰，影片生成可能無法正常工作")
        
        self.text_generator = text_generator
        self.brand_style_keeper = brand_style_keeper
        self.temp_dir = Path(temp_dir) if temp_dir else Path(tempfile.gettempdir()) / "marketgenius"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        self.model = "gpt-4-turbo"  # 默認使用的語言模型
    
    def set_text_generator(self, generator: TextGenerator) -> None:
        """
        設置文本生成器。
        
        Args:
            generator: 文本生成器實例
        """
        self.text_generator = generator
        logger.debug("已設置文本生成器")
    
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
        logger.debug(f"已設置影片生成模型: {model_name}")
    
    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(3))
    async def generate_video_script(self,
                                  topic: str,
                                  brand_model: BrandModel,
                                  platform: Platform = Platform.YOUTUBE,
                                  duration_seconds: int = 120,
                                  style: Optional[str] = None,
                                  include_b_roll: bool = True,
                                  include_captions: bool = True,
                                  reference_content: Optional[str] = None,
                                  target_audience: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        生成影片腳本。
        
        Args:
            topic: 影片主題
            brand_model: 品牌模型
            platform: 目標平台
            duration_seconds: 影片長度（秒）
            style: 影片風格（例如「教學」、「故事」、「演示」）
            include_b_roll: 是否包含 B-roll 建議
            include_captions: 是否生成字幕
            reference_content: 參考內容
            target_audience: 目標受眾
            
        Returns:
            生成的影片腳本
        """
        if not self.api_key:
            logger.error("未設置 API 密鑰，無法生成影片腳本")
            return {
                "success": False,
                "error": "API 密鑰未設置",
                "script": "",
                "title": ""
            }
        
        # 準備提示詞
        system_prompt = self._create_script_system_prompt(brand_model, platform, style)
        user_prompt = self._create_script_user_prompt(
            topic,
            brand_model,
            platform,
            duration_seconds,
            style,
            include_b_roll,
            include_captions,
            reference_content,
            target_audience
        )
        
        try:
            # 調用 API 生成腳本
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=3000,
                n=1
            )
            
            # 提取生成的腳本
            generated_script = response.choices[0].message.content.strip()
            
            # 使用品牌風格保持器檢查一致性（如果可用）
            style_consistency = None
            style_suggestions = None
            if self.brand_style_keeper:
                consistency_check = self.brand_style_keeper.check_consistency(
                    generated_script, ContentType.VIDEO
                )
                style_consistency = consistency_check["consistency_score"]
                style_suggestions = consistency_check["suggestions"]
            
            # 提取標題和描述
            title, description, script_text = self._extract_script_components(generated_script)
            
            # 提供結果
            result = {
                "success": True,
                "title": title,
                "description": description,
                "script": script_text,
                "duration_seconds": duration_seconds,
                "word_count": len(script_text.split()),
                "platform": platform.value,
                "style": style,
                "timestamp": datetime.now().isoformat()
            }
            
            if style_consistency is not None:
                result["style_consistency"] = style_consistency
                result["style_suggestions"] = style_suggestions
            
            return result
            
        except Exception as e:
            logger.error(f"生成影片腳本時出錯: {e}")
            return {
                "success": False,
                "error": str(e),
                "script": "",
                "title": ""
            }
    
    async def generate_video_description(self,
                                      title: str,
                                      script: str,
                                      brand_model: BrandModel,
                                      platform: Platform = Platform.YOUTUBE,
                                      include_keywords: bool = True,
                                      include_timestamps: bool = True) -> Dict[str, Any]:
        """
        為影片生成描述。
        
        Args:
            title: 影片標題
            script: 影片腳本
            brand_model: 品牌模型
            platform: 目標平台
            include_keywords: 是否包含關鍵詞
            include_timestamps: 是否包含時間戳
            
        Returns:
            生成的影片描述
        """
        if not self.text_generator:
            logger.warning("未設置文本生成器，將使用內部方法生成影片描述")
            return await self._generate_description_internal(
                title, script, brand_model, platform, include_keywords, include_timestamps
            )
        
        # 使用文本生成器生成描述
        topic = f"{title} 影片描述"
        reference_content = f"影片標題: {title}\n\n影片腳本摘要: {script[:500]}..." if len(script) > 500 else script
        
        additional_instructions = f"""
請為該影片創建一個引人入勝的描述，適合 {platform.value} 平台，應該:
1. 簡明扼要地介紹影片內容
2. 包含相關關鍵詞以改善搜索可見度
3. 使用品牌風格和語調
4. 包含引人點擊的號召性用語
"""
        
        if include_timestamps:
            additional_instructions += "\n5. 添加影片主要部分的時間戳"
        
        # 根據平台調整長度
        target_length = 500 if platform == Platform.YOUTUBE else 300
        
        description_result = await self.text_generator.generate_text(
            topic=topic,
            brand_model=brand_model,
            platform=platform,
            content_type=ContentType.TEXT,
            target_length=target_length,
            include_hashtags=platform != Platform.YOUTUBE,
            include_emoji=platform != Platform.YOUTUBE,
            include_call_to_action=True,
            reference_content=reference_content,
            additional_instructions=additional_instructions
        )
        
        if not description_result["success"]:
            logger.warning(f"使用文本生成器生成影片描述失敗: {description_result.get('error')}")
            return await self._generate_description_internal(
                title, script, brand_model, platform, include_keywords, include_timestamps
            )
        
        return {
            "success": True,
            "description": description_result["text"],
            "title": title,
            "platform": platform.value,
            "length": len(description_result["text"]),
            "timestamp": datetime.now().isoformat()
        }
    
    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(3))
    async def _generate_description_internal(self,
                                         title: str,
                                         script: str,
                                         brand_model: BrandModel,
                                         platform: Platform = Platform.YOUTUBE,
                                         include_keywords: bool = True,
                                         include_timestamps: bool = True) -> Dict[str, Any]:
        """
        內部方法: 為影片生成描述。
        
        Args:
            [與 generate_video_description 相同]
            
        Returns:
            生成的影片描述
        """
        if not self.api_key:
            logger.error("未設置 API 密鑰，無法生成影片描述")
            return {
                "success": False,
                "error": "API 密鑰未設置",
                "description": ""
            }
        
        # 準備提示詞
        system_prompt = f"""
你是 {brand_model.name} 的影片描述專家。你需要為 {platform.value} 平台的影片創建引人入勝且優化的描述。

品牌風格:
{"; ".join(f"{attr.name}: {attr.value:.1f}/1.0" for attr in brand_model.style_attributes) if brand_model.style_attributes else "專業、清晰的風格"}

你的描述應該:
1. 簡明扼要地介紹影片內容
2. 包含相關關鍵詞以提高搜索排名
3. 採用品牌一致的風格和語調
4. 包含清晰的號召性用語
5. 符合 {platform.value} 平台的最佳實踐
"""
        
        user_prompt = f"""
請為以下影片創建一個引人入勝的描述:

影片標題: {title}

影片腳本摘要:
{script[:1000]}{'...' if len(script) > 1000 else ''}

要求:
- 平台: {platform.value}
- 包含關鍵詞: {'是' if include_keywords else '否'}
- 包含時間戳: {'是' if include_timestamps else '否'}
- 使用品牌的風格和語調
- 添加引人點擊、訂閱或參與的號召性用語
"""
        
        try:
            # 調用 API 生成描述
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1000,
                n=1
            )
            
            # 提取生成的描述
            description = response.choices[0].message.content.strip()
            
            return {
                "success": True,
                "description": description,
                "title": title,
                "platform": platform.value,
                "length": len(description),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"生成影片描述時出錯: {e}")
            return {
                "success": False,
                "error": str(e),
                "description": ""
            }
    
    async def generate_video_thumbnail_prompt(self,
                                           title: str,
                                           script: str,
                                           brand_model: BrandModel) -> Dict[str, Any]:
        """
        生成影片縮略圖的提示詞。
        
        Args:
            title: 影片標題
            script: 影片腳本
            brand_model: 品牌模型
            
        Returns:
            縮略圖提示詞
        """
        if not self.api_key:
            logger.error("未設置 API 密鑰，無法生成縮略圖提示詞")
            return {
                "success": False,
                "error": "API 密鑰未設置",
                "prompt": ""
            }
        
        # 準備提示詞
        system_prompt = f"""
你是一名專業的影片縮略圖設計專家。你需要創建用於生成吸引人的影片縮略圖的文本提示詞，這些提示詞將用於圖像生成 AI。

品牌風格:
{"; ".join(f"{attr.name}: {attr.value:.1f}/1.0" for attr in brand_model.style_attributes) if brand_model.style_attributes else "專業、吸引人的風格"}

品牌顏色:
{f"主色: {brand_model.colors.primary}" if brand_model.colors and brand_model.colors.primary else "無指定顏色方案"}
{f"次色: {brand_model.colors.secondary}" if brand_model.colors and brand_model.colors.secondary else ""}

生成的提示詞應該:
1. 描述能引起點擊的視覺元素
2. 保持與影片內容相關
3. 遵循品牌視覺風格
4. 避免文字過多（縮略圖中的文字應限制在 3-4 個詞）
5. 聚焦於高質量、專業的視覺效果
"""
        
        user_prompt = f"""
請為以下影片創建一個用於生成縮略圖的提示詞:

影片標題: {title}

影片內容摘要:
{script[:500]}{'...' if len(script) > 500 else ''}

你的提示詞應該描述:
1. 主要視覺元素和構圖
2. 顏色方案（符合品牌顏色）
3. 情感與氛圍
4. 任何應包含的文字（簡短）
5. 風格參考（如照片寫實、扁平設計等）

請注意，這個提示詞將用於圖像生成 AI，因此應該簡潔、具體且描述清晰。生成的縮略圖應該吸引人，同時準確反映影片內容和品牌風格。
"""
        
        try:
            # 調用 API 生成縮略圖提示詞
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500,
                n=1
            )
            
            # 提取生成的提示詞
            thumbnail_prompt = response.choices[0].message.content.strip()
            
            return {
                "success": True,
                "prompt": thumbnail_prompt,
                "title": title,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"生成影片縮略圖提示詞時出錯: {e}")
            return {
                "success": False,
                "error": str(e),
                "prompt": ""
            }
    
    def _create_script_system_prompt(self, brand_model: BrandModel, platform: Platform, 
                                   style: Optional[str] = None) -> str:
        """
        創建影片腳本系統提示詞。
        
        Args:
            brand_model: 品牌模型
            platform: 目標平台
            style: 影片風格
            
        Returns:
            系統提示詞
        """
        # 品牌說明
        brand_description = f"你是 {brand_model.name} 的影片腳本撰寫專家。"
        
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
        
        # 風格指南
        style_guide = ""
        if style:
            style_guide = f"""
影片風格: {style}
請確保腳本符合這種風格，包括語調、節奏和內容結構。
            """
        
        # 平台特定指南
        platform_guide = self._get_platform_video_guidelines(platform)
        
        # 組合系統提示詞
        system_prompt = f"""
{brand_description}

{audience_info}

{style_instructions}

關鍵詞和主題:
{', '.join(brand_model.keywords) if brand_model.keywords else '未提供特定關鍵詞'}

{style_guide}

{platform_guide}

你的任務是創建一個專業的影片腳本，該腳本:
1. 與品牌風格和語調一致
2. 適合指定的平台和影片風格
3. 結構清晰，包括開場、主體內容和結尾
4. 節奏適當，能在指定時間內完成
5. 包含對視覺元素的引導（如需要）
6. 具有吸引力，能保持觀眾注意力

請提供完整的腳本，包括:
- 影片標題
- 影片描述（如適用）
- 完整的旁白/對白文本
- 場景描述和視覺引導（如需要）
        """
        
        return system_prompt.strip()
    
    def _create_script_user_prompt(self,
                                 topic: str,
                                 brand_model: BrandModel,
                                 platform: Platform,
                                 duration_seconds: int,
                                 style: Optional[str],
                                 include_b_roll: bool,
                                 include_captions: bool,
                                 reference_content: Optional[str],
                                 target_audience: Optional[List[str]]) -> str:
        """
        創建影片腳本用戶提示詞。
        
        Args:
            [與 generate_video_script 相同的參數]
            
        Returns:
            用戶提示詞
        """
        # 基本要求
        user_prompt = f"請為 {brand_model.name} 創建一個關於「{topic}」的影片腳本。"
        
        # 平台
        user_prompt += f"\n\n平台: {platform.value}"
        
        # 長度
        minutes = duration_seconds // 60
        seconds = duration_seconds % 60
        user_prompt += f"\n影片長度: {minutes}分{seconds}秒"
        
        # 風格
        if style:
            user_prompt += f"\n影片風格: {style}"
        
        # 目標受眾
        if target_audience:
            user_prompt += f"\n目標受眾: {', '.join(target_audience)}"
        
        # 參考內容
        if reference_content:
            user_prompt += f"\n\n參考材料:\n{reference_content}"
        
        # 特殊要求
        special_requests = []
        
        if include_b_roll:
            special_requests.append("包含 B-roll 畫面建議，以增強視覺吸引力")
        
        if include_captions:
            special_requests.append("設計易於閱讀的字幕，確保關鍵信息即使在無聲觀看時也能傳達")
        
        if special_requests:
            user_prompt += "\n\n特殊要求:\n" + "\n".join(f"- {req}" for req in special_requests)
        
        # 腳本結構
        user_prompt += """
\n\n請按以下格式提供腳本:
# 影片標題

## 影片描述
[簡短的影片描述，包含關鍵詞和號召性用語]

## 腳本
[詳細腳本，包含旁白/對白和視覺指引]
"""
        
        return user_prompt
    
    def _get_platform_video_guidelines(self, platform: Platform) -> str:
        """
        獲取平台特定的影片指南。
        
        Args:
            platform: 目標平台
            
        Returns:
            平台影片指南
        """
        guidelines = f"{platform.value} 影片指南:\n"
        
        if platform == Platform.YOUTUBE:
            guidelines += """
- 前 15 秒最為關鍵，應包含吸引人的開場和主題概述
- 保持節奏適中，每 3-4 分鐘引入新元素以保持觀眾注意力
- 包含清晰的號召性用語（訂閱、點贊、評論）
- 標題應引人注目且包含關鍵詞，長度控制在 60 字元以內
- 在結尾預告下一影片或引導至其他相關內容
- 考慮添加時間戳，幫助觀眾導航較長的影片
            """
        
        elif platform == Platform.INSTAGRAM:
            guidelines += """
- Instagram Feed 影片應保持在 60 秒以內，Reels 可達 90 秒
- 開場需在前 3 秒吸引注意力
- 使用動態視覺元素和快節奏內容
- 設計適合無聲觀看的內容，確保字幕覆蓋關鍵信息
- 考慮垂直 9:16 的格式，尤其是 Reels
- 內容應簡潔有力，直接進入主題
            """
        
        elif platform == Platform.FACEBOOK:
            guidelines += """
- 開場需在 3-5 秒內吸引注意力，考慮添加引人入勝的問題或陳述
- 理想長度為 1-3 分鐘，內容豐富但簡明
- 設計適合無聲觀看的內容，添加清晰的字幕
- 包含引導分享或評論的號召性用語
- 考慮觀眾可能在移動設備上觀看的因素
- 可考慮正方形 1:1 格式以最大化動態消息中的可見性
            """
        
        elif platform == Platform.LINKEDIN:
            guidelines += """
- 內容應專業、信息豐富，提供具體價值
- 理想長度為 1-3 分鐘
- 使用專業語調，但避免過於正式或充滿行業術語
- 包含可操作的見解或建議，而非僅僅是宣傳
- 設計適合辦公環境觀看的內容（考慮無聲觀看）
- 引用數據、研究或專家觀點以增加可信度
            """
        
        else:
            guidelines += "- 請遵循一般影片內容最佳實踐，創建簡潔、引人入勝且與平台適配的內容。"
        
        return guidelines
    
    def _extract_script_components(self, script_text: str) -> Tuple[str, str, str]:
        """
        從生成的腳本文本中提取標題、描述和腳本內容。
        
        Args:
            script_text: 完整的腳本文本
            
        Returns:
            (標題, 描述, 腳本內容)
        """
        title = "未指定標題"
        description = ""
        script = script_text
        
        # 提取標題
        title_match = re.search(r'#\s*(.*?)(?:\n|$)', script_text)
        if title_match:
            title = title_match.group(1).strip()
        
        # 提取描述
        desc_match = re.search(r'##\s*影片描述\s*\n(.*?)(?:\n##|\Z)', script_text, re.DOTALL)
        if desc_match:
            description = desc_match.group(1).strip()
        
        # 提取腳本內容
        script_match = re.search(r'##\s*腳本\s*\n(.*?)(?:\Z)', script_text, re.DOTALL)
        if script_match:
            script = script_match.group(1).strip()
        
        return title, description, script


# 全局影片生成器實例
video_generator = VideoGenerator()
