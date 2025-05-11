#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MarketGenius 品牌風格保持器。
負責確保生成的內容符合品牌風格特徵。
"""

import re
import logging
import string
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from collections import Counter
from typing import Dict, List, Optional, Tuple, Any

from marketgenius.brand.modeler import BrandLanguageModel
from marketgenius.data.schemas import BrandModel, ContentType

# 確保必要的 NLTK 資源存在
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

logger = logging.getLogger(__name__)


class BrandStyleKeeper:
    """品牌風格一致性檢查和增強工具。"""
    
    def __init__(self, brand_model: Optional[BrandModel] = None, 
                language_model: Optional[BrandLanguageModel] = None):
        """
        初始化品牌風格保持器。
        
        Args:
            brand_model: 品牌模型數據
            language_model: 品牌語言模型
        """
        self.brand_model = brand_model
        self.language_model = language_model
        self.stop_words = set(stopwords.words('english'))
    
    def set_brand_model(self, brand_model: BrandModel) -> None:
        """
        設置品牌模型。
        
        Args:
            brand_model: 品牌模型
        """
        self.brand_model = brand_model
        logger.debug(f"已設置品牌風格保持器的品牌模型: {brand_model.name}")
    
    def set_language_model(self, language_model: BrandLanguageModel) -> None:
        """
        設置品牌語言模型。
        
        Args:
            language_model: 品牌語言模型
        """
        self.language_model = language_model
        logger.debug(f"已設置品牌風格保持器的語言模型")
    
    def check_consistency(self, content: str, content_type: ContentType) -> Dict[str, Any]:
        """
        檢查內容與品牌風格的一致性。
        
        Args:
            content: 要檢查的內容文本
            content_type: 內容類型
            
        Returns:
            一致性檢查結果，包含得分和建議
        """
        if not self.brand_model:
            logger.warning("未設置品牌模型，無法進行風格一致性檢查")
            return {
                "consistency_score": 0.0,
                "suggestions": ["請先設置品牌模型"],
                "details": {}
            }
        
        # 初始化結果
        result = {
            "consistency_score": 0.0,
            "suggestions": [],
            "details": {}
        }
        
        # 1. 關鍵詞檢查
        keyword_score, keyword_details = self._check_keywords(content)
        result["details"]["keywords"] = keyword_details
        
        # 2. 語句長度檢查
        sentence_length_score, sentence_length_details = self._check_sentence_length(content)
        result["details"]["sentence_length"] = sentence_length_details
        
        # 3. 風格屬性檢查
        style_score, style_details = self._check_style_attributes(content)
        result["details"]["style"] = style_details
        
        # 4. 語言模型評分（如果有）
        model_score = 0.0
        if self.language_model:
            model_score = self.language_model.score_text(content)
            result["details"]["model_score"] = model_score
        
        # 計算總體一致性得分
        weights = {
            "keywords": 0.2,
            "sentence_length": 0.1,
            "style": 0.3,
            "model": 0.4 if self.language_model else 0.0
        }
        
        # 調整其他權重，如果沒有語言模型
        if not self.language_model:
            weights["keywords"] = 0.4
            weights["sentence_length"] = 0.2
            weights["style"] = 0.4
        
        total_score = (
            keyword_score * weights["keywords"] +
            sentence_length_score * weights["sentence_length"] +
            style_score * weights["style"] +
            model_score * weights["model"]
        )
        
        result["consistency_score"] = total_score
        
        # 生成建議
        suggestions = []
        
        # 關鍵詞建議
        if keyword_score < 0.5 and self.brand_model.keywords:
            missing_keywords = keyword_details.get("missing_keywords", [])
            if missing_keywords:
                suggestions.append(f"考慮增加關鍵詞: {', '.join(missing_keywords[:3])}")
        
        # 句長建議
        if sentence_length_score < 0.5:
            if sentence_length_details.get("avg_length", 0) > sentence_length_details.get("ideal_length", 15):
                suggestions.append("縮短句子長度，使用更簡潔的表達")
            else:
                suggestions.append("擴展句子長度，添加更多細節或描述")
        
        # 風格建議
        if style_score < 0.5:
            for attr, detail in style_details.get("attributes", {}).items():
                if detail.get("score", 0) < 0.4:
                    suggestions.append(f"增強 '{attr}' 風格特徵: {detail.get('suggestion', '')}")
        
        # 整體建議
        if total_score < 0.4:
            suggestions.append("內容與品牌風格差異較大，建議重新創作")
        elif total_score < 0.7:
            suggestions.append("內容部分符合品牌風格，需要修改調整")
        
        result["suggestions"] = suggestions
        
        return result
    
    def enhance_consistency(self, content: str, content_type: ContentType) -> str:
        """
        增強內容與品牌風格的一致性。
        
        Args:
            content: 原始內容
            content_type: 內容類型
            
        Returns:
            增強後的內容
        """
        if not self.brand_model or not self.language_model:
            logger.warning("未設置品牌模型或語言模型，無法增強風格一致性")
            return content
        
        # 基本檢查
        check_result = self.check_consistency(content, content_type)
        
        # 如果一致性已經很高，不需要增強
        if check_result["consistency_score"] > 0.85:
            logger.debug("內容已經高度符合品牌風格，不需要增強")
            return content
        
        # 使用語言模型進行風格增強
        enhanced_content = self.language_model.enhance_text(
            content, 
            brand_style=True,
            keywords=self.brand_model.keywords,
            style_attributes={attr.name: attr.value for attr in self.brand_model.style_attributes}
        )
        
        logger.debug(f"已增強內容風格一致性，原始長度: {len(content)}，增強後長度: {len(enhanced_content)}")
        return enhanced_content
    
    def _check_keywords(self, content: str) -> Tuple[float, Dict[str, Any]]:
        """
        檢查內容是否包含品牌關鍵詞。
        
        Args:
            content: 要檢查的內容
            
        Returns:
            (得分, 詳細信息)
        """
        if not self.brand_model or not self.brand_model.keywords:
            return 1.0, {"status": "未設置品牌關鍵詞"}
        
        # 預處理內容
        words = word_tokenize(content.lower())
        words = [w for w in words if w not in self.stop_words and w not in string.punctuation]
        word_set = set(words)
        
        # 檢查關鍵詞
        found_keywords = []
        missing_keywords = []
        
        for keyword in self.brand_model.keywords:
            if keyword.lower() in content.lower():
                found_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)
        
        # 計算得分
        if not self.brand_model.keywords:
            score = 1.0
        else:
            score = len(found_keywords) / len(self.brand_model.keywords)
        
        return score, {
            "found_keywords": found_keywords,
            "missing_keywords": missing_keywords,
            "coverage": f"{len(found_keywords)}/{len(self.brand_model.keywords)}"
        }
    
    def _check_sentence_length(self, content: str) -> Tuple[float, Dict[str, Any]]:
        """
        檢查句子長度是否符合品牌風格。
        
        Args:
            content: 要檢查的內容
            
        Returns:
            (得分, 詳細信息)
        """
        # 分割句子
        sentences = sent_tokenize(content)
        
        if not sentences:
            return 0.0, {"status": "無內容"}
        
        # 計算句子長度
        lengths = [len(word_tokenize(s)) for s in sentences]
        avg_length = sum(lengths) / len(lengths)
        
        # 理想句長（可以從品牌模型中獲取，或根據行業設置）
        ideal_length = 15
        for attr in self.brand_model.style_attributes if self.brand_model else []:
            if attr.name.lower() in ["簡潔", "簡短", "concise", "brief"]:
                ideal_length = 10 * (1 - attr.value) + 6
            elif attr.name.lower() in ["詳細", "詳盡", "detailed", "elaborate"]:
                ideal_length = 15 + 10 * attr.value
        
        # 計算得分（越接近理想長度得分越高）
        deviation = abs(avg_length - ideal_length) / ideal_length
        score = max(0, 1 - deviation)
        
        return score, {
            "avg_length": avg_length,
            "ideal_length": ideal_length,
            "min_length": min(lengths),
            "max_length": max(lengths),
            "sentence_count": len(sentences)
        }
    
    def _check_style_attributes(self, content: str) -> Tuple[float, Dict[str, Any]]:
        """
        檢查內容是否符合品牌風格屬性。
        
        Args:
            content: 要檢查的內容
            
        Returns:
            (得分, 詳細信息)
        """
        if not self.brand_model or not self.brand_model.style_attributes:
            return 1.0, {"status": "未設置品牌風格屬性"}
        
        # 風格屬性評分
        attributes = {}
        total_score = 0.0
        
        for attr in self.brand_model.style_attributes:
            attr_score, suggestion = self._evaluate_attribute(content, attr.name, attr.value)
            attributes[attr.name] = {
                "target_value": attr.value,
                "score": attr_score,
                "suggestion": suggestion
            }
            total_score += attr_score
        
        # 計算平均得分
        avg_score = total_score / len(self.brand_model.style_attributes) if self.brand_model.style_attributes else 1.0
        
        return avg_score, {
            "attributes": attributes,
            "overall_score": avg_score
        }
    
    def _evaluate_attribute(self, content: str, attribute: str, target_value: float) -> Tuple[float, str]:
        """
        評估內容在特定風格屬性上的得分。
        
        Args:
            content: 要評估的內容
            attribute: 風格屬性名稱
            target_value: 目標值（0-1）
            
        Returns:
            (得分, 改進建議)
        """
        # 這裡根據不同的風格屬性使用不同的評估方法
        # 下面是一些常見屬性的示例評估方法
        
        attribute_lower = attribute.lower()
        
        # 正式/非正式程度
        if attribute_lower in ["正式", "formal"]:
            score = self._evaluate_formality(content)
            suggestion = "使用更正式的用語和句式" if score < target_value else "略微減少正式程度"
        
        # 專業程度
        elif attribute_lower in ["專業", "professional"]:
            score = self._evaluate_professionalism(content)
            suggestion = "增加專業術語和行業詞彙" if score < target_value else "簡化一些專業術語"
        
        # 幽默程度
        elif attribute_lower in ["幽默", "humorous"]:
            score = self._evaluate_humor(content)
            suggestion = "增加一些輕鬆、幽默的表達" if score < target_value else "減少幽默元素，增加正式內容"
        
        # 情感程度
        elif attribute_lower in ["情感", "emotional"]:
            score = self._evaluate_emotion(content)
            suggestion = "使用更具情感的語言和表達" if score < target_value else "使用更客觀、中性的語言"
        
        # 簡潔程度
        elif attribute_lower in ["簡潔", "concise"]:
            score = self._evaluate_conciseness(content)
            suggestion = "精簡內容，刪除冗餘表達" if score < target_value else "添加更多細節和描述"
        
        # 直接程度
        elif attribute_lower in ["直接", "direct"]:
            score = self._evaluate_directness(content)
            suggestion = "更直接地表達主要觀點" if score < target_value else "使用更委婉、間接的表達方式"
        
        # 默認情況
        else:
            score = 0.5  # 無法評估時給出中間值
            suggestion = f"調整 '{attribute}' 特性以符合品牌風格"
        
        # 計算差距並評分
        gap = abs(score - target_value)
        final_score = max(0, 1 - gap)
        
        return final_score, suggestion
    
    def _evaluate_formality(self, content: str) -> float:
        """評估內容的正式程度。"""
        # 正式標記詞
        formal_markers = ["furthermore", "therefore", "consequently", "nevertheless", "regarding", 
                         "accordingly", "hereby", "thus", "hence", "wherein"]
        # 非正式標記詞
        informal_markers = ["anyway", "well", "you know", "kind of", "sort of", "like", "stuff", 
                           "thing", "okay", "OK", "guys", "pretty", "really", "gonna", "wanna"]
        
        # 計算標記詞出現頻率
        content_lower = content.lower()
        formal_count = sum(content_lower.count(marker) for marker in formal_markers)
        informal_count = sum(content_lower.count(marker) for marker in informal_markers)
        
        # 收縮形式（如 don't, can't）通常表示非正式
        contractions = ["n't", "'ll", "'re", "'ve", "'m", "'d"]
        contraction_count = sum(content_lower.count(c) for c in contractions)
        
        informal_count += contraction_count
        
        # 計算正式程度得分
        if formal_count + informal_count == 0:
            return 0.5  # 默認中等正式程度
        
        formality_score = formal_count / (formal_count + informal_count) if formal_count + informal_count > 0 else 0.5
        
        # 句子複雜度也影響正式程度
        sentences = sent_tokenize(content)
        avg_length = sum(len(word_tokenize(s)) for s in sentences) / len(sentences) if sentences else 0
        
        # 長句子通常更正式
        length_factor = min(1.0, avg_length / 20)  # 20 詞的句子被視為相當正式
        
        # 組合得分
        combined_score = 0.7 * formality_score + 0.3 * length_factor
        
        return combined_score
    
    def _evaluate_professionalism(self, content: str) -> float:
        """評估內容的專業程度。"""
        # 簡化實現
        # 真實系統中可使用行業特定詞彙表和更複雜的指標
        
        content_lower = content.lower()
        
        # 專業標記詞（通用）
        professional_markers = ["analysis", "research", "data", "methodology", "results", 
                              "implement", "strategy", "objective", "criteria", "evaluation"]
        
        # 計算標記詞出現頻率
        marker_count = sum(content_lower.count(marker) for marker in professional_markers)
        
        # 專業度根據標記詞密度計算
        words = word_tokenize(content_lower)
        word_count = len(words)
        
        if word_count == 0:
            return 0.0
        
        density = marker_count / word_count
        
        # 根據密度計算專業度得分
        professionalism_score = min(1.0, density * 20)  # 調整為合理範圍
        
        return professionalism_score
    
    def _evaluate_humor(self, content: str) -> float:
        """評估內容的幽默程度。"""
        # 簡化實現
        content_lower = content.lower()
        
        # 幽默標記
        humor_markers = ["laugh", "funny", "joke", "humor", "witty", "haha", "lol", "smile", 
                        "amusing", "hilarious", "ironic", "sarcastic", "playful", "teasing"]
        
        # 標點符號（感嘆號和問號可能表示幽默或誇張）
        exclamations = content.count('!')
        questions = content.count('?')
        
        # 計算標記詞出現頻率
        marker_count = sum(content_lower.count(marker) for marker in humor_markers)
        
        # 根據標記詞和標點符號計算幽默度
        humor_score = min(1.0, (marker_count * 0.3 + exclamations * 0.1 + questions * 0.05))
        
        return humor_score
    
    def _evaluate_emotion(self, content: str) -> float:
        """評估內容的情感程度。"""
        # 簡化實現
        content_lower = content.lower()
        
        # 情感詞表（正面和負面）
        emotional_words = ["love", "hate", "excited", "thrilled", "amazing", "terrible", "wonderful", 
                          "awful", "delighted", "disappointed", "happy", "sad", "angry", "joyful", 
                          "proud", "ashamed", "grateful", "hurt", "inspired", "devastated"]
        
        # 情感標點符號
        exclamations = content.count('!')
        
        # 計算情感詞出現頻率
        emotion_count = sum(content_lower.count(word) for word in emotional_words)
        
        # 計算情感得分
        words = word_tokenize(content_lower)
        word_count = len(words)
        
        if word_count == 0:
            return 0.0
        
        emotion_density = emotion_count / word_count
        emotion_score = min(1.0, emotion_density * 15 + exclamations * 0.1)
        
        return emotion_score
    
    def _evaluate_conciseness(self, content: str) -> float:
        """評估內容的簡潔程度。"""
        # 簡化實現
        
        # 分析句子長度
        sentences = sent_tokenize(content)
        if not sentences:
            return 0.0
        
        # 計算平均句長
        avg_length = sum(len(word_tokenize(s)) for s in sentences) / len(sentences)
        
        # 計算冗詞
        content_lower = content.lower()
        filler_words = ["basically", "actually", "literally", "virtually", "definitely", 
                       "certainly", "probably", "essentially", "totally", "completely", 
                       "absolutely", "really", "very", "quite", "somewhat", "rather"]
        
        filler_count = sum(content_lower.count(word) for word in filler_words)
        
        # 根據句長和冗詞計算簡潔度（反向關係）
        length_factor = max(0, 1 - (avg_length / 20))  # 20詞以上被視為較長
        filler_factor = max(0, 1 - (filler_count / 10))  # 10個以上冗詞被視為較多
        
        conciseness_score = 0.7 * length_factor + 0.3 * filler_factor
        
        return conciseness_score
    
    def _evaluate_directness(self, content: str) -> float:
        """評估內容的直接程度。"""
        # 簡化實現
        content_lower = content.lower()
        
        # 間接表達標記
        indirect_markers = ["perhaps", "maybe", "might", "could", "possibly", "potentially", 
                          "seemingly", "appears to", "it seems", "somewhat", "rather", 
                          "in a sense", "from a certain perspective", "one might say"]
        
        # 直接表達標記
        direct_markers = ["definitely", "absolutely", "certainly", "clearly", "obviously", 
                        "without doubt", "must", "always", "never", "undoubtedly"]
        
        # 疑問句比例（可能表示間接）
        sentences = sent_tokenize(content)
        question_count = sum(1 for s in sentences if s.strip().endswith('?'))
        question_ratio = question_count / len(sentences) if sentences else 0
        
        # 計算標記詞出現頻率
        indirect_count = sum(content_lower.count(marker) for marker in indirect_markers)
        direct_count = sum(content_lower.count(marker) for marker in direct_markers)
        
        # 計算直接度得分
        total_markers = indirect_count + direct_count
        if total_markers == 0:
            marker_score = 0.5  # 默認中等直接程度
        else:
            marker_score = direct_count / total_markers
        
        # 結合疑問句比例（疑問句多表示間接）
        directness_score = marker_score * (1 - question_ratio * 0.5)
        
        return directness_score


# 全局品牌風格保持器實例
brand_style_keeper = BrandStyleKeeper()
