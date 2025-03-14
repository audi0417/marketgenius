#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MarketGenius: AI-driven multi-platform marketing content generation system.
Main application entry point.
"""

import os
import argparse
from marketgenius.ui.app import run_app
from marketgenius.utils.logger import setup_logging
from marketgenius.utils.config import load_config


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="MarketGenius - AI Marketing Content Generator")
    parser.add_argument("--config", type=str, default="config.yml", help="Path to configuration file")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--port", type=int, default=7860, help="Port for the web interface")
    return parser.parse_args()


def main():
    """Main entry point for the application."""
    args = parse_args()
    
    # Setup logging
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logging(log_level)
    
    # Load configuration
    config = load_config(args.config)
    
    # Run the application
    run_app(config, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()