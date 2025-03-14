#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Metrics analyzer for evaluating marketing content performance.
"""

import numpy as np
from datetime import datetime, timedelta
from marketgenius.utils.logger import get_logger

logger = get_logger(__name__)


class EngagementAnalyzer:
    """Analyzer for measuring and evaluating engagement metrics."""
    
    def __init__(self, config=None):
        """
        Initialize the engagement analyzer.
        
        Args:
            config: Configuration dictionary for the analyzer
        """
        self.config = config or {}
        self.benchmarks = self._load_benchmarks()
    
    def _load_benchmarks(self):
        """Load industry benchmark data for comparison."""
        # In a real implementation, this would load actual benchmark data
        # For now, we'll use placeholder values
        return {
            "instagram": {
                "engagement_rate": {
                    "low": 0.01,
                    "average": 0.03,
                    "high": 0.06
                },
                "comment_rate": {
                    "low": 0.002,
                    "average": 0.01,
                    "high": 0.02
                },
                "share_rate": {
                    "low": 0.001,
                    "average": 0.005,
                    "high": 0.015
                }
            },
            "facebook": {
                "engagement_rate": {
                    "low": 0.005,
                    "average": 0.015,
                    "high": 0.04
                },
                "comment_rate": {
                    "low": 0.001,
                    "average": 0.005,
                    "high": 0.015
                },
                "share_rate": {
                    "low": 0.002,
                    "average": 0.01,
                    "high": 0.025
                }
            },
            "linkedin": {
                "engagement_rate": {
                    "low": 0.02,
                    "average": 0.04,
                    "high": 0.08
                },
                "comment_rate": {
                    "low": 0.005,
                    "average": 0.01,
                    "high": 0.025
                },
                "share_rate": {
                    "low": 0.003,
                    "average": 0.008,
                    "high": 0.02
                }
            }
        }
    
    def analyze_metrics(self, metrics_data, platform, content_type=None, historical_data=None):
        """
        Analyze engagement metrics for content.
        
        Args:
            metrics_data: Dictionary with engagement metrics
            platform: The platform the content was published on
            content_type: Type of content (post, story, etc.)
            historical_data: Previous metrics for comparison
            
        Returns:
            Analysis results
        """
        logger.info(f"Analyzing metrics for {platform} content")
        
        try:
            # Calculate key performance indicators
            kpis = self._calculate_kpis(metrics_data)
            
            # Compare with benchmarks
            benchmark_comparison = self._compare_with_benchmarks(kpis, platform)
            
            # Compare with historical data if available
            historical_comparison = None
            if historical_data:
                historical_comparison = self._compare_with_historical(kpis, historical_data)
            
            # Calculate overall performance score
            performance_score = self._calculate_performance_score(kpis, benchmark_comparison)
            
            analysis_results = {
                "timestamp": datetime.now().isoformat(),
                "platform": platform,
                "content_type": content_type,
                "kpis": kpis,
                "benchmark_comparison": benchmark_comparison,
                "historical_comparison": historical_comparison,
                "performance_score": performance_score
            }
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error analyzing metrics: {e}")
            return {
                "error": f"Failed to analyze metrics: {str(e)}",
                "platform": platform,
                "content_type": content_type
            }
    
    def _calculate_kpis(self, metrics_data):
        """Calculate key performance indicators from raw metrics data."""
        # Extract metrics with fallbacks to zero for missing values
        impressions = metrics_data.get("impressions", 0)
        reach = metrics_data.get("reach", 0)
        likes = metrics_data.get("likes", 0)
        comments = metrics_data.get("comments", 0)
        shares = metrics_data.get("shares", 0)
        saves = metrics_data.get("saves", 0)
        clicks = metrics_data.get("clicks", 0)
        
        # Avoid division by zero
        if impressions == 0:
            return {
                "engagement_rate": 0,
                "comment_rate": 0,
                "share_rate": 0,
                "click_through_rate": 0,
                "save_rate": 0,
                "total_engagements": 0
            }
        
        # Calculate KPIs
        total_engagements = likes + comments + shares + saves + clicks
        engagement_rate = total_engagements / impressions
        comment_rate = comments / impressions
        share_rate = shares / impressions
        click_through_rate = clicks / impressions if clicks > 0 else 0
        save_rate = saves / impressions if saves > 0 else 0
        
        return {
            "engagement_rate": engagement_rate,
            "comment_rate": comment_rate,
            "share_rate": share_rate,
            "click_through_rate": click_through_rate,
            "save_rate": save_rate,
            "total_engagements": total_engagements
        }
    
    def _compare_with_benchmarks(self, kpis, platform):
        """Compare KPIs with industry benchmarks."""
        platform_benchmarks = self.benchmarks.get(platform, self.benchmarks.get("instagram", {}))
        
        comparison = {}
        
        # Compare engagement rate
        if "engagement_rate" in kpis and "engagement_rate" in platform_benchmarks:
            er = kpis["engagement_rate"]
            er_benchmarks = platform_benchmarks["engagement_rate"]
            
            if er < er_benchmarks["low"]:
                comparison["engagement_rate"] = "below_average"
            elif er < er_benchmarks["average"]:
                comparison["engagement_rate"] = "average"
            elif er < er_benchmarks["high"]:
                comparison["engagement_rate"] = "above_average"
            else:
                comparison["engagement_rate"] = "excellent"
        
        # Compare comment rate
        if "comment_rate" in kpis and "comment_rate" in platform_benchmarks:
            cr = kpis["comment_rate"]
            cr_benchmarks = platform_benchmarks["comment_rate"]
            
            if cr < cr_benchmarks["low"]:
                comparison["comment_rate"] = "below_average"
            elif cr < cr_benchmarks["average"]:
                comparison["comment_rate"] = "average"
            elif cr < cr_benchmarks["high"]:
                comparison["comment_rate"] = "above_average"
            else:
                comparison["comment_rate"] = "excellent"
        
        # Compare share rate
        if "share_rate" in kpis and "share_rate" in platform_benchmarks:
            sr = kpis["share_rate"]
            sr_benchmarks = platform_benchmarks["share_rate"]
            
            if sr < sr_benchmarks["low"]:
                comparison["share_rate"] = "below_average"
            elif sr < sr_benchmarks["average"]:
                comparison["share_rate"] = "average"
            elif sr < sr_benchmarks["high"]:
                comparison["share_rate"] = "above_average"
            else:
                comparison["share_rate"] = "excellent"
        
        return comparison
    
    def _compare_with_historical(self, kpis, historical_data):
        """Compare KPIs with historical performance data."""
        # Get average historical KPIs
        hist_engagement_rates = [h.get("engagement_rate", 0) for h in historical_data if "engagement_rate" in h]
        hist_comment_rates = [h.get("comment_rate", 0) for h in historical_data if "comment_rate" in h]
        hist_share_rates = [h.get("share_rate", 0) for h in historical_data if "share_rate" in h]
        
        # Calculate averages, avoiding division by zero
        avg_engagement_rate = np.mean(hist_engagement_rates) if hist_engagement_rates else 0
        avg_comment_rate = np.mean(hist_comment_rates) if hist_comment_rates else 0
        avg_share_rate = np.mean(hist_share_rates) if hist_share_rates else 0
        
        # Calculate percent changes
        engagement_change = ((kpis.get("engagement_rate", 0) - avg_engagement_rate) / avg_engagement_rate * 100) if avg_engagement_rate > 0 else 0
        comment_change = ((kpis.get("comment_rate", 0) - avg_comment_rate) / avg_comment_rate * 100) if avg_comment_rate > 0 else 0
        share_change = ((kpis.get("share_rate", 0) - avg_share_rate) / avg_share_rate * 100) if avg_share_rate > 0 else 0
        
        return {
            "engagement_rate_change": engagement_change,
            "comment_rate_change": comment_change,
            "share_rate_change": share_change
        }
    
    def _calculate_performance_score(self, kpis, benchmark_comparison):
        """Calculate an overall performance score based on KPIs and benchmarks."""
        # Convert benchmark ratings to scores
        rating_scores = {
            "below_average": 1,
            "average": 2,
            "above_average": 3,
            "excellent": 4
        }
        
        # Get scores for each metric
        engagement_score = rating_scores.get(benchmark_comparison.get("engagement_rate", "average"), 2)
        comment_score = rating_scores.get(benchmark_comparison.get("comment_rate", "average"), 2)
        share_score = rating_scores.get(benchmark_comparison.get("share_rate", "average"), 2)
        
        # Calculate weighted average (engagement rate has higher weight)
        weighted_score = (engagement_score * 0.5) + (comment_score * 0.25) + (share_score * 0.25)
        
        # Convert to a 0-100 scale
        performance_score = (weighted_score / 4) * 100
        
        return round(performance_score, 1)
    
    def track_metrics_over_time(self, content_id, metrics_data_series):
        """
        Track and analyze metrics over time for a specific content.
        
        Args:
            content_id: Identifier for the content
            metrics_data_series: List of metrics data points with timestamps
            
        Returns:
            Trend analysis results
        """
        logger.info(f"Tracking metrics over time for content: {content_id}")
        
        try:
            # Sort data by timestamp
            sorted_data = sorted(metrics_data_series, key=lambda x: x.get("timestamp", ""))
            
            # Extract key metrics over time
            timestamps = [d.get("timestamp", "") for d in sorted_data]
            engagements = [d.get("total_engagements", 0) for d in sorted_data]
            impressions = [d.get("impressions", 0) for d in sorted_data]
            
            # Calculate engagement rates over time
            engagement_rates = []
            for i in range(len(engagements)):
                if impressions[i] > 0:
                    engagement_rates.append(engagements[i] / impressions[i])
                else:
                    engagement_rates.append(0)
            
            # Calculate growth rates
            growth_rates = []
            for i in range(1, len(engagement_rates)):
                if engagement_rates[i-1] > 0:
                    growth = (engagement_rates[i] - engagement_rates[i-1]) / engagement_rates[i-1]
                    growth_rates.append(growth)
                else:
                    growth_rates.append(0)
            
            # Calculate trend direction
            if len(growth_rates) >= 3:
                recent_growth = np.mean(growth_rates[-3:])
                if recent_growth > 0.05:
                    trend = "increasing"
                elif recent_growth < -0.05:
                    trend = "decreasing"
                else:
                    trend = "stable"
            else:
                trend = "insufficient_data"
            
            return {
                "content_id": content_id,
                "data_points": len(sorted_data),
                "start_date": timestamps[0] if timestamps else "",
                "end_date": timestamps[-1] if timestamps else "",
                "engagement_rates": engagement_rates,
                "average_engagement_rate": np.mean(engagement_rates) if engagement_rates else 0,
                "growth_rates": growth_rates,
                "average_growth_rate": np.mean(growth_rates) if growth_rates else 0,
                "trend": trend
            }
            
        except Exception as e:
            logger.error(f"Error tracking metrics over time: {e}")
            return {
                "error": f"Failed to track metrics: {str(e)}",
                "content_id": content_id
            }