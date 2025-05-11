#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MarketGenius 數據存儲模組。
負責數據持久化和檢索操作。
"""

import os
import json
import pickle
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)

class DataStore:
    """數據存儲類，處理所有數據的保存和加載。"""
    
    def __init__(self, data_dir: str = "data"):
        """
        初始化數據存儲。
        
        Args:
            data_dir: 數據儲存的目錄路徑
        """
        self.data_dir = Path(data_dir)
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """確保所有需要的數據目錄存在。"""
        directories = [
            self.data_dir,
            self.data_dir / "brands",
            self.data_dir / "content",
            self.data_dir / "analytics",
            self.data_dir / "models",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
        logger.debug(f"確保數據目錄存在: {', '.join(str(d) for d in directories)}")
    
    def save_json(self, data: Any, file_path: Union[str, Path], indent: int = 2) -> bool:
        """
        將數據保存為JSON文件。
        
        Args:
            data: 要保存的數據
            file_path: 相對於數據目錄的文件路徑
            indent: JSON縮進級別
            
        Returns:
            操作是否成功
        """
        full_path = self.data_dir / file_path
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=indent)
            logger.debug(f"已保存JSON數據至 {full_path}")
            return True
        except Exception as e:
            logger.error(f"保存JSON數據至 {full_path} 時出錯: {e}")
            return False
    
    def load_json(self, file_path: Union[str, Path], default: Any = None) -> Any:
        """
        從JSON文件加載數據。
        
        Args:
            file_path: 相對於數據目錄的文件路徑
            default: 文件不存在或加載錯誤時返回的默認值
            
        Returns:
            加載的數據或默認值
        """
        full_path = self.data_dir / file_path
        if not os.path.exists(full_path):
            logger.warning(f"JSON文件不存在: {full_path}，返回默認值")
            return default
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.debug(f"已加載JSON數據從 {full_path}")
            return data
        except Exception as e:
            logger.error(f"加載JSON數據從 {full_path} 時出錯: {e}")
            return default
    
    def save_pickle(self, data: Any, file_path: Union[str, Path]) -> bool:
        """
        將數據保存為Pickle文件（適用於複雜對象）。
        
        Args:
            data: 要保存的數據
            file_path: 相對於數據目錄的文件路徑
            
        Returns:
            操作是否成功
        """
        full_path = self.data_dir / file_path
        try:
            with open(full_path, 'wb') as f:
                pickle.dump(data, f)
            logger.debug(f"已保存Pickle數據至 {full_path}")
            return True
        except Exception as e:
            logger.error(f"保存Pickle數據至 {full_path} 時出錯: {e}")
            return False
    
    def load_pickle(self, file_path: Union[str, Path], default: Any = None) -> Any:
        """
        從Pickle文件加載數據。
        
        Args:
            file_path: 相對於數據目錄的文件路徑
            default: 文件不存在或加載錯誤時返回的默認值
            
        Returns:
            加載的數據或默認值
        """
        full_path = self.data_dir / file_path
        if not os.path.exists(full_path):
            logger.warning(f"Pickle文件不存在: {full_path}，返回默認值")
            return default
        
        try:
            with open(full_path, 'rb') as f:
                data = pickle.load(f)
            logger.debug(f"已加載Pickle數據從 {full_path}")
            return data
        except Exception as e:
            logger.error(f"加載Pickle數據從 {full_path} 時出錯: {e}")
            return default
    
    def save_text(self, text: str, file_path: Union[str, Path]) -> bool:
        """
        保存文本文件。
        
        Args:
            text: 要保存的文本
            file_path: 相對於數據目錄的文件路徑
            
        Returns:
            操作是否成功
        """
        full_path = self.data_dir / file_path
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(text)
            logger.debug(f"已保存文本數據至 {full_path}")
            return True
        except Exception as e:
            logger.error(f"保存文本數據至 {full_path} 時出錯: {e}")
            return False
    
    def load_text(self, file_path: Union[str, Path], default: str = "") -> str:
        """
        加載文本文件。
        
        Args:
            file_path: 相對於數據目錄的文件路徑
            default: 文件不存在或加載錯誤時返回的默認值
            
        Returns:
            加載的文本或默認值
        """
        full_path = self.data_dir / file_path
        if not os.path.exists(full_path):
            logger.warning(f"文本文件不存在: {full_path}，返回默認值")
            return default
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                text = f.read()
            logger.debug(f"已加載文本數據從 {full_path}")
            return text
        except Exception as e:
            logger.error(f"加載文本數據從 {full_path} 時出錯: {e}")
            return default
    
    def list_files(self, directory: Union[str, Path], pattern: str = "*") -> List[Path]:
        """
        列出目錄中的文件。
        
        Args:
            directory: 相對於數據目錄的目錄路徑
            pattern: 文件名匹配模式
            
        Returns:
            匹配的文件路徑列表
        """
        full_dir = self.data_dir / directory
        if not full_dir.exists():
            logger.warning(f"目錄不存在: {full_dir}")
            return []
        
        return list(full_dir.glob(pattern))
    
    def delete_file(self, file_path: Union[str, Path]) -> bool:
        """
        刪除文件。
        
        Args:
            file_path: 相對於數據目錄的文件路徑
            
        Returns:
            操作是否成功
        """
        full_path = self.data_dir / file_path
        if not os.path.exists(full_path):
            logger.warning(f"要刪除的文件不存在: {full_path}")
            return False
        
        try:
            os.remove(full_path)
            logger.debug(f"已刪除文件: {full_path}")
            return True
        except Exception as e:
            logger.error(f"刪除文件 {full_path} 時出錯: {e}")
            return False


# 全局數據存儲實例
data_store = DataStore()
