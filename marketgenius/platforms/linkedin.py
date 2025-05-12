#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MarketGenius LinkedIn 平台適配器。
負責根據 LinkedIn 平台的特定要求優化內容。
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple

from marketgenius.data.schemas import ContentType, ContentItem, TextContent, ImageContent, VideoContent

logger = logging.getLogger(__name__)


class LinkedInAdapter:
    """LinkedIn 平台內容適配器。"""
    
    # LinkedIn 平台限制和最佳實踐
    MAX_POST_LENGTH = 3000  # 字元數
    IDEAL_POST_LENGTH = 200  # 單詞數（最佳實踐）
    MAX_ARTICLE_LENGTH = 100000  # 字元數
    IDEAL_ARTICLE_LENGTH = 1500  # 單詞數（最佳實踐）
    MAX_TITLE_LENGTH = 150  # 字元數
    IDEAL_HEADLINE_LENGTH = 70  # 字元數（最佳實踐）
    MAX_DESCRIPTION_LENGTH = 2000  # 字元數
    OPTIMAL_HASHTAGS = 5  # 最佳實踐數量（3-5 個）
    MAX_HASHTAGS = 10  # 技術上沒有限制，但超過 10 個會影響可讀性
    ALLOWED_IMAGE_FORMATS = [".jpg", ".jpeg", ".png", ".gif"]
    MAX_VIDEO_LENGTH_SECONDS = 600  # 10 分鐘
    IDEAL_VIDEO_LENGTH_SECONDS = 180  # 3 分鐘（最佳實踐）
    
    def __init__(self):
        """初始化 LinkedIn 適配器。"""
        logger.debug("初始化 LinkedIn 平台適配器")
    
    def adapt_content(self, content_item: ContentItem) -> Dict[str, Any]:
        """
        根據 LinkedIn 平台要求適配內容。
        
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
        
        # 判斷內容類型（貼文還是文章）
        is_article = len(original_text.split()) > 300 or len(original_text) > 1000
        
        if is_article:
            # 適配文章長度
            adapted_text = self._adapt_article_length(original_text)
        else:
            # 適配貼文長度
            adapted_text = self._adapt_post_length(original_text)
        
        # 適配主題標籤
        adapted_text, hashtags = self._adapt_hashtags(adapted_text, content_item.text_content.hashtags)
        
        # 檢查提及（mentions）格式
        adapted_text = self._adapt_mentions(adapted_text)
        
        # 更新內容
        adapted_content = content_item.copy(deep=True)
        adapted_content.text_content.text = adapted_text
        adapted_content.text_content.hashtags = hashtags
        
        # 添加 LinkedIn 特定元數據
        metadata = {
            "platform": "linkedin",
            "content_type": "article" if is_article else "post",
            "character_count": len(adapted_text),
            "word_count": len(adapted_text.split()),
            "hashtag_count": len(hashtags) if hashtags else 0,
            "is_within_limits": len(adapted_text) <= (self.MAX_ARTICLE_LENGTH if is_article else self.MAX_POST_LENGTH),
            "recommendations": []
        }
        
        # 添加建議
        if is_article:
            if len(adapted_text.split()) < 800:
                metadata["recommendations"].append("文章較短，建議擴展內容至 800-2000 詞以獲得最佳效果")
            elif len(adapted_text.split()) > 2000:
                metadata["recommendations"].append("文章較長，考慮分割成多篇較短的文章")
        else:
            if len(adapted_text.split()) > self.IDEAL_POST_LENGTH * 1.5:
                metadata["recommendations"].append(f"貼文較長，LinkedIn 上較短的貼文（{self.IDEAL_POST_LENGTH} 詞左右）通常表現更好")
        
        if not hashtags:
            metadata["recommendations"].append("添加 3-5 個相關主題標籤以提高發現性")
        elif len(hashtags) > self.OPTIMAL_HASHTAGS:
            metadata["recommendations"].append(f"主題標籤過多，LinkedIn 上 3-5 個主題標籤效果最佳")
        
        # 適配圖片數量建議
        metadata["recommendations"].append("LinkedIn 上有圖片的貼文參與度比純文本高 98%")
        
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
        
        # 判斷內容類型（貼文還是文章）
        is_article = len(caption.split()) > 300 or len(caption) > 1000
        
        if is_article:
            adapted_caption = self._adapt_article_length(caption)
        else:
            adapted_caption = self._adapt_post_length(caption)
        
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
            "platform": "linkedin",
            "content_type": "image",
            "post_type": "article" if is_article else "post",
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
        elif is_article and len(caption.split()) < 800:
            metadata["recommendations"].append("文章較短，建議擴展內容至 800-2000 詞以獲得最佳效果")
        
        if not hashtags:
            metadata["recommendations"].append("添加 3-5 個相關主題標籤以提高發現性")
        elif len(hashtags) > self.OPTIMAL_HASHTAGS:
            metadata["recommendations"].append(f"主題標籤過多，LinkedIn 上 3-5 個主題標籤效果最佳")
        
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
        
        # 適配主題標籤
        adapted_description, hashtags = self._adapt_hashtags(adapted_description, None)
        
        # 更新內容
        adapted_content = content_item.copy(deep=True)
        adapted_content.video_content.title = adapted_title
        adapted_content.video_content.description = adapted_description
        
        # 檢查影片長度
        duration_valid = True
        duration_message = ""
        if content_item.video_content.duration_seconds:
            duration = content_item.video_content.duration_seconds
            if duration > self.MAX_VIDEO_LENGTH_SECONDS:
                duration_valid = False
                duration_message = f"影片超出 LinkedIn 最大長度 ({duration} 秒 > {self.MAX_VIDEO_LENGTH_SECONDS} 秒)"
            elif duration > self.IDEAL_VIDEO_LENGTH_SECONDS:
                duration_message = f"影片較長，LinkedIn 上 {self.IDEAL_VIDEO_LENGTH_SECONDS} 秒以內的影片通常表現更好"
        
        # 添加元數據
        metadata = {
            "platform": "linkedin",
            "content_type": "video",
            "title_length": len(adapted_title),
            "description_length": len(adapted_description),
            "duration_seconds": content_item.video_content.duration_seconds,
            "duration_valid": duration_valid,
            "hashtag_count": len(hashtags) if hashtags else 0,
            "recommendations": []
        }
        
        # 添加建議
        if duration_message:
            metadata["recommendations"].append(duration_message)
        
        if original_title != adapted_title:
            metadata["recommendations"].append(f"標題已從 {len(original_title)} 字元縮短至 {len(adapted_title)} 字元")
        
        if not description:
            metadata["recommendations"].append("添加專業的影片描述以提高發現性和參與度")
        
        if not content_item.video_content.thumbnail_prompt:
            metadata["recommendations"].append("添加自定義縮略圖以提高點擊率")
        
        if not hashtags:
            metadata["recommendations"].append("添加 3-5 個相關主題標籤以提高發現性")
        elif len(hashtags) > self.OPTIMAL_HASHTAGS:
            metadata["recommendations"].append(f"主題標籤過多，LinkedIn 上 3-5 個主題標籤效果最佳")
        
        return {
            "success": True,
            "content": adapted_content.dict(),
            "metadata": metadata
        }
    
    def _adapt_post_length(self, text: str) -> str:
        """
        適配貼文長度。
        
        Args:
            text: 原始文本
            
        Returns:
            適配後的文本
        """
        if len(text) <= self.MAX_POST_LENGTH:
            return text
        
        # 如果超出最大長度，進行裁剪
        logger.warning(f"文本超出 LinkedIn 貼文最大長度 ({len(text)} > {self.MAX_POST_LENGTH})，將進行裁剪")
        return self._truncate_text(text, self.MAX_POST_LENGTH)
    
    def _adapt_article_length(self, text: str) -> str:
        """
        適配文章長度。
        
        Args:
            text: 原始文本
            
        Returns:
            適配後的文本
        """
        if len(text) <= self.MAX_ARTICLE_LENGTH:
            return text
        
        # 如果超出最大長度，進行裁剪
        logger.warning(f"文本超出 LinkedIn 文章最大長度 ({len(text)} > {self.MAX_ARTICLE_LENGTH})，將進行裁剪")
        return self._truncate_text(text, self.MAX_ARTICLE_LENGTH)
    
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
            logger.info(f"主題標籤數量超出最佳實踐 ({len(all_hashtags)} > {self.MAX_HASHTAGS})，只保留前 {self.MAX_HASHTAGS} 個")
            all_hashtags = all_hashtags[:self.MAX_HASHTAGS]
        
        # LinkedIn 上主題標籤通常應該是適度使用並融入文本
        # 不需要特別處理文本中的標籤分布
        
        return text, all_hashtags
    
    def _adapt_mentions(self, text: str) -> str:
        """
        檢查並適配提及（@mentions）格式。
        
        Args:
            text: 包含提及的文本
            
        Returns:
            適配後的文本
        """
        # LinkedIn 使用 @firstname-lastname 格式
        # 確保所有提及都使用正確格式
        mention_pattern = r'@([a-zA-Z0-9\-._]+)'
        mentions = re.findall(mention_pattern, text)
        
        # LinkedIn 的提及格式目前不需要特別處理
        # 保留此方法以便未來需要時擴展
        
        return text
    
    def _check_image_format(self, image_url: str) -> Tuple[bool, str]:
        """
        檢查圖像格式是否適合 LinkedIn。
        
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
            return False, f"圖像格式可能不受支持，LinkedIn 支持: {', '.join(self.ALLOWED_IMAGE_FORMATS)}"
        
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
        
        # 尋找最後一個完整段落的位置
        if "\n\n" in text[:max_length - 50]:
            # 優先在段落處截斷
            truncated = text[:max_length]
            last_para = truncated.rfind("\n\n")
            
            if last_para > max_length * 0.7:  # 確保不會截斷得太短
                truncated = truncated[:last_para]
                return truncated.strip() + "...\n\n(全文請參見完整文章)"
        
        # 如果找不到段落或段落太靠前，則尋找最後一個完整句子的位置
        truncated = text[:max_length]
        last_sentence = max(
            truncated.rfind(". "),
            truncated.rfind("! "),
            truncated.rfind("? ")
        )
        
        if last_sentence > max_length * 0.7:  # 確保不會截斷得太短
            truncated = truncated[:last_sentence + 1]
            return truncated.strip() + " ...\n\n(全文請參見完整文章)"
        
        # 如果找不到合適的句子斷點，尋找最後一個完整單詞
        last_space = truncated.rfind(' ')
        
        if last_space > 0:
            truncated = truncated[:last_space]
        
        # 添加省略號
        return truncated.strip() + "...\n\n(全文請參見完整文章)"
    
    def get_preferred_content_lengths(self) -> Dict[str, Dict[str, int]]:
        """
        獲取 LinkedIn 推薦的內容長度。
        
        Returns:
            推薦的內容長度
        """
        return {
            "post": {
                "max_chars": self.MAX_POST_LENGTH,
                "ideal_words": self.IDEAL_POST_LENGTH,
                "max_hashtags": self.MAX_HASHTAGS,
                "optimal_hashtags": self.OPTIMAL_HASHTAGS
            },
            "article": {
                "max_chars": self.MAX_ARTICLE_LENGTH,
                "ideal_words": self.IDEAL_ARTICLE_LENGTH,
                "max_title_chars": self.MAX_TITLE_LENGTH,
                "ideal_headline_chars": self.IDEAL_HEADLINE_LENGTH
            },
            "video": {
                "max_seconds": self.MAX_VIDEO_LENGTH_SECONDS,
                "ideal_seconds": self.IDEAL_VIDEO_LENGTH_SECONDS,
                "max_description_chars": self.MAX_DESCRIPTION_LENGTH
            }
        }
    
    def get_professional_tone_recommendations(self) -> List[str]:
        """
        獲取 LinkedIn 專業語調建議。
        
        Returns:
            專業語調建議列表
        """
        return [
            "使用專業但不生硬的語調，保持親和力",
            "避免過多使用行業術語，確保一般受眾也能理解內容",
            "包含專業見解和有價值的觀點，而非僅僅陳述事實",
            "在介紹自己或產品前，先提供價值",
            "使用數據和案例支持你的論點",
            "保持簡潔和直接，避免過多修飾詞",
            "專注於解決方案而非問題",
            "創建結構化的內容，使用小標題和段落分隔",
            "通過提問和呼籲行動來鼓勵參與",
            "始終保持專業、積極和建設性"
        ]


# 全局 LinkedIn 適配器實例
linkedin_adapter = LinkedInAdapter()
