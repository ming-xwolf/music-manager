#!/usr/bin/env python3
"""
Ollama LLM提供者
通过本地Ollama服务进行文件名分析
"""

import requests
import json
import re
from typing import Dict, Optional
from .base import LLMProvider


class OllamaProvider(LLMProvider):
    """Ollama LLM提供者"""
    
    DEFAULT_API_BASE = "http://localhost:11434"
    DEFAULT_MODEL = "qwen2.5:7b"
    
    def __init__(self, api_base: str = None, model: str = None, config_manager=None, **kwargs):
        """
        初始化Ollama提供者
        
        Args:
            api_base: Ollama API基础URL (默认: http://localhost:11434)
            model: 模型名称 (默认: qwen2.5:7b)
            config_manager: 配置管理器实例
        """
        super().__init__(**kwargs)
        self.api_base = api_base or self.DEFAULT_API_BASE
        self.model = model or self.DEFAULT_MODEL
        self.config_manager = config_manager
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json"
        })
        
    def is_available(self) -> bool:
        """检查Ollama服务是否可用"""
        try:
            # 检查Ollama服务是否运行
            response = self.session.get(f"{self.api_base}/api/tags", timeout=5)
            if response.status_code != 200:
                return False
                
            # 检查模型是否可用
            response = self.session.post(
                f"{self.api_base}/api/generate",
                json={
                    "model": self.model,
                    "prompt": "test",
                    "stream": False,
                    "options": {"num_predict": 1}
                },
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False
            
    def analyze_filename(self, filename: str) -> Dict[str, str]:
        """使用Ollama分析文件名"""
        try:
            prompt = self._create_analysis_prompt(filename)
            
            response = self.session.post(
                f"{self.api_base}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 200,
                        "top_p": 0.9
                    }
                },
                timeout=60
            )
            
            if response.status_code != 200:
                return self._create_error_result(filename, "API请求失败")
                
            result = response.json()
            content = result.get("response", "")
            
            return self._parse_llm_response(filename, content)
            
        except Exception as e:
            return self._create_error_result(filename, f"请求失败: {str(e)}")
            
    def _get_max_song_name_length(self) -> int:
        """获取歌曲名最大长度配置"""
        if self.config_manager and hasattr(self.config_manager, 'config'):
            return self.config_manager.config.analysis.max_song_name_length
        return 20  # 默认值
        
    def _create_analysis_prompt(self, filename: str) -> str:
        """创建分析提示词"""
        max_length = self._get_max_song_name_length()
        return f"""
请分析这个音乐文件名："{filename}"

要求：
1. 识别歌手名称，如果无法确定则使用"未知"
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
        from pathlib import Path
        name_without_ext = Path(original_filename).stem
        
        # 去除可能的数字前缀
        clean_name = re.sub(r'^\d+-', '', name_without_ext)
        
        # 如果原文件名不超过最大长度，使用原文件名
        if len(clean_name) <= max_length:
            return clean_name
        
        # 如果原文件名也超过最大长度，截取指定长度
        return song_name[:max_length]
        
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
        
    def get_provider_name(self) -> str:
        """获取提供者名称"""
        return "Ollama" 