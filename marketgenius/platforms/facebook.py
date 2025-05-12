#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MarketGenius Facebook 平台適配器。
負責根據 Facebook 平台的特定要求優化內容。
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple

from marketgenius.data.schemas import ContentType, ContentItem, TextContent, ImageContent, VideoContent

logger = logging.getLogger(__name__)


class FacebookAdapter:
    """Facebook 平台內容適配器。"""
    
    # Facebook 平台限制和最佳實踐
    MAX_POST_LENGTH = 63206  # 字元數
    IDEAL_POST_LENGTH = 40 # 單詞數
    MAX_TITLE_LENGTH = 100  # 字元數
    MAX_HASHTAGS = 5  # 最佳實踐
    MAX_DESCRIPTION_LENGTH = 5000  # 字元數
    ALLOWED_IMAGE_FORMATS = [".jpg", ".jpeg", ".png", ".gif"]
    
    def __init__(self):
        """初始化 Facebook 適配器。"""
        logger.debug("初始化 Facebook 平台適配器")
    
    def adapt_content(self, content_item: ContentItem) -> Dict[str, Any]:
        """
        根據 Facebook 平台要求適配內容。
        
        Args:
            content_item: 要適配的內容項目
            
        Returns:
            適配後的內容
        """
        # 檢查內容類型並調用相應的適配方法
        if content_item.content_type == ContentType.TEXT:
            return self.adapt_text_content(content_item)
        elif content_item.content_type == ContentType.IMAGE:
            return self.adapt_image_content(content_item)
        elif content_item.content_type == ContentType.VIDEO:
            return self.adapt_video_content(content_item)
        else:
            logger.warning(f"不支持的內容類型: {content_item.content_type}")
            return {
                "success": False,
                "error": f"不支持的內容類型: {content_item.content_type}",
                "content": content_item.dict()
            }
    
    def adapt_text_content(self, content_item: ContentItem) -> Dict[str, Any]:
        """
        適配文本內容。
        
        Args:
            content_item: 包含文本內容的內容項目
            
        Returns:
            適配後的文本內容
        """
        if not content_item.text_content:
            logger.error("內容項目缺少文本內容")
            return {
                "success": False,
                "error": "缺少文本內容",
                "content": content_item.dict()
            }
        
        # 取得原始文本
        original_text = content_item.text_content.text
        
        # 適配文本長度
        adapted_text = self._adapt_text_length(original_text)
        
        # 適配主題標籤
        adapted_text, hashtags = self._adapt_hashtags(adapted_text, content_item.text_content.hashtags)
        
        # 檢查提及（mentions）格式
        adapted_text = self._adapt_mentions(adapted_text)
        
        # 更新內容
        adapted_content = content_item.copy(deep=True)
        adapted_content.text_content.text = adapted_text
        adapted_content.text_content.hashtags = hashtags
        
        # 添加 Facebook 特定元數據
        metadata = {
            "platform": "facebook",
            "content_type": "text",
            "character_count": len(adapted_text),
            "word_count": len(adapted_text.split()),
            "hashtag_count": len(hashtags) if hashtags else 0,
            "is_within_limits": len(adapted_text) <= self.MAX_POST_LENGTH,
            "recommendations": []
        }
        
        # 添加建議
        if len(adapted_text.split()) > self.IDEAL_POST_LENGTH * 2:
            metadata["recommendations"].append("考慮縮短貼文，Facebook 上較短的貼文（40-80 詞）通常表現更好")
        
        if not hashtags or len(hashtags) < 2:
            metadata["recommendations"].append("考慮添加 2-3 個相關主題標籤以提高發現性")
        
        return {
            "success": True,
            "content": adapted_content.dict(),
            "metadata": metadata
        }
    
    def adapt_image_content(self, content_item: ContentItem) -> Dict[str, Any]:
        """
        適配圖像內容。
        
        Args:
            content_item: 包含圖像內容的內容項目
            
        Returns:
            適配後的圖像內容
        """
        if not content_item.image_content:
            logger.error("內容項目缺少圖像內容")
            return {
                "success": False,
                "error": "缺少圖像內容",
                "content": content_item.dict()
            }
        
        # 適配圖像說明
        caption = content_item.image_content.caption or ""
        adapted_caption, hashtags = self._adapt_hashtags(caption, None)
        
        # 檢查圖像格式（如果有 URL）
        image_format_valid = True
        format_message = ""
        if content_item.image_content.image_url:
            image_format_valid, format_message = self._check_image_format(content_item.image_content.image_url)
        
        # 更新內容
        adapted_content = content_item.copy(deep=True)
        adapted_content.image_content.caption = adapted_caption
        
        # 添加元數據
        metadata = {
            "platform": "facebook",
            "content_type": "image",
            "caption_length": len(adapted_caption),
            "image_url": content_item.image_content.image_url,
            "alt_text_available": bool(content_item.image_content.alt_text),
            "image_format_valid": image_format_valid,
            "recommendations": []
        }
        
        # 添加建議
        if not content_item.image_content.alt_text:
            metadata["recommendations"].append("添加替代文本以提高可訪問性")
        
        if not image_format_valid:
            metadata["recommendations"].append(format_message)
        
        if not caption:
            metadata["recommendations"].append("添加引人入勝的圖像說明以提高參與度")
        
        return {
            "success": True,
            "content": adapted_content.dict(),
            "metadata": metadata
        }
    
    def adapt_video_content(self, content_item: ContentItem) -> Dict[str, Any]:
        """
        適配影片內容。
        
        Args:
            content_item: 包含影片內容的內容項目
            
        Returns:
            適配後的影片內容
        """
        if not content_item.video_content:
            logger.error("內容項目缺少影片內容")
            return {
                "success": False,
                "error": "缺少影片內容",
                "content": content_item.dict()
            }
        
        # 適配標題長度
        original_title = content_item.video_content.title
        adapted_title = self._truncate_text(original_title, self.MAX_TITLE_LENGTH)
        
        # 適配描述
        description = content_item.video_content.description or ""
        adapted_description = self._truncate_text(description, self.MAX_DESCRIPTION_LENGTH)
        
        # 更新內容
        adapted_content = content_item.copy(deep=True)
        adapted_content.video_content.title = adapted_title
        adapted_content.video_content.description = adapted_description
        
        # 檢查影片長度最佳實踐
        duration_optimal = True
        duration_message = ""
        if content_item.video_content.duration_seconds:
            duration = content_item.video_content.duration_seconds
            if duration < 15:
                duration_optimal = False
                duration_message = "影片過短，Facebook 建議至少 15 秒"
            elif duration > 240:
                duration_optimal = False
                duration_message = "影片較長，考慮創建 2-4 分鐘的版本以提高參與度"
        
        # 添加元數據
        metadata = {
            "platform": "facebook",
            "content_type": "video",
            "title_length": len(adapted_title),
            "description_length": len(adapted_description),
            "duration_seconds": content_item.video_content.duration_seconds,
            "duration_optimal": duration_optimal,
            "recommendations": []
        }
        
        # 添加建議
        if not duration_optimal:
            metadata["recommendations"].append(duration_message)
        
        if original_title != adapted_title:
            metadata["recommendations"].append(f"標題已從 {len(original_title)} 字元縮短至 {len(adapted_title)} 字元")
        
        if not description:
            metadata["recommendations"].append("添加引人入勝的影片描述以提高發現性和參與度")
        
        if not content_item.video_content.thumbnail_prompt:
            metadata["recommendations"].append("添加自定義縮略圖以提高點擊率")
        
        return {
            "success": True,
            "content": adapted_content.dict(),
            "metadata": metadata
        }
    
    def _adapt_text_length(self, text: str) -> str:
        """
        適配文本長度。
        
        Args:
            text: 原始文本
            
        Returns:
            適配後的文本
        """
        if len(text) <= self.MAX_POST_LENGTH:
            return text
        
        # 如果超出最大長度，進行裁剪
        logger.warning(f"文本超出 Facebook 最大長度 ({len(text)} > {self.MAX_POST_LENGTH})，將進行裁剪")
        return self._truncate_text(text, self.MAX_POST_LENGTH)
    
    def _adapt_hashtags(self, text: str, existing_hashtags: Optional[List[str]] = None) -> Tuple[str, List[str]]:
        """
        適配主題標籤。
        
        Args:
            text: 包含主題標籤的文本
            existing_hashtags: 現有的主題標籤列表
            
        Returns:
            (適配後的文本, 主題標籤列表)
        """
        # 提取文本中的所有主題標籤
        hashtag_pattern = r'#(\w+)'
        text_hashtags = re.findall(hashtag_pattern, text)
        
        # 合併所有主題標籤
        all_hashtags = []
        if text_hashtags:
            all_hashtags.extend(text_hashtags)
        if existing_hashtags:
            all_hashtags.extend([tag for tag in existing_hashtags if tag not in all_hashtags])
        
        # 如果超出最佳數量，只保留前幾個
        if len(all_hashtags) > self.MAX_HASHTAGS:
            logger.info(f"主題標籤數量超出建議數量 ({len(all_hashtags)} > {self.MAX_HASHTAGS})，只保留前 {self.MAX_HASHTAGS} 個")
            all_hashtags = all_hashtags[:self.MAX_HASHTAGS]
        
        # 如果需要從文本中移除多餘的主題標籤
        if len(text_hashtags) > self.MAX_HASHTAGS:
            # 移除所有主題標籤
            text_without_hashtags = re.sub(hashtag_pattern, '', text)
            # 重新添加前幾個
            final_text = text_without_hashtags.strip()
            for tag in all_hashtags:
                final_text += f" #{tag}"
            return final_text, all_hashtags
        
        return text, all_hashtags
    
    def _adapt_mentions(self, text: str) -> str:
        """
        檢查並適配提及（@mentions）格式。
        
        Args:
            text: 包含提及的文本
            
        Returns:
            適配後的文本
        """
        # Facebook 使用 @username 格式
        # 確保所有提及都使用正確格式
        mention_pattern = r'@([a-zA-Z0-9._]+)'
        mentions = re.findall(mention_pattern, text)
        
        # 現在 Facebook 的提及格式已經是 @username，所以不需要額外處理
        # 但這裡保留此方法以便未來需要時擴展
        
        return text
    
    def _check_image_format(self, image_url: str) -> Tuple[bool, str]:
        """
        檢查圖像格式是否適合 Facebook。
        
        Args:
            image_url: 圖像 URL
            
        Returns:
            (格式是否有效, 消息)
        """
        if not image_url:
            return False, "缺少圖像 URL"
        
        # 檢查文件擴展名
        lower_url = image_url.lower()
        valid_format = any(lower_url.endswith(fmt) for fmt in self.ALLOWED_IMAGE_FORMATS)
        
        if not valid_format:
            return False, f"圖像格式可能不受支持，Facebook 支持: {', '.join(self.ALLOWED_IMAGE_FORMATS)}"
        
        return True, "圖像格式有效"
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """
        將文本截斷到指定長度。
        
        Args:
            text: 原始文本
            max_length: 最大長度
            
        Returns:
            截斷後的文本
        """
        if len(text) <= max_length:
            return text
        
        # 尋找最後一個完整單詞的位置
        truncated = text[:max_length]
        last_space = truncated.rfind(' ')
        
        if last_space > 0:
            truncated = truncated[:last_space]
        
        # 添加省略號
        return truncated.strip() + "..."


# 全局 Facebook 適配器實例
facebook_adapter = FacebookAdapter()
