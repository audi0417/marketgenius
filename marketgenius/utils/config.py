#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuration utilities for the MarketGenius application.
"""

import os
import yaml
from marketgenius.utils.logger import get_logger

logger = get_logger(__name__)

DEFAULT_CONFIG = {
    "api": {
        "openai_api_key": "",
        "stability_api_key": "",
        "azure_api_key": "",
        "azure_endpoint": "",
        "azure_api_version": "2023-07-01-preview"
    },
    "models": {
        "main_model": "gpt-4",
        "temperature": 0.7,
        "seed": 42
    },
    "content": {
        "max_rounds": 10
    },
    "brand": {
        "models_dir": "models/brands"
    },
    "text_generation": {
        "max_tokens": 2000
    },
    "image_generation": {
        "default_size": "1024x1024",
        "model": "stable-diffusion-v1-5",
        "use_stable_diffusion": True,
        "use_huggingface": False
    },
    "video_generation": {
        "enabled": False
    },
    "analytics": {
        "store_results": True
    }
}


def load_config(config_path=None):
    """
    Load configuration from a YAML file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Configuration dictionary
    """
    config = DEFAULT_CONFIG.copy()
    
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                file_config = yaml.safe_load(f)
                
            # Merge file config with default config
            _deep_update(config, file_config)
            logger.info(f"Configuration loaded from: {config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration from {config_path}: {e}")
            logger.info("Using default configuration")
    else:
        logger.info("No configuration file found. Using default configuration.")
    
    # Check for environment variables
    _update_from_env(config)
    
    return config


def save_config(config, config_path):
    """
    Save configuration to a YAML file.
    
    Args:
        config: Configuration dictionary
        config_path: Path to save the configuration file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(config_path)), exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False)
            
        logger.info(f"Configuration saved to: {config_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving configuration to {config_path}: {e}")
        return False


def _deep_update(d, u):
    """
    Recursively update a dictionary.
    
    Args:
        d: Dictionary to update
        u: Dictionary with updates
    """
    for k, v in u.items():
        if isinstance(v, dict) and k in d and isinstance(d[k], dict):
            _deep_update(d[k], v)
        else:
            d[k] = v


def _update_from_env(config):
    """
    Update configuration from environment variables.
    
    Args:
        config: Configuration dictionary to update
    """
    # API keys
    if os.environ.get('OPENAI_API_KEY'):
        config['api']['openai_api_key'] = os.environ.get('OPENAI_API_KEY')
        
    if os.environ.get('STABILITY_API_KEY'):
        config['api']['stability_api_key'] = os.environ.get('STABILITY_API_KEY')
        
    if os.environ.get('AZURE_OPENAI_API_KEY'):
        config['api']['azure_api_key'] = os.environ.get('AZURE_OPENAI_API_KEY')
        
    if os.environ.get('AZURE_OPENAI_ENDPOINT'):
        config['api']['azure_endpoint'] = os.environ.get('AZURE_OPENAI_ENDPOINT')