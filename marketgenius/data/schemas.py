#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MarketGenius 數據模式定義。
定義系統中使用的所有數據結構和驗證規則。
"""

import datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, validator, HttpUrl


class Platform(str, Enum):
    """支持的社交媒體平台。"""
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    TIKTOK = "tiktok"


class ContentType(str, Enum):
    """內容類型枚舉。"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    CAROUSEL = "carousel"
    STORY = "story"
    REEL = "reel"


class ContentTone(str, Enum):
    """內容語調枚舉。"""
    FORMAL = "formal"
    CASUAL = "casual"
    HUMOROUS = "humorous"
    INFORMATIVE = "informative"
    INSPIRATIONAL = "inspirational"
    PROMOTIONAL = "promotional"
    EDUCATIONAL = "educational"


class BrandStyleAttribute(BaseModel):
    """品牌風格屬性。"""
    name: str
    value: float = Field(..., ge=0.0, le=1.0)
    description: Optional[str] = None


class BrandColors(BaseModel):
    """品牌顏色方案。"""
    primary: str = Field(..., regex=r'^#[0-9A-Fa-f]{6}$')
    secondary: Optional[str] = Field(None, regex=r'^#[0-9A-Fa-f]{6}$')
    accent: Optional[List[str]] = None
    background: Optional[str] = Field(None, regex=r'^#[0-9A-Fa-f]{6}$')
    text: Optional[str] = Field(None, regex=r'^#[0-9A-Fa-f]{6}$')


class BrandModel(BaseModel):
    """品牌模型。"""
    id: str
    name: str
    description: Optional[str] = None
    industry: Optional[str] = None
    target_audience: Optional[List[str]] = None
    keywords: List[str] = Field(default_factory=list)
    style_attributes: List[BrandStyleAttribute] = Field(default_factory=list)
    colors: Optional[BrandColors] = None
    fonts: Optional[Dict[str, str]] = None
    logo_url: Optional[str] = None
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    
    @validator('updated_at', always=True)
    def set_updated_at(cls, v, values):
        """更新時間自動設置為當前時間。"""
        return datetime.datetime.now()


class ContentRequest(BaseModel):
    """內容生成請求。"""
    brand_id: str
    platform: Platform
    content_type: ContentType
    topic: str
    target_audience: Optional[List[str]] = None
    tone: Optional[ContentTone] = None
    keywords: Optional[List[str]] = None
    length: Optional[int] = None
    include_hashtags: bool = False
    include_emoji: bool = False
    include_call_to_action: bool = False
    additional_instructions: Optional[str] = None
    reference_urls: Optional[List[str]] = None


class TextContent(BaseModel):
    """文本內容。"""
    text: str
    hashtags: Optional[List[str]] = None
    mentions: Optional[List[str]] = None


class ImageContent(BaseModel):
    """圖像內容。"""
    prompt: str
    image_url: Optional[str] = None
    alt_text: Optional[str] = None
    caption: Optional[str] = None


class VideoContent(BaseModel):
    """視頻內容。"""
    title: str
    script: str
    description: Optional[str] = None
    thumbnail_prompt: Optional[str] = None
    duration_seconds: Optional[int] = None
    video_url: Optional[str] = None


class ContentItem(BaseModel):
    """內容項目。"""
    id: str = Field(..., description="唯一識別符")
    brand_id: str
    platform: Platform
    content_type: ContentType
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    text_content: Optional[TextContent] = None
    image_content: Optional[ImageContent] = None
    video_content: Optional[VideoContent] = None
    raw_request: Optional[Dict[str, Any]] = None
    
    @validator('content_type', 'text_content', 'image_content', 'video_content')
    def validate_content_consistency(cls, v, values, **kwargs):
        """驗證內容類型與內容數據一致性。"""
        content_type = values.get('content_type')
        
        if content_type == ContentType.TEXT and 'text_content' not in values:
            raise ValueError("文本內容類型必須提供 text_content")
        
        if content_type == ContentType.IMAGE and 'image_content' not in values:
            raise ValueError("圖像內容類型必須提供 image_content")
        
        if content_type == ContentType.VIDEO and 'video_content' not in values:
            raise ValueError("視頻內容類型必須提供 video_content")
        
        return v


class MetricsData(BaseModel):
    """指標數據。"""
    views: Optional[int] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    shares: Optional[int] = None
    clicks: Optional[int] = None
    impressions: Optional[int] = None
    engagement_rate: Optional[float] = None
    reach: Optional[int] = None
    saved: Optional[int] = None
    video_views: Optional[int] = None
    play_rate: Optional[float] = None
    watch_time_seconds: Optional[int] = None
    custom_metrics: Optional[Dict[str, Any]] = None


class ContentPerformance(BaseModel):
    """內容表現。"""
    content_id: str
    platform: Platform
    post_url: Optional[str] = None
    published_at: Optional[datetime.datetime] = None
    metrics: MetricsData = Field(default_factory=MetricsData)
    raw_metrics: Optional[Dict[str, Any]] = None
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)


class OptimizationSuggestion(BaseModel):
    """優化建議。"""
    content_id: str
    suggestion_type: str
    suggestion: str
    importance: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)


class AnalyticsReport(BaseModel):
    """分析報告。"""
    id: str
    brand_id: str
    title: str
    description: Optional[str] = None
    date_range: Dict[str, datetime.datetime]
    platforms: List[Platform]
    content_ids: List[str]
    performance_summary: Dict[str, Any]
    top_performing_content: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    charts_data: Optional[Dict[str, Any]] = None
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
