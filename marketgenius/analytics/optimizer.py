#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Content optimizer for suggesting improvements to marketing content.
"""

from marketgenius.utils.logger import get_logger

logger = get_logger(__name__)


class ContentOptimizer:
    """Optimizer for suggesting improvements to marketing content."""
    
    def __init__(self, config=None):
        """
        Initialize the content optimizer.
        
        Args:
            config: Configuration dictionary for the optimizer
        """
        self.config = config or {}
        self.optimization_rules = self._load_optimization_rules()
    
    def _load_optimization_rules(self):
        """Load optimization rules for different platforms and content types."""
        # In a real implementation, these would be more sophisticated rules
        # possibly loaded from a database or configuration file
        return {
            "instagram": {
                "post": [
                    "Keep captions under 125 words for optimal engagement",
                    "Include 5-10 relevant hashtags",
                    "Ask a question to encourage comments",
                    "Include a clear call-to-action",
                    "Use emojis to increase engagement",
                    "Front-load important information"
                ],
                "story": [
                    "Keep text minimal and readable",
                    "Include interactive elements (polls, questions)",
                    "Use full screen imagery",
                    "Include a clear call-to-action",
                    "Maintain brand colors and fonts"
                ],
                "carousel": [
                    "Use first slide to hook viewers",
                    "Maintain consistent design across slides",
                    "Limit to 5-7 slides for optimal engagement",
                    "Include a strong CTA in the last slide",
                    "Number slides to indicate progression"
                ]
            },
            "facebook": {
                "post": [
                    "Keep text under 40-80 words for optimal engagement",
                    "Include a high-quality image or video",
                    "Ask questions to encourage comments",
                    "Include a clear call-to-action",
                    "Time posts according to audience activity"
                ],
                "video": [
                    "Front-load key information in the first 3 seconds",
                    "Design for silent viewing (captions/text overlays)",
                    "Keep videos under 2 minutes for best completion rates",
                    "Include a clear call-to-action",
                    "Use square or vertical format for mobile viewers"
                ]
            },
            "linkedin": {
                "post": [
                    "Keep text under 1300 characters",
                    "Use line breaks for readability",
                    "Include no more than 3 hashtags",
                    "Ask thoughtful questions to encourage comments",
                    "Share industry insights and professional knowledge"
                ],
                "article": [
                    "Keep titles under 50 characters",
                    "Include a compelling featured image",
                    "Structure content with clear headings",
                    "Include 5-8 relevant tags",
                    "End with a question or call-to-action"
                ]
            }
        }
    
    def generate_suggestions(self, content, platform, content_type, performance_data=None):
        """
        Generate optimization suggestions for content.
        
        Args:
            content: The content to optimize
            platform: Platform the content is for
            content_type: Type of content
            performance_data: Optional performance data to inform suggestions
            
        Returns:
            List of optimization suggestions
        """
        logger.info(f"Generating suggestions for {platform} {content_type}")
        
        suggestions = []
        
        # Get platform and content type specific rules
        platform_rules = self.optimization_rules.get(platform, {})
        content_rules = platform_rules.get(content_type, [])
        
        # Check content against rules
        if platform == "instagram":
            suggestions.extend(self._check_instagram_content(content, content_type, content_rules))
        elif platform == "facebook":
            suggestions.extend(self._check_facebook_content(content, content_type, content_rules))
        elif platform == "linkedin":
            suggestions.extend(self._check_linkedin_content(content, content_type, content_rules))
        
        # Add performance-based suggestions if data is available
        if performance_data:
            suggestions.extend(self._generate_performance_based_suggestions(performance_data, platform))
        
        # Add general suggestions that apply to all content
        suggestions.extend(self._generate_general_suggestions(content))
        
        return {
            "platform": platform,
            "content_type": content_type,
            "suggestions": suggestions,
            "priority_suggestions": suggestions[:3] if len(suggestions) > 3 else suggestions
        }
    
    def _check_instagram_content(self, content, content_type, rules):
        """Check Instagram content against optimization rules."""
        suggestions = []
        text = content.get("caption", "")
        hashtags = content.get("hashtags", [])
        
        # Check caption length
        word_count = len(text.split())
        if content_type == "post" and word_count > 125:
            suggestions.append({
                "issue": "Caption length",
                "suggestion": f"Consider shortening your caption from {word_count} words to under 125 words for optimal engagement",
                "priority": "medium"
            })
        
        # Check hashtag count
        hashtag_count = len(hashtags)
        if content_type == "post" and (hashtag_count < 5 or hashtag_count > 30):
            if hashtag_count < 5:
                suggestions.append({
                    "issue": "Hashtag usage",
                    "suggestion": f"Consider adding more relevant hashtags (currently using {hashtag_count}, optimal is 5-30)",
                    "priority": "medium"
                })
            elif hashtag_count > 30:
                suggestions.append({
                    "issue": "Hashtag usage",
                    "suggestion": f"Instagram limits posts to 30 hashtags, you're using {hashtag_count}",
                    "priority": "high"
                })
        
        # Check for questions to encourage engagement
        if "?" not in text and content_type == "post":
            suggestions.append({
                "issue": "Engagement prompt",
                "suggestion": "Consider adding a question to encourage comments and engagement",
                "priority": "low"
            })
        
        # Check for call-to-action
        cta_phrases = ["click", "tap", "swipe", "share", "comment", "follow", "check out", "learn more", "sign up", "buy"]
        has_cta = any(phrase in text.lower() for phrase in cta_phrases)
        if not has_cta:
            suggestions.append({
                "issue": "Call-to-action",
                "suggestion": "Include a clear call-to-action to drive desired user behavior",
                "priority": "high"
            })
        
        return suggestions
    
    def _check_facebook_content(self, content, content_type, rules):
        """Check Facebook content against optimization rules."""
        suggestions = []
        text = content.get("post_text", "")
        media = content.get("media", [])
        
        # Check text length
        word_count = len(text.split())
        if content_type == "post" and word_count > 80:
            suggestions.append({
                "issue": "Post length",
                "suggestion": f"Consider shortening your post from {word_count} words to 40-80 words for optimal engagement",
                "priority": "medium"
            })
        
        # Check for media
        if content_type == "post" and not media:
            suggestions.append({
                "issue": "Visual content",
                "suggestion": "Posts with images or videos get significantly higher engagement. Consider adding visual content.",
                "priority": "high"
            })
        
        # Check for questions to encourage engagement
        if "?" not in text and content_type == "post":
            suggestions.append({
                "issue": "Engagement prompt",
                "suggestion": "Consider adding a question to encourage comments and engagement",
                "priority": "low"
            })
        
        # Check for call-to-action
        cta_phrases = ["click", "like", "share", "comment", "learn more", "sign up", "shop now", "contact us"]
        has_cta = any(phrase in text.lower() for phrase in cta_phrases)
        if not has_cta:
            suggestions.append({
                "issue": "Call-to-action",
                "suggestion": "Include a clear call-to-action to drive desired user behavior",
                "priority": "high"
            })
        
        return suggestions
    
    def _check_linkedin_content(self, content, content_type, rules):
        """Check LinkedIn content against optimization rules."""
        suggestions = []
        text = content.get("post_text", "")
        hashtags = content.get("hashtags", [])
        
        # Check text length for posts
        char_count = len(text)
        if content_type == "post" and char_count > 1300:
            suggestions.append({
                "issue": "Post length",
                "suggestion": f"Your post is {char_count} characters. LinkedIn shows only the first 1300 characters before adding 'see more'",
                "priority": "medium"
            })
        
        # Check hashtag count
        hashtag_count = len(hashtags)
        if content_type == "post" and hashtag_count > 3:
            suggestions.append({
                "issue": "Hashtag usage",
                "suggestion": f"LinkedIn best practices suggest using no more than 3 relevant hashtags (you're using {hashtag_count})",
                "priority": "low"
            })
        
        # Check for line breaks
        if content_type == "post" and text.count("\n") < 3 and len(text) > 200:
            suggestions.append({
                "issue": "Readability",
                "suggestion": "Consider adding more line breaks to improve readability on mobile devices",
                "priority": "medium"
            })
        
        # Check for professional tone
        casual_phrases = ["hey guys", "what's up", "omg", "lol", "wtf", "btw"]
        has_casual_tone = any(phrase in text.lower() for phrase in casual_phrases)
        if has_casual_tone:
            suggestions.append({
                "issue": "Professional tone",
                "suggestion": "Consider using a more professional tone for LinkedIn content",
                "priority": "high"
            })
        
        return suggestions
    
    def _generate_performance_based_suggestions(self, performance_data, platform):
        """Generate suggestions based on content performance data."""
        suggestions = []
        
        # Check engagement rate
        engagement_rate = performance_data.get("engagement_rate", 0)
        platform_benchmarks = {
            "instagram": 0.03,
            "facebook": 0.015,
            "linkedin": 0.04
        }
        benchmark = platform_benchmarks.get(platform, 0.03)
        
        if engagement_rate < benchmark * 0.5:
            suggestions.append({
                "issue": "Low engagement",
                "suggestion": "Your engagement rate is significantly below average. Consider testing different content formats or posting times.",
                "priority": "high"
            })
        
        # Check comment rate
        comment_rate = performance_data.get("comment_rate", 0)
        comment_benchmarks = {
            "instagram": 0.01,
            "facebook": 0.005,
            "linkedin": 0.01
        }
        comment_benchmark = comment_benchmarks.get(platform, 0.01)
        
        if comment_rate < comment_benchmark * 0.5:
            suggestions.append({
                "issue": "Low comments",
                "suggestion": "Your content isn't generating many comments. Try including questions or controversial statements to spark discussion.",
                "priority": "medium"
            })
        
        # Check optimal posting time
        post_time = performance_data.get("post_time")
        if post_time:
            hour = int(post_time.split(":")[0])
            if platform == "instagram" and (hour < 11 or hour > 20):
                suggestions.append({
                    "issue": "Posting time",
                    "suggestion": "For Instagram, the optimal posting times are typically between 11am and 8pm. Consider adjusting your posting schedule.",
                    "priority": "low"
                })
            elif platform == "facebook" and (hour < 13 or hour > 16):
                suggestions.append({
                    "issue": "Posting time",
                    "suggestion": "For Facebook, the optimal posting times are typically between 1pm and 4pm. Consider adjusting your posting schedule.",
                    "priority": "low"
                })
            elif platform == "linkedin" and (hour < 8 or hour > 14) and hour != 17:
                suggestions.append({
                    "issue": "Posting time",
                    "suggestion": "For LinkedIn, the optimal posting times are typically between 8am-2pm and around 5pm. Consider adjusting your posting schedule.",
                    "priority": "low"
                })
        
        return suggestions
    
    def _generate_general_suggestions(self, content):
        """Generate general content suggestions that apply across platforms."""
        suggestions = []
        text = content.get("caption", content.get("post_text", ""))
        
        # Check for emoji usage
        if not any(char in text for char in "😀🙂😍👍🎉"):
            suggestions.append({
                "issue": "Emoji usage",
                "suggestion": "Consider adding relevant emojis to increase engagement and convey emotion",
                "priority": "low"
            })
        
        # Check for long paragraphs
        paragraphs = text.split("\n\n")
        for i, paragraph in enumerate(paragraphs):
            if len(paragraph.split()) > 40:
                suggestions.append({
                    "issue": "Paragraph length",
                    "suggestion": f"Paragraph {i+1} is quite long. Consider breaking it into smaller chunks for better readability.",
                    "priority": "low"
                })
        
        return suggestions
    
    def optimize_content(self, content, platform, content_type):
        """
        Automatically optimize content based on best practices.
        
        Args:
            content: The content to optimize
            platform: Platform the content is for
            content_type: Type of content
            
        Returns:
            Optimized content
        """
        logger.info(f"Optimizing content for {platform} {content_type}")
        
        # In a real implementation, this would use LLM to actually modify content
        # For now, we'll just return original content with optimization notes
        
        # Get suggestions
        suggestions_result = self.generate_suggestions(content, platform, content_type)
        suggestions = suggestions_result.get("suggestions", [])
        
        # Create optimization notes
        optimization_notes = []
        for suggestion in suggestions:
            optimization_notes.append(f"- {suggestion['issue']}: {suggestion['suggestion']}")
        
        optimization_notes_text = "\n".join(optimization_notes)
        
        # Return original content with notes
        optimized_content = dict(content)
        optimized_content["optimization_notes"] = optimization_notes_text
        optimized_content["optimization_count"] = len(suggestions)
        
        return optimized_content