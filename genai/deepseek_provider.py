#!/usr/bin/env python3
"""
Deepseek LLM提供者
通过Deepseek API进行文件名分析
"""

import requests
from typing import Dict
from .base import LLMProvider


class DeepseekProvider(LLMProvider):
    """Deepseek LLM提供者"""
    
    DEFAULT_API_BASE = "https://api.deepseek.com/v1"
    DEFAULT_MODEL = "deepseek-chat"
    
    def __init__(self, api_key: str, api_base: str = None, model: str = None, config_manager=None, **kwargs):
        """
        初始化Deepseek提供者
        
        Args:
            api_key: Deepseek API密钥
            api_base: API基础URL (可选)
            model: 模型名称 (可选)
            config_manager: 配置管理器实例
        """
        super().__init__(config_manager=config_manager, **kwargs)
        self.api_key = api_key
        self.api_base = api_base or self.DEFAULT_API_BASE
        self.model = model or self.DEFAULT_MODEL
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
        
    def is_available(self) -> bool:
        """检查Deepseek服务是否可用"""
        if not self.api_key:
            return False
            
        try:
            response = self.session.post(
                f"{self.api_base}/chat/completions",
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 5
                },
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False
            
    def _make_llm_request(self, prompt: str) -> str:
        """向Deepseek发送请求并获取响应"""
        response = self.session.post(
            f"{self.api_base}/chat/completions",
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 200,
                "temperature": 0.3
            },
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception("API请求失败")
            
        result = response.json()
        return result.get("choices", [{}])[0].get("message", {}).get("content", "")
        
    def get_provider_name(self) -> str:
        """获取提供者名称"""
        return "Deepseek" 