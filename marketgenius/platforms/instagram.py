#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MarketGenius Instagram 平台適配器。
負責根據 Instagram 平台的特定要求優化內容。
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple

from marketgenius.data.schemas import ContentType, ContentItem, TextContent, ImageContent, VideoContent

logger = logging.getLogger(__name__)


class InstagramAdapter:
    """Instagram 平台內容適配器。"""
    
    # Instagram 平台限制和最佳實踐
    MAX_CAPTION_LENGTH = 2200  # 字元數
    IDEAL_CAPTION_LENGTH = 150  # 單詞數上限，最佳實踐
    MAX_HASHTAGS = 30  # 技術上限
    OPTIMAL_HASHTAGS = 11  # 最佳實踐數量
    ALLOWED_IMAGE_FORMATS = [".jpg", ".jpeg", ".png"]
    MAX_VIDEO_LENGTH_SECONDS = 90  # Reels 影片
    MAX_FEED_VIDEO_SECONDS = 60  # Feed 影片
    ALLOWED_ASPECT_RATIOS = ["1:1", "4:5", "16:9"]  # 方形、垂直、橫向
    
    def __init__(self):
        """初始化 Instagram 適配器。"""
        logger.debug("初始化 Instagram 平台適配器")
    
    def adapt_content(self, content_item: ContentItem) -> Dict[str, Any]:
        """
        根據 Instagram 平台要求適配內容。
        
        Args:
            content_item: 要適配的內容項目
            
        Returns:
            適配後的內容
        """
        # 檢查內容類型並調用相應的適配方法
        if content_item.content_type == ContentType.TEXT:
            # Instagram 沒有純文本功能，轉換為圖像說明
            return self.adapt_to_caption(content_item)
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
    
    def adapt_to_caption(self, content_item: ContentItem) -> Dict[str, Any]:
        """
        將文本內容適配為 Instagram 圖像說明。
        
        Args:
            content_item: 包含文本內容的內容項目
            
        Returns:
            轉換為圖像說明的內容
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
        
        # 適配說明長度
        adapted_caption = self._adapt_caption_length(original_text)
        
        # 適配主題標籤
        adapted_caption, hashtags = self._adapt_hashtags(adapted_caption, content_item.text_content.hashtags)
        
        # 檢查提及（mentions）格式
        adapted_caption = self._adapt_mentions(adapted_caption)
        
        # 創建新的圖像內容項目
        adapted_content = content_item.copy(deep=True)
        adapted_content.content_type = ContentType.IMAGE
        
        # 建立圖像內容
        if not adapted_content.image_content:
            adapted_content.image_content = ImageContent(
                prompt="根據圖像說明生成圖像",
                caption=adapted_caption,
                alt_text=f"由 {adapted_content.brand_id} 創建的圖像"
            )
        else:
            adapted_content.image_content.caption = adapted_caption
        
        # 添加元數據
        metadata = {
            "platform": "instagram",
            "content_type": "image",
            "original_type": "text",
            "caption_length": len(adapted_caption),
            "character_count": len(adapted_caption),
            "word_count": len(adapted_caption.split()),
            "hashtag_count": len(hashtags) if hashtags else 0,
            "is_within_limits": len(adapted_caption) <= self.MAX_CAPTION_LENGTH,
            "note": "純文本內容已轉換為帶說明的圖像，因為 Instagram 不支持純文本貼文",
            "recommendations": []
        }
        
        # 添加建議
        if len(adapted_caption.split()) > self.IDEAL_CAPTION_LENGTH:
            metadata["recommendations"].append(f"考慮縮短說明，Instagram 上最佳說明長度為 {self.IDEAL_CAPTION_LENGTH} 詞以內")
        
        if not hashtags:
            metadata["recommendations"].append("添加 5-15 個相關主題標籤以提高發現性")
        elif len(hashtags) < 5:
            metadata["recommendations"].append("增加使用的主題標籤數量，Instagram 上 5-15 個主題標籤效果最佳")
        elif len(hashtags) > self.OPTIMAL_HASHTAGS:
            metadata["recommendations"].append(f"主題標籤過多，考慮減少到 {self.OPTIMAL_HASHTAGS} 個以獲得最佳參與度")
        
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
        adapted_caption = self._adapt_caption_length(caption)
        
        # 適配主題標籤
        adapted_caption, hashtags = self._adapt_hashtags(adapted_caption, None)
        
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
            "platform": "instagram",
            "content_type": "image",
            "caption_length": len(adapted_caption),
            "image_url": content_item.image_content.image_url,
            "alt_text_available": bool(content_item.image_content.alt_text),
            "image_format_valid": image_format_valid,
            "hashtag_count": len(hashtags) if hashtags else 0,
            "recommendations": []
        }
        
        # 添加建議
        if not content_item.image_content.alt_text:
            metadata["recommendations"].append("添加替代文本以提高可訪問性和 SEO 表現")
        
        if not image_format_valid:
            metadata["recommendations"].append(format_message)
        
        if not caption:
            metadata["recommendations"].append("添加引人入勝的圖像說明以提高參與度")
        
        if not hashtags:
            metadata["recommendations"].append("添加 5-15 個相關主題標籤以提高發現性")
        elif len(hashtags) < 5:
            metadata["recommendations"].append("增加使用的主題標籤數量，Instagram 上 5-15 個主題標籤效果最佳")
        
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
        
        # 取得描述並適配
        description = content_item.video_content.description or ""
        adapted_description = self._adapt_caption_length(description)
        
        # 適配主題標籤
        adapted_description, hashtags = self._adapt_hashtags(adapted_description, None)
        
        # 更新內容
        adapted_content = content_item.copy(deep=True)
        adapted_content.video_content.description = adapted_description
        
        # 檢查影片長度
        duration_valid = True
        duration_message = ""
        if content_item.video_content.duration_seconds:
            duration = content_item.video_content.duration_seconds
            if duration > self.MAX_VIDEO_LENGTH_SECONDS:
                duration_valid = False
                duration_message = f"影片超出 Instagram Reels 最大長度 ({duration} 秒 > {self.MAX_VIDEO_LENGTH_SECONDS} 秒)"
            elif duration > self.MAX_FEED_VIDEO_SECONDS:
                duration_message = f"影片長度 ({duration} 秒) 超出 Feed 影片限制 ({self.MAX_FEED_VIDEO_SECONDS} 秒)，但適合 Reels"
        
        # 添加元數據
        metadata = {
            "platform": "instagram",
            "content_type": "video",
            "video_type": "reels" if content_item.video_content.duration_seconds > self.MAX_FEED_VIDEO_SECONDS else "feed",
            "description_length": len(adapted_description),
            "duration_seconds": content_item.video_content.duration_seconds,
            "duration_valid": duration_valid,
            "hashtag_count": len(hashtags) if hashtags else 0,
            "recommendations": []
        }
        
        # 添加建議
        if duration_message:
            metadata["recommendations"].append(duration_message)
        
        if not content_item.video_content.thumbnail_prompt:
            metadata["recommendations"].append("添加自定義縮略圖以提高點擊率")
        
        if not hashtags:
            metadata["recommendations"].append("添加 5-15 個相關主題標籤以提高發現性")
        elif len(hashtags) < 5:
            metadata["recommendations"].append("增加使用的主題標籤數量，Instagram 上 5-15 個主題標籤效果最佳")
        
        return {
            "success": True,
            "content": adapted_content.dict(),
            "metadata": metadata
        }
    
    def _adapt_caption_length(self, caption: str) -> str:
        """
        適配說明長度。
        
        Args:
            caption: 原始說明
            
        Returns:
            適配後的說明
        """
        if len(caption) <= self.MAX_CAPTION_LENGTH:
            return caption
        
        # 如果超出最大長度，進行裁剪
        logger.warning(f"說明超出 Instagram 最大長度 ({len(caption)} > {self.MAX_CAPTION_LENGTH})，將進行裁剪")
        return self._truncate_text(caption, self.MAX_CAPTION_LENGTH)
    
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
        
        # 如果超出最大數量，只保留前幾個
        if len(all_hashtags) > self.MAX_HASHTAGS:
            logger.info(f"主題標籤數量超出 Instagram 限制 ({len(all_hashtags)} > {self.MAX_HASHTAGS})，只保留前 {self.MAX_HASHTAGS} 個")
            all_hashtags = all_hashtags[:self.MAX_HASHTAGS]
        
        # 對於 Instagram，通常建議將所有主題標籤放在說明末尾
        # 如果文本中有分散的主題標籤，重新組織它們
        if text_hashtags and len(text_hashtags) > 3:
            # 移除文本中的所有主題標籤
            text_without_hashtags = re.sub(hashtag_pattern, '', text)
            text_without_hashtags = text_without_hashtags.strip()
            
            # 將主題標籤集中到末尾
            hashtag_text = " ".join([f"#{tag}" for tag in all_hashtags])
            
            # 在說明和主題標籤之間添加分隔
            if text_without_hashtags and hashtag_text:
                final_text = text_without_hashtags + "\n\n" + hashtag_text
            else:
                final_text = text_without_hashtags + hashtag_text
            
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
        # Instagram 使用 @username 格式
        # 確保所有提及都使用正確格式
        mention_pattern = r'@([a-zA-Z0-9._]+)'
        mentions = re.findall(mention_pattern, text)
        
        # 現在 Instagram 的提及格式已經是 @username，所以不需要額外處理
        # 但這裡保留此方法以便未來需要時擴展
        
        return text
    
    def _check_image_format(self, image_url: str) -> Tuple[bool, str]:
        """
        檢查圖像格式是否適合 Instagram。
        
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
            return False, f"圖像格式可能不受支持，Instagram 支持: {', '.join(self.ALLOWED_IMAGE_FORMATS)}"
        
        return True, "圖像格式有效"
    
    def _check_aspect_ratio(self, width: int, height: int) -> Tuple[bool, str, str]:
        """
        檢查圖像或影片的寬高比。
        
        Args:
            width: 寬度
            height: 高度
            
        Returns:
            (是否為有效比例, 消息, 最接近的標準比例)
        """
        # 計算比例
        ratio = width / height
        
        # 檢查是否接近標準比例
        square_ratio = 1.0  # 1:1
        portrait_ratio = 0.8  # 4:5
        landscape_ratio = 16/9  # 16:9
        
        # 找到最接近的標準比例
        ratios = [square_ratio, portrait_ratio, landscape_ratio]
        ratio_names = ["1:1", "4:5", "16:9"]
        differences = [abs(ratio - r) for r in ratios]
        closest_index = differences.index(min(differences))
        closest_ratio = ratio_names[closest_index]
        
        # 檢查是否在允許的範圍內
        if closest_index == 0 and abs(ratio - square_ratio) < 0.05:
            return True, "方形比例 (1:1) 適合 Instagram", closest_ratio
        elif closest_index == 1 and abs(ratio - portrait_ratio) < 0.05:
            return True, "縱向比例 (4:5) 適合 Instagram", closest_ratio
        elif closest_index == 2 and abs(ratio - landscape_ratio) < 0.1:
            return True, "橫向比例 (16:9) 適合 Instagram", closest_ratio
        else:
            return False, f"比例 {width}:{height} 不是 Instagram 推薦的比例，最接近 {closest_ratio}", closest_ratio
    
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
    
    def get_preferred_image_dimensions(self) -> List[Dict[str, Any]]:
        """
        獲取 Instagram 推薦的圖像尺寸。
        
        Returns:
            推薦的圖像尺寸列表
        """
        return [
            {"name": "方形", "width": 1080, "height": 1080, "ratio": "1:1", "usage": "Feed, 縮略圖"},
            {"name": "縱向", "width": 1080, "height": 1350, "ratio": "4:5", "usage": "Feed"},
            {"name": "橫向", "width": 1080, "height": 608, "ratio": "16:9", "usage": "IGTV 封面"},
            {"name": "故事", "width": 1080, "height": 1920, "ratio": "9:16", "usage": "Stories, Reels"},
        ]
    
    def get_preferred_video_dimensions(self) -> List[Dict[str, Any]]:
        """
        獲取 Instagram 推薦的影片尺寸。
        
        Returns:
            推薦的影片尺寸列表
        """
        return [
            {"name": "方形", "width": 1080, "height": 1080, "ratio": "1:1", "usage": "Feed", "max_duration": 60},
            {"name": "縱向", "width": 1080, "height": 1350, "ratio": "4:5", "usage": "Feed", "max_duration": 60},
            {"name": "故事/Reels", "width": 1080, "height": 1920, "ratio": "9:16", "usage": "Stories, Reels", "max_duration": 90},
            {"name": "IGTV", "width": 1080, "height": 1920, "ratio": "9:16", "usage": "IGTV", "max_duration": 3600},
        ]


# 全局 Instagram 適配器實例
instagram_adapter = InstagramAdapter()
