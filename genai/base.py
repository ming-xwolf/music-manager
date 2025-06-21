#!/usr/bin/env python3
"""
LLM提供者基类
定义所有LLM提供者需要实现的接口，并提供通用的处理逻辑
"""

import json
import re
from abc import ABC, abstractmethod
from typing import Dict, Optional
from pathlib import Path


class LLMProvider(ABC):
    """LLM提供者基类"""
    
    def __init__(self, config_manager=None, **kwargs):
        """
        初始化LLM提供者
        
        Args:
            config_manager: 配置管理器实例
            **kwargs: 其他配置参数
        """
        self.config = kwargs
        self.config_manager = config_manager
        
    @abstractmethod
    def is_available(self) -> bool:
        """检查LLM服务是否可用"""
        pass
        
    @abstractmethod
    def _make_llm_request(self, prompt: str) -> str:
        """
        向LLM发送请求并获取响应
        
        Args:
            prompt: 分析提示词
            
        Returns:
            LLM的原始响应内容
            
        Raises:
            Exception: 请求失败时抛出异常
        """
        pass
        
    @abstractmethod
    def get_provider_name(self) -> str:
        """获取提供者名称"""
        pass
        
    def analyze_filename(self, filename: str) -> Dict[str, str]:
        """
        分析文件名并提供重命名建议
        
        Args:
            filename: 原始文件名
            
        Returns:
            Dict包含:
            - artist: 歌手名称 (单个歌手直接使用，多个歌手最多3个用空格连接，超过3个列出前3个加"等"，未找到则为"未知")
            - language: 语言类型 (国语/粤语/英语，默认国语)
            - song_name: 歌曲名称 (最多20个汉字，先从原文件名中截取，如果超长则AI总结)
            - suggested_name: 建议的文件名格式 "歌手-语言-歌曲名"
            - confidence: 置信度 (0-1)
        """
        try:
            prompt = self._create_analysis_prompt(filename)
            content = self._make_llm_request(prompt)
            return self._parse_llm_response(filename, content)
        except Exception as e:
            return self._create_error_result(filename, f"请求失败: {str(e)}")
    
    def _get_max_song_name_length(self) -> int:
        """获取歌曲名最大长度配置"""
        if self.config_manager and hasattr(self.config_manager, 'config'):
            return self.config_manager.config.analysis.max_song_name_length
        return 20  # 默认值
        
    def _process_artist_name(self, artist_name: str) -> str:
        """
        处理歌手名称，确保符合规则
        
        Args:
            artist_name: 原始歌手名称
            
        Returns:
            处理后的歌手名称
        """
        if not artist_name or artist_name.strip() == "":
            return "未知"
            
        artist_name = artist_name.strip()
        
        # 如果已经是"未知"，直接返回
        if artist_name == "未知":
            return artist_name
            
        # 分割歌手名称，支持多种分隔符
        separators = ['&', '、', '，', ',', '和', '与', 'feat.', 'ft.', 'featuring']
        artists = [artist_name]
        
        for sep in separators:
            new_artists = []
            for artist in artists:
                new_artists.extend([a.strip() for a in artist.split(sep) if a.strip()])
            artists = new_artists
            
        # 去重并保持顺序
        unique_artists = []
        for artist in artists:
            if artist and artist not in unique_artists:
                unique_artists.append(artist)
        
        # 应用规则
        if len(unique_artists) == 0:
            return "未知"
        elif len(unique_artists) == 1:
            return unique_artists[0]
        elif len(unique_artists) <= 3:
            return " ".join(unique_artists)
        else:
            return " ".join(unique_artists[:3]) + "等"
    
    def _process_song_name(self, song_name: str, original_filename: str) -> str:
        """
        处理歌曲名长度限制
        
        Args:
            song_name: AI提取的歌曲名
            original_filename: 原始文件名
            
        Returns:
            处理后的歌曲名
        """
        max_length = self._get_max_song_name_length()
        
        # 如果AI提取的歌曲名不超过最大长度，直接使用
        if len(song_name) <= max_length:
            return song_name
        
        # 如果超过最大长度，尝试从原文件名中截取
        # 去除扩展名
        name_without_ext = Path(original_filename).stem
        
        # 去除可能的数字前缀
        clean_name = re.sub(r'^\d+-', '', name_without_ext)
        
        # 如果原文件名不超过最大长度，使用原文件名
        if len(clean_name) <= max_length:
            return clean_name
        
        # 如果原文件名也超过最大长度，截取指定长度
        return song_name[:max_length]
    
    def _create_analysis_prompt(self, filename: str) -> str:
        """创建分析提示词"""
        max_length = self._get_max_song_name_length()
        return f"""
请分析这个音乐文件名："{filename}"

要求：
1. 识别歌手名称：
   - 如果是单个歌手，直接使用歌手名
   - 如果是多个歌手，最多列出3个歌手名，用空格连接，如"张三 李四 王五"
   - 如果超过3个歌手，列出前3个歌手名加"等"，如"张三 李四 王五等"
   - 如果无法确定则使用"未知"
2. 识别语言类型：国语、粤语、英语三种之一，默认国语
3. 识别歌曲名称，限制在{max_length}个汉字长度内，先从原文件名中截取，如果超长则给出合适的总结
4. 按照"歌手-语言-歌曲名"格式给出建议

请严格按照以下JSON格式回复，不要包含其他内容：
{{
    "artist": "歌手名称",
    "language": "语言类型",
    "song_name": "歌曲名称",
    "confidence": 0.8
}}
"""
    
    def _parse_llm_response(self, filename: str, content: str) -> Dict[str, str]:
        """解析LLM响应"""
        try:
            # 尝试提取JSON内容
            json_match = re.search(r'\{[^}]+\}', content)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                
                artist = data.get("artist", "未知").strip()
                language = data.get("language", "国语").strip()
                song_name = data.get("song_name", "未知歌曲").strip()
                confidence = float(data.get("confidence", 0.5))
                
                # 验证语言类型
                if language not in ["国语", "粤语", "英语"]:
                    language = "国语"
                
                # 处理歌手名称
                artist = self._process_artist_name(artist)
                
                # 处理歌曲名长度限制
                song_name = self._process_song_name(song_name, filename)
                
                suggested_name = f"{artist}-{language}-{song_name}"
                
                return {
                    "artist": artist,
                    "language": language,
                    "song_name": song_name,
                    "suggested_name": suggested_name,
                    "confidence": confidence
                }
                
        except Exception as e:
            pass
            
        return self._create_error_result(filename, "响应解析失败")
    
    def _create_error_result(self, filename: str, error: str) -> Dict[str, str]:
        """创建错误结果"""
        return {
            "artist": "未知",
            "language": "国语",
            "song_name": "解析失败",
            "suggested_name": f"未知-国语-解析失败",
            "confidence": 0.0,
            "error": error
        }