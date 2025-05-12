#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MarketGenius YouTube 平台適配器。
負責根據 YouTube 平台的特定要求優化內容。
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple

from marketgenius.data.schemas import ContentType, ContentItem, TextContent, ImageContent, VideoContent

logger = logging.getLogger(__name__)


class YouTubeAdapter:
    """YouTube 平台內容適配器。"""
    
    # YouTube 平台限制和最佳實踐
    MAX_TITLE_LENGTH = 100  # 字元數
    IDEAL_TITLE_LENGTH = 60  # 字元數（最佳實踐）
    MAX_DESCRIPTION_LENGTH = 5000  # 字元數
    MIN_DESCRIPTION_LENGTH = 250  # 字元數（最佳實踐）
    OPTIMAL_DESCRIPTION_LENGTH = 1000  # 字元數（最佳實踐）
    MAX_TAGS = 500  # 字元總數
    OPTIMAL_TAGS_COUNT = 10  # 標籤數量（最佳實踐）
    MAX_TAG_LENGTH = 30  # 每個標籤的最大長度
    MIN_VIDEO_LENGTH_SECONDS = 30  # 最短影片長度（最佳實踐）
    IDEAL_VIDEO_LENGTH_SECONDS = 480  # 最佳影片長度（統計顯示 8-10 分鐘效果最佳）
    MAX_SHORTS_LENGTH_SECONDS = 60  # YouTube Shorts 最長時間
    MAX_FILE_SIZE_GB = 256  # 最大文件大小（GB）
    
    def __init__(self):
        """初始化 YouTube 適配器。"""
        logger.debug("初始化 YouTube 平台適配器")
    
    def adapt_content(self, content_item: ContentItem) -> Dict[str, Any]:
        """
        根據 YouTube 平台要求適配內容。
        
        Args:
            content_item: 要適配的內容項目
            
        Returns:
            適配後的內容
        """
        # YouTube 主要支持影片內容
        if content_item.content_type == ContentType.VIDEO:
            return self.adapt_video_content(content_item)
        elif content_item.content_type == ContentType.TEXT:
            # 文本內容可以適配為 YouTube 說明
            return self.adapt_to_description(content_item)
        elif content_item.content_type == ContentType.IMAGE:
            # 圖像內容可以適配為 YouTube 縮略圖
            return self.adapt_to_thumbnail(content_item)
        else:
            logger.warning(f"YouTube 主要支持影片內容，其他類型可能需要轉換: {content_item.content_type}")
            return {
                "success": False,
                "error": f"YouTube 主要支持影片內容，其他類型可能需要轉換: {content_item.content_type}",
                "content": content_item.dict()
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
        
        # 適配標題
        original_title = content_item.video_content.title
        adapted_title = self._adapt_title(original_title)
        
        # 適配描述
        description = content_item.video_content.description or ""
        adapted_description = self._adapt_description(description)
        
        # 提取關鍵詞作為標籤
        tags = self._extract_tags(adapted_description, original_title)
        
        # 更新內容
        adapted_content = content_item.copy(deep=True)
        adapted_content.video_content.title = adapted_title
        adapted_content.video_content.description = adapted_description
        
        # 檢查影片長度
        duration_recommendation = ""
        is_shorts = False
        if content_item.video_content.duration_seconds:
            duration = content_item.video_content.duration_seconds
            if duration <= self.MAX_SHORTS_LENGTH_SECONDS:
                is_shorts = True
                if duration < 15:
                    duration_recommendation = "影片長度較短，甚至對於 YouTube Shorts 也偏短，建議至少 15 秒"
            elif duration < self.MIN_VIDEO_LENGTH_SECONDS:
                duration_recommendation = f"影片較短，YouTube 上至少 {self.MIN_VIDEO_LENGTH_SECONDS} 秒的影片表現更好"
            elif duration > self.IDEAL_VIDEO_LENGTH_SECONDS * 2:
                duration_recommendation = f"影片較長，YouTube 統計顯示 {self.IDEAL_VIDEO_LENGTH_SECONDS//60} 分鐘左右的影片參與度最高"
        
        # 添加元數據
        metadata = {
            "platform": "youtube",
            "content_type": "shorts" if is_shorts else "video",
            "title_length": len(adapted_title),
            "description_length": len(adapted_description),
            "title_seo_optimized": self._is_title_seo_optimized(adapted_title),
            "description_seo_optimized": self._is_description_seo_optimized(adapted_description),
            "tags_count": len(tags),
            "duration_seconds": content_item.video_content.duration_seconds,
            "has_thumbnail": bool(content_item.video_content.thumbnail_prompt),
            "recommendations": []
        }
        
        # 添加建議
        if original_title != adapted_title:
            metadata["recommendations"].append(f"標題已從 {len(original_title)} 字元調整為 {len(adapted_title)} 字元")
        
        if not self._is_title_seo_optimized(adapted_title):
            metadata["recommendations"].append("改進標題 SEO：添加主要關鍵詞並放在開頭，使標題引人注目")
        
        if not description:
            metadata["recommendations"].append("添加豐富的影片描述以提高 SEO 和觀眾參與度")
        elif len(adapted_description) < self.MIN_DESCRIPTION_LENGTH:
            metadata["recommendations"].append(f"描述過短，YouTube 建議至少 {self.MIN_DESCRIPTION_LENGTH} 字元以提高 SEO")
        
        if not content_item.video_content.thumbnail_prompt:
            metadata["recommendations"].append("添加自定義縮略圖以提高點擊率，高品質縮略圖可提高 30% 以上點擊率")
        
        if duration_recommendation:
            metadata["recommendations"].append(duration_recommendation)
        
        if not tags:
            metadata["recommendations"].append("添加相關標籤以提高發現性，YouTube 建議 5-15 個相關標籤")
        elif len(tags) < 5:
            metadata["recommendations"].append("增加標籤數量，YouTube 建議 5-15 個相關標籤")
        
        # YouTube 特定建議
        if not is_shorts and not self._has_timestamps(adapted_description):
            metadata["recommendations"].append("在描述中添加時間戳，幫助觀眾導航長影片，提高參與度")
        
        if not self._has_call_to_action(adapted_description):
            metadata["recommendations"].append("添加明確的號召性用語（如訂閱、點贊、評論）以提高參與度")
        
        if not self._has_links(adapted_description):
            metadata["recommendations"].append("在描述中添加相關鏈接（社交媒體、網站等）以提高跨平台參與")
        
        return {
            "success": True,
            "content": adapted_content.dict(),
            "metadata": metadata
        }
    
    def adapt_to_description(self, content_item: ContentItem) -> Dict[str, Any]:
        """
        將文本內容適配為 YouTube 影片描述。
        
        Args:
            content_item: 包含文本內容的內容項目
            
        Returns:
            適配為影片描述的內容
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
        
        # 適配描述
        adapted_description = self._adapt_description(original_text)
        
        # 提取標籤
        tags = self._extract_tags(adapted_description, "")
        
        # 創建新的影片內容項目
        adapted_content = content_item.copy(deep=True)
        adapted_content.content_type = ContentType.VIDEO
        
        # 建立影片內容
        if not adapted_content.video_content:
            # 從文本創建合適的標題
            title = self._generate_title_from_text(original_text)
            
            adapted_content.video_content = VideoContent(
                title=title,
                description=adapted_description,
                script="[需要提供影片腳本]"
            )
        else:
            adapted_content.video_content.description = adapted_description
        
        # 添加元數據
        metadata = {
            "platform": "youtube",
            "content_type": "video_description",
            "original_type": "text",
            "description_length": len(adapted_description),
            "description_seo_optimized": self._is_description_seo_optimized(adapted_description),
            "tags_count": len(tags),
            "has_timestamps": self._has_timestamps(adapted_description),
            "has_call_to_action": self._has_call_to_action(adapted_description),
            "has_links": self._has_links(adapted_description),
            "note": "文本內容已轉換為影片描述，但還需要提供實際影片和標題",
            "recommendations": []
        }
        
        # 添加建議
        if len(adapted_description) < self.MIN_DESCRIPTION_LENGTH:
            metadata["recommendations"].append(f"描述過短，YouTube 建議至少 {self.MIN_DESCRIPTION_LENGTH} 字元以提高 SEO")
        
        if not self._is_description_seo_optimized(adapted_description):
            metadata["recommendations"].append("改進描述 SEO：添加關鍵詞並放在開頭，使描述前兩行具有吸引力")
        
        if not self._has_timestamps(adapted_description):
            metadata["recommendations"].append("添加時間戳，幫助觀眾導航影片內容")
        
        if not self._has_call_to_action(adapted_description):
            metadata["recommendations"].append("添加明確的號召性用語（如訂閱、點贊、評論）以提高參與度")
        
        if not self._has_links(adapted_description):
            metadata["recommendations"].append("添加相關鏈接（社交媒體、網站等）以提高跨平台參與")
        
        return {
            "success": True,
            "content": adapted_content.dict(),
            "metadata": metadata
        }
    
    def adapt_to_thumbnail(self, content_item: ContentItem) -> Dict[str, Any]:
        """
        將圖像內容適配為 YouTube 縮略圖。
        
        Args:
            content_item: 包含圖像內容的內容項目
            
        Returns:
            適配為縮略圖的內容
        """
        if not content_item.image_content:
            logger.error("內容項目缺少圖像內容")
            return {
                "success": False,
                "error": "缺少圖像內容",
                "content": content_item.dict()
            }
        
        # 創建新的影片內容項目
        adapted_content = content_item.copy(deep=True)
        adapted_content.content_type = ContentType.VIDEO
        
        # 取得圖像 URL 或提示詞
        image_url = content_item.image_content.image_url
        image_prompt = content_item.image_content.prompt
        
        # 從圖像說明中提取可能的標題
        caption = content_item.image_content.caption or ""
        title = self._generate_title_from_text(caption) if caption else "影片標題"
        
        # 建立影片內容
        if not adapted_content.video_content:
            adapted_content.video_content = VideoContent(
                title=title,
                description="[需要提供影片描述]",
                script="[需要提供影片腳本]"
            )
        
        # 設置縮略圖信息
        if image_url:
            # 如果有 URL，檢查格式
            is_valid_format, format_message = self._check_thumbnail_format(image_url)
            if is_valid_format:
                adapted_content.video_content.thumbnail_url = image_url
            else:
                # 如果格式不支持，使用提示詞創建新縮略圖
                adapted_content.video_content.thumbnail_prompt = f"YouTube 縮略圖: {image_prompt or '高品質 YouTube 影片縮略圖'}"
        else:
            # 使用提示詞
            adapted_content.video_content.thumbnail_prompt = image_prompt or "高品質 YouTube 影片縮略圖"
        
        # 添加元數據
        metadata = {
            "platform": "youtube",
            "content_type": "thumbnail",
            "original_type": "image",
            "has_image_url": bool(image_url),
            "has_prompt": bool(image_prompt),
            "note": "圖像已設置為影片縮略圖，但還需要提供實際影片、標題和描述",
            "recommendations": []
        }
        
        # 添加建議
        metadata["recommendations"].append("YouTube 縮略圖尺寸應為 1280x720 像素 (16:9)")
        metadata["recommendations"].append("縮略圖應使用鮮明的顏色，包含清晰的文字和引人注目的圖像")
        metadata["recommendations"].append("文字應控制在 1-3 個簡短詞語，避免太多文字")
        metadata["recommendations"].append("縮略圖應與標題相互補充，而不是重複相同信息")
        
        return {
            "success": True,
            "content": adapted_content.dict(),
            "metadata": metadata
        }
    
    def _adapt_title(self, title: str) -> str:
        """
        適配 YouTube 標題。
        
        Args:
            title: 原始標題
            
        Returns:
            適配後的標題
        """
        if not title:
            return "需要提供影片標題"
        
        # 確保標題在限制範圍內
        if len(title) > self.MAX_TITLE_LENGTH:
            logger.warning(f"標題超出 YouTube 最大長度 ({len(title)} > {self.MAX_TITLE_LENGTH})，將進行裁剪")
            title = self._truncate_text(title, self.MAX_TITLE_LENGTH)
        
        # 如果標題太短或太通用，給出警告
        if len(title) < 5:
            logger.warning("標題過短，可能影響 SEO 表現")
        
        # 確保標題首字母大寫（適用於英文標題）
        if re.match(r'^[a-z]', title):
            title = title[0].upper() + title[1:]
        
        return title
    
    def _adapt_description(self, description: str) -> str:
        """
        適配 YouTube 描述。
        
        Args:
            description: 原始描述
            
        Returns:
            適配後的描述
        """
        if not description:
            return ""
        
        # 確保描述在限制範圍內
        if len(description) > self.MAX_DESCRIPTION_LENGTH:
            logger.warning(f"描述超出 YouTube 最大長度 ({len(description)} > {self.MAX_DESCRIPTION_LENGTH})，將進行裁剪")
            description = self._truncate_text(description, self.MAX_DESCRIPTION_LENGTH)
        
        # 如果描述不包含常見元素，進行提示
        has_timestamps = self._has_timestamps(description)
        has_links = self._has_links(description)
        has_call_to_action = self._has_call_to_action(description)
        
        if not has_timestamps and not has_links and not has_call_to_action:
            logger.info("描述缺少重要元素（時間戳、鏈接、號召性用語），可以提升 SEO 和參與度")
        
        return description
    
    def _extract_tags(self, text: str, title: str) -> List[str]:
        """
        從文本和標題中提取 YouTube 標籤。
        
        Args:
            text: 文本內容
            title: 標題
            
        Returns:
            標籤列表
        """
        tags = []
        
        # 從標題中提取可能的關鍵詞
        if title:
            # 移除標點符號，分割為單詞
            title_words = re.sub(r'[^\w\s]', ' ', title).split()
            # 過濾長度大於 3 的單詞
            title_tags = [word.lower() for word in title_words if len(word) > 3]
            tags.extend(title_tags[:3])  # 最多使用前 3 個關鍵詞
        
        # 從文本中提取主題標籤（# 開頭）
        hashtag_pattern = r'#(\w+)'
        hashtags = re.findall(hashtag_pattern, text)
        if hashtags:
            tags.extend(hashtags)
        
        # 查找文本中的關鍵詞短語
        # 簡單的啟發式方法：查找帶有引號或加粗的文本
        quote_pattern = r'"([^"]+)"'
        bold_pattern = r'\*\*([^*]+)\*\*'
        
        quotes = re.findall(quote_pattern, text)
        bolds = re.findall(bold_pattern, text)
        
        # 添加找到的短語（如果它們不太長）
        for phrase in quotes + bolds:
            if 2 < len(phrase.split()) < 5 and len(phrase) < self.MAX_TAG_LENGTH:
                tags.append(phrase.lower())
        
        # 去重並限制標籤數量
        unique_tags = []
        total_length = 0
        
        for tag in tags:
            if tag not in unique_tags:
                # 確保每個標籤不超過字符限制
                if len(tag) <= self.MAX_TAG_LENGTH:
                    # 確保所有標籤的總長度不超過限制
                    if total_length + len(tag) + 1 <= self.MAX_TAGS:  # +1 表示分隔符
                        unique_tags.append(tag)
                        total_length += len(tag) + 1
        
        return unique_tags
    
    def _is_title_seo_optimized(self, title: str) -> bool:
        """
        檢查標題是否針對 SEO 進行了優化。
        
        Args:
            title: 標題
            
        Returns:
            是否已優化
        """
        if not title:
            return False
        
        # 檢查長度是否在理想範圍內
        if not (20 <= len(title) <= self.IDEAL_TITLE_LENGTH):
            return False
        
        # 檢查是否包含數字（數字在標題中效果好）
        if not re.search(r'\d', title):
            return False
        
        # 檢查是否使用引人注目的詞語
        attention_words = ['how', 'why', 'what', 'best', 'top', 'guide', 'tutorial', 
                         'review', 'tips', 'secrets', 'ultimate', 'complete']
        
        has_attention_word = any(word in title.lower() for word in attention_words)
        
        # 返回整體評估
        return has_attention_word
    
    def _is_description_seo_optimized(self, description: str) -> bool:
        """
        檢查描述是否針對 SEO 進行了優化。
        
        Args:
            description: 描述
            
        Returns:
            是否已優化
        """
        if not description:
            return False
        
        # 檢查長度是否足夠
        if len(description) < self.MIN_DESCRIPTION_LENGTH:
            return False
        
        # 檢查是否重複使用標題中的關鍵詞
        # 需要額外的標題參數，此處簡化實現
        
        # 檢查是否在前兩行包含核心信息
        first_lines = description.split('\n')[:2]
        first_lines_text = ' '.join(first_lines)
        
        if len(first_lines_text) < 50:
            return False
        
        # 檢查是否包含其他元素
        has_other_elements = (
            self._has_timestamps(description) or
            self._has_links(description) or
            self._has_call_to_action(description)
        )
        
        return has_other_elements
    
    def _has_timestamps(self, text: str) -> bool:
        """
        檢查文本是否包含時間戳。
        
        Args:
            text: 文本
            
        Returns:
            是否包含時間戳
        """
        # YouTube 時間戳格式：mm:ss 或 hh:mm:ss
        timestamp_pattern = r'\b(\d+:\d+(?::\d+)?)\b'
        timestamps = re.findall(timestamp_pattern, text)
        
        return len(timestamps) >= 2  # 至少需要兩個時間戳才有意義
    
    def _has_links(self, text: str) -> bool:
        """
        檢查文本是否包含鏈接。
        
        Args:
            text: 文本
            
        Returns:
            是否包含鏈接
        """
        # 簡單的 URL 檢測
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, text)
        
        return len(urls) > 0
    
    def _has_call_to_action(self, text: str) -> bool:
        """
        檢查文本是否包含號召性用語。
        
        Args:
            text: 文本
            
        Returns:
            是否包含號召性用語
        """
        cta_phrases = [
            'subscribe', 'like', 'comment', 'share', 'click', 
            'join', 'follow', 'check out', 'visit', 'download',
            '訂閱', '點贊', '評論', '分享', '點擊', 
            '加入', '關注', '查看', '訪問', '下載'
        ]
        
        lower_text = text.lower()
        
        return any(phrase in lower_text for phrase in cta_phrases)
    
    def _check_thumbnail_format(self, image_url: str) -> Tuple[bool, str]:
        """
        檢查縮略圖格式是否適合 YouTube。
        
        Args:
            image_url: 圖像 URL
            
        Returns:
            (格式是否有效, 消息)
        """
        if not image_url:
            return False, "缺少圖像 URL"
        
        # YouTube 支持的縮略圖格式：JPG, PNG, GIF, BMP
        allowed_formats = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]
        
        # 檢查文件擴展名
        lower_url = image_url.lower()
        valid_format = any(lower_url.endswith(fmt) for fmt in allowed_formats)
        
        if not valid_format:
            return False, f"圖像格式可能不受支持，YouTube 支持: {', '.join(allowed_formats)}"
        
        # YouTube 縮略圖推薦尺寸：1280x720 (16:9)
        # 此處無法檢查尺寸，返回建議
        return True, "圖像格式有效，確保尺寸為 1280x720 (16:9)"
    
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
        
        # 尋找最後一個完整句子的位置
        truncated = text[:max_length]
        last_sentence = max(
            truncated.rfind(". "),
            truncated.rfind("! "),
            truncated.rfind("? ")
        )
        
        if last_sentence > max_length * 0.7:  # 確保不會截斷得太短
            truncated = truncated[:last_sentence + 1]
            return truncated.strip()
        
        # 如果找不到合適的句子斷點，尋找最後一個完整單詞
        last_space = truncated.rfind(' ')
        
        if last_space > 0:
            truncated = truncated[:last_space]
        
        # 添加省略號
        return truncated.strip() + "..."
    
    def _generate_title_from_text(self, text: str) -> str:
        """
        從文本生成合適的 YouTube 標題。
        
        Args:
            text: 原始文本
            
        Returns:
            生成的標題
        """
        if not text:
            return "YouTube 影片"
        
        # 使用第一句作為標題基礎
        first_sentence = text.split('.')[0].strip()
        
        # 如果第一句太長，取前幾個詞
        words = first_sentence.split()
        if len(words) > 10:
            first_sentence = ' '.join(words[:10]) + "..."
        
        # 確保標題長度合適
        if len(first_sentence) > self.IDEAL_TITLE_LENGTH:
            first_sentence = self._truncate_text(first_sentence, self.IDEAL_TITLE_LENGTH)
        
        # 確保首字母大寫（適用於英文標題）
        if first_sentence and re.match(r'^[a-z]', first_sentence):
            first_sentence = first_sentence[0].upper() + first_sentence[1:]
        
        return first_sentence
    
    def get_optimal_video_settings(self) -> Dict[str, Any]:
        """
        獲取 YouTube 最佳影片設置。
        
        Returns:
            最佳影片設置
        """
        return {
            "title": {
                "max_length": self.MAX_TITLE_LENGTH,
                "ideal_length": self.IDEAL_TITLE_LENGTH
            },
            "description": {
                "max_length": self.MAX_DESCRIPTION_LENGTH,
                "min_length": self.MIN_DESCRIPTION_LENGTH,
                "optimal_length": self.OPTIMAL_DESCRIPTION_LENGTH
            },
            "tags": {
                "max_total_chars": self.MAX_TAGS,
                "optimal_count": self.OPTIMAL_TAGS_COUNT,
                "max_tag_length": self.MAX_TAG_LENGTH
            },
            "video": {
                "min_length_seconds": self.MIN_VIDEO_LENGTH_SECONDS,
                "ideal_length_seconds": self.IDEAL_VIDEO_LENGTH_SECONDS,
                "max_shorts_length": self.MAX_SHORTS_LENGTH_SECONDS,
                "max_file_size_gb": self.MAX_FILE_SIZE_GB
            },
            "thumbnail": {
                "width": 1280,
                "height": 720,
                "ratio": "16:9",
                "formats": ["JPG", "PNG", "GIF", "BMP"]
            }
        }


# 全局 YouTube 適配器實例
youtube_adapter = YouTubeAdapter()
