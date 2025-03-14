#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Platform adapter for optimizing content for different social media platforms.
"""

from marketgenius.utils.logger import get_logger
from marketgenius.platforms.instagram import InstagramAdapter
from marketgenius.platforms.facebook import FacebookAdapter
from marketgenius.platforms.linkedin import LinkedInAdapter
from marketgenius.platforms.youtube import YouTubeAdapter

logger = get_logger(__name__)


class PlatformAdapter:
    """Adapter for optimizing content for different social media platforms."""
    
    def __init__(self):
        """Initialize the platform adapter with platform-specific adapters."""
        self.adapters = {
            "instagram": InstagramAdapter(),
            "facebook": FacebookAdapter(),
            "linkedin": LinkedInAdapter(),
            "youtube": YouTubeAdapter()
        }
    
    def adapt_content(self, content, platform, business_info=None):
        """
        Adapt content for a specific platform.
        
        Args:
            content: Raw content dictionary
            platform: Target platform (instagram, facebook, linkedin, youtube)
            business_info: Optional business information for customization
            
        Returns:
            Platform-optimized content
        """
        platform = platform.lower()
        
        if platform not in self.adapters:
            logger.warning(f"No adapter available for platform: {platform}. Using generic adaptation.")
            return self._generic_adapt(content, platform)
        
        logger.info(f"Adapting content for platform: {platform}")
        return self.adapters[platform].adapt(content, business_info)
    
    def _generic_adapt(self, content, platform):
        """
        Generic content adaptation when a specific adapter is not available.
        
        Args:
            content: Raw content dictionary
            platform: Target platform name
            
        Returns:
            Minimally adapted content
        """
        # Create a copy to avoid modifying the original
        adapted = content.copy()
        
        # Add platform indicator
        adapted["platform"] = platform
        
        # Add generic platform notice
        if "notes" not in adapted:
            adapted["notes"] = ""
        adapted["notes"] += f"\nThis content has been generically adapted for {platform}."
        
        return adapted