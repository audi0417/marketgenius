#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MarketGenius 數據加載模組。
負責從外部來源加載數據，包括文件、API 和數據庫。
"""

import os
import csv
import json
import logging
import requests
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)

class DataLoader:
    """數據加載類，處理從各種來源加載數據。"""
    
    def __init__(self, cache_dir: str = "cache"):
        """
        初始化數據加載器。
        
        Args:
            cache_dir: 緩存目錄路徑
        """
        self.cache_dir = Path(cache_dir)
        self._ensure_cache_directory()
        self.session = requests.Session()
    
    def _ensure_cache_directory(self) -> None:
        """確保緩存目錄存在。"""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"確保緩存目錄存在: {self.cache_dir}")
    
    def load_csv(self, file_path: Union[str, Path], has_header: bool = True) -> List[Dict[str, str]]:
        """
        加載 CSV 文件。
        
        Args:
            file_path: CSV 文件路徑
            has_header: 是否有標題行
            
        Returns:
            CSV 數據列表（字典列表，如果有標題行）
        """
        file_path = Path(file_path)
        if not file_path.exists():
            logger.error(f"CSV 文件不存在: {file_path}")
            return []
        
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as f:
                if has_header:
                    reader = csv.DictReader(f)
                    return list(reader)
                else:
                    reader = csv.reader(f)
                    return [{"column_" + str(i): cell for i, cell in enumerate(row)} for row in reader]
        except Exception as e:
            logger.error(f"加載 CSV 文件 {file_path} 時出錯: {e}")
            return []
    
    def load_json_file(self, file_path: Union[str, Path], default: Any = None) -> Any:
        """
        加載 JSON 文件。
        
        Args:
            file_path: JSON 文件路徑
            default: 文件不存在或加載錯誤時返回的默認值
            
        Returns:
            JSON 數據或默認值
        """
        file_path = Path(file_path)
        if not file_path.exists():
            logger.error(f"JSON 文件不存在: {file_path}")
            return default
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加載 JSON 文件 {file_path} 時出錯: {e}")
            return default
    
    def fetch_url(self, url: str, params: Optional[Dict] = None, 
                 headers: Optional[Dict] = None, cache: bool = True, 
                 cache_ttl: int = 3600) -> Optional[str]:
        """
        從 URL 獲取數據，可選緩存。
        
        Args:
            url: 要請求的 URL
            params: 請求參數
            headers: 請求標頭
            cache: 是否緩存結果
            cache_ttl: 緩存有效時間（秒）
            
        Returns:
            響應文本或 None（如果請求失敗）
        """
        cache_key = f"{url}_{str(params)}"
        cache_path = self.cache_dir / f"{hash(cache_key)}.cache"
        
        # 檢查緩存
        if cache and cache_path.exists():
            cache_stat = cache_path.stat()
            cache_age = os.time() - cache_stat.st_mtime
            
            if cache_age < cache_ttl:
                try:
                    with open(cache_path, 'r', encoding='utf-8') as f:
                        logger.debug(f"從緩存加載 URL 數據: {url}")
                        return f.read()
                except Exception as e:
                    logger.warning(f"讀取緩存時出錯: {e}")
        
        # 請求 URL
        try:
            response = self.session.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            content = response.text
            
            # 保存到緩存
            if cache:
                try:
                    with open(cache_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                except Exception as e:
                    logger.warning(f"寫入緩存時出錯: {e}")
            
            logger.debug(f"已獲取 URL 數據: {url}")
            return content
        except Exception as e:
            logger.error(f"獲取 URL {url} 時出錯: {e}")
            return None
    
    def fetch_json_api(self, url: str, params: Optional[Dict] = None, 
                      headers: Optional[Dict] = None, cache: bool = True, 
                      cache_ttl: int = 3600) -> Optional[Dict]:
        """
        從 JSON API 獲取數據。
        
        Args:
            url: API URL
            params: 請求參數
            headers: 請求標頭
            cache: 是否緩存結果
            cache_ttl: 緩存有效時間（秒）
            
        Returns:
            JSON 數據或 None（如果請求失敗）
        """
        response_text = self.fetch_url(url, params, headers, cache, cache_ttl)
        if response_text is None:
            return None
        
        try:
            return json.loads(response_text)
        except Exception as e:
            logger.error(f"解析 API JSON 響應時出錯: {e}")
            return None
    
    def load_text_file(self, file_path: Union[str, Path], default: str = "") -> str:
        """
        加載文本文件。
        
        Args:
            file_path: 文本文件路徑
            default: 文件不存在或加載錯誤時返回的默認值
            
        Returns:
            文件內容或默認值
        """
        file_path = Path(file_path)
        if not file_path.exists():
            logger.error(f"文本文件不存在: {file_path}")
            return default
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"加載文本文件 {file_path} 時出錯: {e}")
            return default
    
    def load_binary_file(self, file_path: Union[str, Path]) -> Optional[bytes]:
        """
        加載二進制文件。
        
        Args:
            file_path: 二進制文件路徑
            
        Returns:
            二進制數據或 None（如果加載失敗）
        """
        file_path = Path(file_path)
        if not file_path.exists():
            logger.error(f"二進制文件不存在: {file_path}")
            return None
        
        try:
            with open(file_path, 'rb') as f:
                return f.read()
        except Exception as e:
            logger.error(f"加載二進制文件 {file_path} 時出錯: {e}")
            return None
    
    def load_brand_samples(self, brand_id: str, sample_dir: Union[str, Path] = "samples") -> List[str]:
        """
        加載品牌樣本內容。
        
        Args:
            brand_id: 品牌 ID
            sample_dir: 樣本目錄路徑
            
        Returns:
            樣本內容列表
        """
        sample_path = Path(sample_dir) / brand_id
        if not sample_path.exists() or not sample_path.is_dir():
            logger.warning(f"品牌樣本目錄不存在: {sample_path}")
            return []
        
        samples = []
        for file_path in sample_path.glob("*.txt"):
            content = self.load_text_file(file_path)
            if content:
                samples.append(content)
        
        logger.debug(f"已加載 {len(samples)} 個品牌樣本，品牌 ID: {brand_id}")
        return samples


# 全局數據加載器實例
data_loader = DataLoader()
