#!/usr/bin/env python3
"""
LLM提供者基类
定义所有LLM提供者需要实现的接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional


class LLMProvider(ABC):
    """LLM提供者基类"""
    
    def __init__(self, **kwargs):
        """初始化LLM提供者"""
        self.config = kwargs
        
    @abstractmethod
    def is_available(self) -> bool:
        """检查LLM服务是否可用"""
        pass
        
    @abstractmethod
    def analyze_filename(self, filename: str) -> Dict[str, str]:
        """
        分析文件名并提供重命名建议
        
        Args:
            filename: 原始文件名
            
        Returns:
            Dict包含:
            - artist: 歌手名称 (如果未找到则为"未知")
            - language: 语言类型 (国语/粤语/英语，默认国语)
            - song_name: 歌曲名称 (最多20个汉字，先从原文件名中截取，如果超长则AI总结)
            - suggested_name: 建议的文件名格式 "歌手-语言-歌曲名"
            - confidence: 置信度 (0-1)
        """
        pass
        
    @abstractmethod
    def get_provider_name(self) -> str:
        """获取提供者名称"""
        pass 