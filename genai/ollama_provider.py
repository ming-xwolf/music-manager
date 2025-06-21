#!/usr/bin/env python3
"""
Ollama LLM提供者
通过本地Ollama服务进行文件名分析
"""

import requests
from typing import Dict
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
        super().__init__(config_manager=config_manager, **kwargs)
        self.api_base = api_base or self.DEFAULT_API_BASE
        self.model = model or self.DEFAULT_MODEL
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
            
    def _make_llm_request(self, prompt: str) -> str:
        """向Ollama发送请求并获取响应"""
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
            raise Exception("API请求失败")
            
        result = response.json()
        return result.get("response", "")
        
    def get_provider_name(self) -> str:
        """获取提供者名称"""
        return "Ollama" 