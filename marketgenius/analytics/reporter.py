#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Performance reporter for generating marketing content performance reports.
"""

import os
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
from marketgenius.utils.logger import get_logger

logger = get_logger(__name__)


class PerformanceReporter:
    """Reporter for generating marketing content performance reports."""
    
    def __init__(self, config=None):
        """
        Initialize the performance reporter.
        
        Args:
            config: Configuration dictionary for the reporter
        """
        self.config = config or {}
        self.reports_dir = self.config.get("reports_dir", "reports")
        
        # Ensure reports directory exists
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def generate_content_report(self, content_id, content_info, performance_data):
        """
        Generate a performance report for specific content.
        
        Args:
            content_id: Identifier for the content
            content_info: Information about the content (type, platform, etc.)
            performance_data: Performance metrics data
            
        Returns:
            Report data dictionary and report file path
        """
        logger.info(f"Generating content report for content ID: {content_id}")
        
        try:
            # Create report data structure
            report = {
                "report_id": f"report_{content_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "content_id": content_id,
                "content_info": content_info,
                "report_date": datetime.now().isoformat(),
                "performance_data": performance_data,
                "key_insights": self._generate_key_insights(performance_data, content_info),
                "improvement_recommendations": self._generate_recommendations(performance_data, content_info)
            }
            
            # Generate visualizations and save report
            # Generate visualizations and save report
            report_path = self._save_report(report)
            
            # Add visualization paths to report
            report["visualization_paths"] = self._generate_visualizations(report, report_path)
            
            return report, report_path
            
        except Exception as e:
            logger.error(f"Error generating content report: {e}")
            return {
                "error": f"Failed to generate report: {str(e)}",
                "content_id": content_id
            }, None
    
    def generate_campaign_report(self, campaign_id, campaign_info, content_reports):
        """
        Generate a performance report for an entire campaign.
        
        Args:
            campaign_id: Identifier for the campaign
            campaign_info: Information about the campaign
            content_reports: List of content reports in the campaign
            
        Returns:
            Campaign report data and report file path
        """
        logger.info(f"Generating campaign report for campaign ID: {campaign_id}")
        
        try:
            # Aggregate performance data across content
            aggregated_data = self._aggregate_campaign_data(content_reports)
            
            # Create report data structure
            report = {
                "report_id": f"campaign_{campaign_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "campaign_id": campaign_id,
                "campaign_info": campaign_info,
                "report_date": datetime.now().isoformat(),
                "content_count": len(content_reports),
                "aggregated_performance": aggregated_data,
                "top_performing_content": self._identify_top_content(content_reports),
                "performance_by_platform": self._analyze_performance_by_platform(content_reports),
                "performance_by_content_type": self._analyze_performance_by_content_type(content_reports),
                "key_insights": self._generate_campaign_insights(aggregated_data, campaign_info),
                "recommendations": self._generate_campaign_recommendations(aggregated_data, campaign_info)
            }
            
            # Generate visualizations and save report
            report_path = self._save_report(report, is_campaign=True)
            
            # Add visualization paths to report
            report["visualization_paths"] = self._generate_campaign_visualizations(report, report_path)
            
            return report, report_path
            
        except Exception as e:
            logger.error(f"Error generating campaign report: {e}")
            return {
                "error": f"Failed to generate campaign report: {str(e)}",
                "campaign_id": campaign_id
            }, None
    
    def _generate_key_insights(self, performance_data, content_info):
        """Generate key insights from performance data."""
        insights = []
        
        # Extract key metrics
        engagement_rate = performance_data.get("engagement_rate", 0)
        impressions = performance_data.get("impressions", 0)
        reach = performance_data.get("reach", 0)
        platform = content_info.get("platform", "")
        
        # Add insights based on engagement rate
        if platform == "instagram":
            if engagement_rate > 0.06:
                insights.append("Exceptional engagement rate that exceeds industry benchmarks")
            elif engagement_rate > 0.03:
                insights.append("Above-average engagement rate for Instagram content")
            elif engagement_rate < 0.01:
                insights.append("Below-average engagement rate, consider content optimization")
        elif platform == "facebook":
            if engagement_rate > 0.04:
                insights.append("Exceptional engagement rate that exceeds industry benchmarks")
            elif engagement_rate > 0.015:
                insights.append("Above-average engagement rate for Facebook content")
            elif engagement_rate < 0.005:
                insights.append("Below-average engagement rate, consider content optimization")
        
        # Add insights based on reach vs. impressions ratio
        if reach > 0 and impressions > 0:
            impression_ratio = impressions / reach
            if impression_ratio > 1.5:
                insights.append(f"High impression to reach ratio ({impression_ratio:.2f}), indicating content was viewed multiple times by the same users")
            elif impression_ratio < 1.1:
                insights.append("Low impression to reach ratio, suggesting limited repeat views")
        
        # Add insights based on comments to likes ratio
        comments = performance_data.get("comments", 0)
        likes = performance_data.get("likes", 0)
        if likes > 0:
            comment_ratio = comments / likes
            if comment_ratio > 0.1:
                insights.append("High comment-to-like ratio, indicating strong audience engagement")
            elif comment_ratio < 0.01:
                insights.append("Low comment-to-like ratio, consider adding more conversation starters")
        
        # Add insights based on time of day (if available)
        post_time = performance_data.get("post_time")
        if post_time:
            hour = int(post_time.split(":")[0])
            if platform == "instagram" and (hour >= 11 and hour <= 15):
                insights.append("Posted during optimal engagement hours for Instagram")
            elif platform == "facebook" and (hour >= 13 and hour <= 16):
                insights.append("Posted during optimal engagement hours for Facebook")
        
        # If not enough insights, add a generic one
        if len(insights) < 2:
            insights.append(f"Content received {impressions} impressions and reached {reach} unique users")
        
        return insights
    
    def _generate_recommendations(self, performance_data, content_info):
        """Generate recommendations based on performance data."""
        recommendations = []
        
        # Extract key metrics
        engagement_rate = performance_data.get("engagement_rate", 0)
        comments = performance_data.get("comments", 0)
        likes = performance_data.get("likes", 0)
        shares = performance_data.get("shares", 0)
        platform = content_info.get("platform", "")
        content_type = content_info.get("content_type", "")
        
        # Recommendations based on engagement rate
        if engagement_rate < 0.02:
            recommendations.append("Consider testing different content formats to improve engagement")
            recommendations.append("Analyze high-performing content to identify successful elements")
        
        # Recommendations based on comments
        if comments < 5:
            recommendations.append("Include questions or controversial statements to encourage comments")
            recommendations.append("Respond to existing comments to foster conversation")
        
        # Recommendations based on shares
        if shares < 3:
            recommendations.append("Create more shareable content by focusing on value-adding information or emotional appeal")
        
        # Platform-specific recommendations
        if platform == "instagram":
            if content_type == "post" and performance_data.get("saves", 0) < 5:
                recommendations.append("Create more saveable content with actionable information or resources")
            recommendations.append("Test different hashtag strategies to expand reach")
        elif platform == "facebook":
            recommendations.append("Consider boosting top-performing organic content to expand reach")
            recommendations.append("Test different post lengths to find optimal engagement")
        elif platform == "linkedin":
            recommendations.append("Share industry insights and professional knowledge to increase credibility")
            recommendations.append("Engage with commenters to build professional relationships")
        
        # Timing recommendations
        post_time = performance_data.get("post_time")
        if post_time:
            hour = int(post_time.split(":")[0])
            if platform == "instagram" and (hour < 11 or hour > 20):
                recommendations.append("Test posting between 11am and 8pm for potentially higher engagement")
            elif platform == "facebook" and (hour < 13 or hour > 16):
                recommendations.append("Test posting between 1pm and 4pm for potentially higher engagement")
        
        # Ensure we have a reasonable number of recommendations
        if len(recommendations) > 5:
            recommendations = recommendations[:5]  # Limit to top 5
        elif len(recommendations) < 2:
            recommendations.append("Continue monitoring performance and test new content strategies")
        
        return recommendations
    
    def _save_report(self, report, is_campaign=False):
        """Save report to disk and return the file path."""
        report_type = "campaign" if is_campaign else "content"
        report_id = report.get("report_id", f"{report_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}")
        
        # Create directory for this report
        report_dir = os.path.join(self.reports_dir, report_id)
        os.makedirs(report_dir, exist_ok=True)
        
        # Save report as JSON
        report_path = os.path.join(report_dir, f"{report_id}.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Report saved to: {report_path}")
        return report_dir
    
    def _generate_visualizations(self, report, report_dir):
        """Generate visualizations for content report and return paths."""
        visualization_paths = {}
        
        try:
            performance_data = report.get("performance_data", {})
            
            # Generate engagement chart if time series data is available
            if "time_series" in performance_data:
                engagement_chart_path = os.path.join(report_dir, "engagement_over_time.png")
                self._create_engagement_time_chart(performance_data["time_series"], engagement_chart_path)
                visualization_paths["engagement_chart"] = engagement_chart_path
            
            # Generate metrics comparison chart
            metrics_chart_path = os.path.join(report_dir, "metrics_comparison.png")
            self._create_metrics_comparison_chart(performance_data, metrics_chart_path)
            visualization_paths["metrics_chart"] = metrics_chart_path
            
            return visualization_paths
            
        except Exception as e:
            logger.error(f"Error generating visualizations: {e}")
            return {}
    
    def _generate_campaign_visualizations(self, report, report_dir):
        """Generate visualizations for campaign report and return paths."""
        visualization_paths = {}
        
        try:
            # Generate platform comparison chart
            if "performance_by_platform" in report:
                platform_chart_path = os.path.join(report_dir, "platform_comparison.png")
                self._create_platform_comparison_chart(report["performance_by_platform"], platform_chart_path)
                visualization_paths["platform_chart"] = platform_chart_path
            
            # Generate content type comparison chart
            if "performance_by_content_type" in report:
                content_type_chart_path = os.path.join(report_dir, "content_type_comparison.png")
                self._create_content_type_chart(report["performance_by_content_type"], content_type_chart_path)
                visualization_paths["content_type_chart"] = content_type_chart_path
            
            # Generate top content chart
            if "top_performing_content" in report:
                top_content_chart_path = os.path.join(report_dir, "top_content.png")
                self._create_top_content_chart(report["top_performing_content"], top_content_chart_path)
                visualization_paths["top_content_chart"] = top_content_chart_path
            
            return visualization_paths
            
        except Exception as e:
            logger.error(f"Error generating campaign visualizations: {e}")
            return {}
    
    def _create_engagement_time_chart(self, time_series_data, output_path):
        """Create a chart showing engagement over time."""
        try:
            # Extract data
            timestamps = [entry.get("timestamp") for entry in time_series_data]
            engagement_rates = [entry.get("engagement_rate", 0) for entry in time_series_data]
            
            # Convert timestamps to datetime objects and format them
            dates = [datetime.fromisoformat(ts.replace('Z', '+00:00')) for ts in timestamps]
            date_labels = [date.strftime('%m-%d %H:%M') for date in dates]
            
            # Create the plot
            plt.figure(figsize=(10, 5))
            plt.plot(date_labels, engagement_rates, marker='o', linestyle='-', color='#3498db')
            plt.title('Engagement Rate Over Time', fontsize=14)
            plt.xlabel('Date & Time', fontsize=12)
            plt.ylabel('Engagement Rate', fontsize=12)
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.grid(True, linestyle='--', alpha=0.7)
            
            # Save the figure
            plt.savefig(output_path)
            plt.close()
            
            logger.info(f"Engagement time chart saved to: {output_path}")
            
        except Exception as e:
            logger.error(f"Error creating engagement time chart: {e}")
    
    def _create_metrics_comparison_chart(self, performance_data, output_path):
        """Create a chart comparing different engagement metrics."""
        try:
            # Extract metrics
            metrics = {
                'Likes': performance_data.get('likes', 0),
                'Comments': performance_data.get('comments', 0),
                'Shares': performance_data.get('shares', 0),
                'Saves': performance_data.get('saves', 0)
            }
            
            # Filter out zero values
            metrics = {k: v for k, v in metrics.items() if v > 0}
            
            if not metrics:
                logger.warning("No metrics data available for comparison chart")
                return
            
            # Create the plot
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Colors for the bars
            colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12']
            
            # Create bar chart
            bars = ax.bar(metrics.keys(), metrics.values(), color=colors[:len(metrics)])
            
            # Add value labels on top of each bar
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{int(height)}', ha='center', va='bottom')
            
            # Customize the plot
            ax.set_title('Engagement Metrics Comparison', fontsize=14)
            ax.set_ylabel('Count', fontsize=12)
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            
            # Save the figure
            plt.tight_layout()
            plt.savefig(output_path)
            plt.close()
            
            logger.info(f"Metrics comparison chart saved to: {output_path}")
            
        except Exception as e:
            logger.error(f"Error creating metrics comparison chart: {e}")
    
    def _create_platform_comparison_chart(self, platform_data, output_path):
        """Create a chart comparing performance across platforms."""
        try:
            # Extract platforms and engagement rates
            platforms = list(platform_data.keys())
            engagement_rates = [data.get('engagement_rate', 0) for data in platform_data.values()]
            
            if not platforms:
                logger.warning("No platform data available for comparison chart")
                return
            
            # Create the plot
            plt.figure(figsize=(10, 6))
            
            # Colors for the bars
            colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6']
            
            # Create bar chart
            bars = plt.bar(platforms, engagement_rates, color=colors[:len(platforms)])
            
            # Add value labels on top of each bar
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 0.001,
                        f'{height:.2%}', ha='center', va='bottom')
            
            # Customize the plot
            plt.title('Engagement Rate by Platform', fontsize=14)
            plt.ylabel('Engagement Rate', fontsize=12)
            plt.ylim(0, max(engagement_rates) * 1.2)  # Give some headroom for labels
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            
            # Save the figure
            plt.tight_layout()
            plt.savefig(output_path)
            plt.close()
            
            logger.info(f"Platform comparison chart saved to: {output_path}")
            
        except Exception as e:
            logger.error(f"Error creating platform comparison chart: {e}")
    
    def _create_content_type_chart(self, content_type_data, output_path):
        """Create a chart comparing performance across content types."""
        try:
            # Extract content types and engagement rates
            content_types = list(content_type_data.keys())
            engagement_rates = [data.get('engagement_rate', 0) for data in content_type_data.values()]
            
            if not content_types:
                logger.warning("No content type data available for comparison chart")
                return
            
            # Create the plot
            plt.figure(figsize=(10, 6))
            
            # Colors for the bars
            colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6']
            
            # Create bar chart
            bars = plt.bar(content_types, engagement_rates, color=colors[:len(content_types)])
            
            # Add value labels on top of each bar
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 0.001,
                        f'{height:.2%}', ha='center', va='bottom')
            
            # Customize the plot
            plt.title('Engagement Rate by Content Type', fontsize=14)
            plt.ylabel('Engagement Rate', fontsize=12)
            plt.ylim(0, max(engagement_rates) * 1.2)  # Give some headroom for labels
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            
            # Save the figure
            plt.tight_layout()
            plt.savefig(output_path)
            plt.close()
            
            logger.info(f"Content type chart saved to: {output_path}")
            
        except Exception as e:
            logger.error(f"Error creating content type chart: {e}")
    
    def _create_top_content_chart(self, top_content_data, output_path):
        """Create a chart showing top performing content."""
        try:
            # Extract content IDs and engagement rates
            content_ids = [item.get('content_id', f'Content {i+1}') for i, item in enumerate(top_content_data)]
            engagement_rates = [item.get('engagement_rate', 0) for item in top_content_data]
            
            if not content_ids:
                logger.warning("No top content data available for chart")
                return
            
            # Create shortened content IDs for display
            short_ids = [f"Content {i+1}" for i in range(len(content_ids))]
            
            # Create the plot
            plt.figure(figsize=(10, 6))
            
            # Create horizontal bar chart
            bars = plt.barh(short_ids, engagement_rates, color='#3498db')
            
            # Add value labels
            for i, bar in enumerate(bars):
                width = bar.get_width()
                plt.text(width + 0.001, bar.get_y() + bar.get_height()/2,
                        f'{width:.2%}', va='center')
            
            # Customize the plot
            plt.title('Top Performing Content by Engagement Rate', fontsize=14)
            plt.xlabel('Engagement Rate', fontsize=12)
            plt.xlim(0, max(engagement_rates) * 1.2)  # Give some headroom for labels
            plt.grid(axis='x', linestyle='--', alpha=0.7)
            
            # Save the figure
            plt.tight_layout()
            plt.savefig(output_path)
            plt.close()
            
            logger.info(f"Top content chart saved to: {output_path}")
            
        except Exception as e:
            logger.error(f"Error creating top content chart: {e}")
    
    def _aggregate_campaign_data(self, content_reports):
        """Aggregate performance data across all content in a campaign."""
        aggregated = {
            "total_impressions": 0,
            "total_reach": 0,
            "total_engagements": 0,
            "average_engagement_rate": 0,
            "total_likes": 0,
            "total_comments": 0,
            "total_shares": 0
        }
        
        # Sum metrics across all content
        for report in content_reports:
            performance_data = report.get("performance_data", {})
            
            aggregated["total_impressions"] += performance_data.get("impressions", 0)
            aggregated["total_reach"] += performance_data.get("reach", 0)
            aggregated["total_likes"] += performance_data.get("likes", 0)
            aggregated["total_comments"] += performance_data.get("comments", 0)
            aggregated["total_shares"] += performance_data.get("shares", 0)
        
        # Calculate total engagements
        aggregated["total_engagements"] = (
            aggregated["total_likes"] + 
            aggregated["total_comments"] + 
            aggregated["total_shares"]
        )
        
        # Calculate average engagement rate
        if aggregated["total_impressions"] > 0:
            aggregated["average_engagement_rate"] = aggregated["total_engagements"] / aggregated["total_impressions"]
        
        return aggregated
    
    def _identify_top_content(self, content_reports):
        """Identify top performing content in the campaign."""
        # Extract content IDs and engagement rates
        content_performance = []
        for report in content_reports:
            content_id = report.get("content_id", "")
            content_info = report.get("content_info", {})
            performance_data = report.get("performance_data", {})
            
            engagement_rate = performance_data.get("engagement_rate", 0)
            
            content_performance.append({
                "content_id": content_id,
                "platform": content_info.get("platform", ""),
                "content_type": content_info.get("content_type", ""),
                "engagement_rate": engagement_rate
            })
        
        # Sort by engagement rate (descending)
        top_content = sorted(content_performance, key=lambda x: x["engagement_rate"], reverse=True)
        
        # Return top 5 or all if less than 5
        return top_content[:5] if len(top_content) > 5 else top_content
    
    def _analyze_performance_by_platform(self, content_reports):
        """Analyze performance aggregated by platform."""
        platform_metrics = {}
        
        for report in content_reports:
            content_info = report.get("content_info", {})
            performance_data = report.get("performance_data", {})
            
            platform = content_info.get("platform", "unknown")
            
            if platform not in platform_metrics:
                platform_metrics[platform] = {
                    "content_count": 0,
                    "total_impressions": 0,
                    "total_engagements": 0,
                    "engagement_rate": 0
                }
            
            # Update metrics for this platform
            platform_metrics[platform]["content_count"] += 1
            platform_metrics[platform]["total_impressions"] += performance_data.get("impressions", 0)
            
            # Calculate engagements
            engagements = (
                performance_data.get("likes", 0) +
                performance_data.get("comments", 0) +
                performance_data.get("shares", 0)
            )
            
            platform_metrics[platform]["total_engagements"] += engagements
        
        # Calculate engagement rates
        for platform, metrics in platform_metrics.items():
            if metrics["total_impressions"] > 0:
                metrics["engagement_rate"] = metrics["total_engagements"] / metrics["total_impressions"]
        
        return platform_metrics
    
    def _analyze_performance_by_content_type(self, content_reports):
        """Analyze performance aggregated by content type."""
        content_type_metrics = {}
        
        for report in content_reports:
            content_info = report.get("content_info", {})
            performance_data = report.get("performance_data", {})
            
            content_type = content_info.get("content_type", "unknown")
            
            if content_type not in content_type_metrics:
                content_type_metrics[content_type] = {
                    "content_count": 0,
                    "total_impressions": 0,
                    "total_engagements": 0,
                    "engagement_rate": 0
                }
            
            # Update metrics for this content type
            content_type_metrics[content_type]["content_count"] += 1
            content_type_metrics[content_type]["total_impressions"] += performance_data.get("impressions", 0)
            
            # Calculate engagements
            engagements = (
                performance_data.get("likes", 0) +
                performance_data.get("comments", 0) +
                performance_data.get("shares", 0)
            )
            
            content_type_metrics[content_type]["total_engagements"] += engagements
        
        # Calculate engagement rates
        for content_type, metrics in content_type_metrics.items():
            if metrics["total_impressions"] > 0:
                metrics["engagement_rate"] = metrics["total_engagements"] / metrics["total_impressions"]
        
        return content_type_metrics
    
    def _generate_campaign_insights(self, aggregated_data, campaign_info):
        """Generate key insights for a campaign report."""
        insights = []
        
        # Generate insights based on aggregated data
        engagement_rate = aggregated_data.get("average_engagement_rate", 0)
        
        if engagement_rate > 0.04:
            insights.append("Campaign is achieving exceptional engagement rates above industry benchmarks")
        elif engagement_rate > 0.02:
            insights.append("Campaign is achieving solid engagement rates in line with industry standards")
        elif engagement_rate < 0.01:
            insights.append("Campaign engagement rates are below average, suggesting optimization opportunities")
        
        # Insights based on total metrics
        total_impressions = aggregated_data.get("total_impressions", 0)
        total_reach = aggregated_data.get("total_reach", 0)
        
        if total_impressions > 0 and total_reach > 0:
            frequency = total_impressions / total_reach
            insights.append(f"Campaign achieved an average frequency of {frequency:.1f} impressions per person reached")
        
        # Comment engagement insights
        total_comments = aggregated_data.get("total_comments", 0)
        total_likes = aggregated_data.get("total_likes", 0)
        
        if total_comments > 0 and total_likes > 0:
            comment_ratio = total_comments / total_likes
            if comment_ratio > 0.1:
                insights.append("Campaign is generating strong comment engagement relative to likes")
            elif comment_ratio < 0.02:
                insights.append("Campaign is generating minimal comment engagement, consider adding conversation starters")
        
        # Add generic insights if needed
        if len(insights) < 3:
            campaign_name = campaign_info.get("name", "Campaign")
            insights.append(f"{campaign_name} generated {total_impressions} impressions and {aggregated_data.get('total_engagements', 0)} total engagements")
        
        return insights
    
    def _generate_campaign_recommendations(self, aggregated_data, campaign_info):
        """Generate recommendations for a campaign report."""
        recommendations = []
        
        # Generate recommendations based on aggregated data
        engagement_rate = aggregated_data.get("average_engagement_rate", 0)
        
        if engagement_rate < 0.02:
            recommendations.append("Review top-performing content and identify common elements to replicate")
            recommendations.append("Consider revising content strategy to better align with audience interests")
        
        # Recommendations based on comment engagement
        total_comments = aggregated_data.get("total_comments", 0)
        total_impressions = aggregated_data.get("total_impressions", 0)
        
        if total_impressions > 0 and (total_comments / total_impressions) < 0.005:
            recommendations.append("Develop more conversation-starting content to increase comment engagement")
            recommendations.append("Respond to existing comments to foster community engagement")
        
        # Recommendations based on campaign objectives
        campaign_objective = campaign_info.get("objective", "")
        
        if campaign_objective == "brand_awareness":
            recommendations.append("Focus on increasing reach with broader targeting and shareable content")
        elif campaign_objective == "engagement":
            recommendations.append("Create more interactive content such as polls, questions, and contests")
        elif campaign_objective == "conversion":
            recommendations.append("Strengthen call-to-action elements and test different CTAs to optimize conversion")
        
        # Add generic recommendations if needed
        if len(recommendations) < 3:
            recommendations.append("Continue testing different content formats to identify what resonates best with your audience")
            recommendations.append("Analyze platform-specific performance to optimize resource allocation")
        
        return recommendations