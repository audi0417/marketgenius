#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Analytics module for MarketGenius.

This module provides functionality for analyzing marketing content performance,
generating reports, and suggesting optimizations.
"""

from marketgenius.analytics.metrics import EngagementAnalyzer
from marketgenius.analytics.optimizer import ContentOptimizer
from marketgenius.analytics.reporter import PerformanceReporter

__all__ = ['EngagementAnalyzer', 'ContentOptimizer', 'PerformanceReporter']