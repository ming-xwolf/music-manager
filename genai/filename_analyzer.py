#!/usr/bin/env python3
"""
文件名分析器
负责判断文件名格式并调用LLM进行分析
"""

import re
from typing import Dict, Optional, List
from pathlib import Path
from .base import LLMProvider


class FilenameAnalyzer:
    """文件名智能分析器"""
    
    # 标准格式正则表达式：歌手-语言-歌曲名
    STANDARD_FORMAT_PATTERN = r'^(.+?)-([国粤英]语|国语|粤语|英语)-(.+)$'
    
    def __init__(self, llm_provider: LLMProvider, config_manager=None):
        """
        初始化分析器
        
        Args:
            llm_provider: LLM提供者实例
            config_manager: 配置管理器实例
        """
        self.llm_provider = llm_provider
        self.config_manager = config_manager
    
    def _get_max_song_name_length(self) -> int:
        """获取歌曲名最大长度配置"""
        if self.config_manager and hasattr(self.config_manager, 'config'):
            return self.config_manager.config.analysis.max_song_name_length
        return 20  # 默认值
        
    def is_standard_format(self, filename: str) -> bool:
        """
        检查文件名是否已经符合标准格式
        
        Args:
            filename: 文件名（不含扩展名）
            
        Returns:
            bool: 是否符合标准格式
        """
        # 去除文件扩展名
        name_without_ext = Path(filename).stem
        
        # 去除数字前缀（如果有）
        clean_name = re.sub(r'^\d+-', '', name_without_ext)
        
        # 检查是否匹配标准格式
        return bool(re.match(self.STANDARD_FORMAT_PATTERN, clean_name))
        
    def analyze_filename(self, filename: str) -> Dict[str, str]:
        """
        分析单个文件名
        
        Args:
            filename: 文件名
            
        Returns:
            Dict: 分析结果，包含：
                - needs_analysis: 是否需要分析
                - is_standard_format: 是否已经是标准格式
                - original_name: 原始文件名
                - artist: 歌手名（如果分析了的话）
                - language: 语言类型（如果分析了的话）
                - song_name: 歌曲名（如果分析了的话）
                - suggested_name: 建议的文件名
                - confidence: 置信度（0-1）
                - provider: LLM提供者名称（如果使用了的话）
                - error: 错误信息（如果有的话）
        """
        # 去除文件扩展名进行分析
        name_without_ext = Path(filename).stem
        max_length = self._get_max_song_name_length()
        
        # 检查是否已经符合标准格式
        if self.is_standard_format(filename):
            return {
                "needs_analysis": False,
                "is_standard_format": True,
                "original_name": filename,
                "suggested_name": f"未知-国语-{name_without_ext[:max_length]}",
                "confidence": 1.0
            }
            
        # 使用LLM分析
        try:
            llm_result = self.llm_provider.analyze_filename(name_without_ext)
            
            result = {
                "needs_analysis": True,
                "is_standard_format": False,
                "original_name": filename,
                "artist": llm_result.get("artist", "未知"),
                "language": llm_result.get("language", "国语"),
                "song_name": llm_result.get("song_name", "未知歌曲"),
                "suggested_name": llm_result.get("suggested_name", f"未知-国语-{name_without_ext[:max_length]}"),
                "confidence": llm_result.get("confidence", 0.5),
                "provider": self.llm_provider.get_provider_name()
            }
            
            # 如果有错误信息，添加到结果中
            if "error" in llm_result:
                result["error"] = llm_result["error"]
                
            return result
            
        except Exception as e:
            return {
                "needs_analysis": True,
                "is_standard_format": False,
                "original_name": filename,
                "suggested_name": f"未知-国语-{name_without_ext[:max_length]}",
                "error": f"分析失败: {str(e)}",
                "confidence": 0.0
            }
            
    def batch_analyze(self, filenames: List[str]) -> List[Dict[str, str]]:
        """
        批量分析文件名
        
        Args:
            filenames: 文件名列表
            
        Returns:
            List[Dict]: 分析结果列表
        """
        results = []
        for filename in filenames:
            result = self.analyze_filename(filename)
            results.append(result)
        return results
        
    def get_analysis_stats(self, results: List[Dict[str, str]]) -> Dict[str, int]:
        """
        获取分析统计信息
        
        Args:
            results: 分析结果列表
            
        Returns:
            Dict: 统计信息
        """
        stats = {
            "total_files": len(results),
            "standard_format": 0,
            "needs_analysis": 0,
            "analysis_success": 0,
            "analysis_failed": 0,
            "skipped": 0
        }
        
        for result in results:
            if result.get("is_standard_format", False):
                stats["standard_format"] += 1
                stats["skipped"] += 1
            elif result.get("needs_analysis", False):
                stats["needs_analysis"] += 1
                if "error" in result:
                    stats["analysis_failed"] += 1
                else:
                    stats["analysis_success"] += 1
                    
        return stats 