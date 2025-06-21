#!/usr/bin/env python3
"""
GenAI配置管理
管理LLM提供者的配置信息
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class DeepseekConfig:
    """Deepseek配置"""
    api_key: str = ""
    api_base: str = "https://api.deepseek.com/v1"
    model: str = "deepseek-chat"
    enabled: bool = False


@dataclass
class OllamaConfig:
    """Ollama配置"""
    api_base: str = "http://localhost:11434"
    model: str = "qwen2.5:7b"
    enabled: bool = False


@dataclass
class AnalysisConfig:
    """分析配置"""
    confidence_threshold: float = 0.4
    max_song_name_length: int = 20
    default_language: str = "国语"
    skip_standard_format: bool = True


@dataclass
class GenAIConfig:
    """GenAI总配置"""
    enabled: bool = False
    default_provider: str = "ollama"  # deepseek 或 ollama
    deepseek: DeepseekConfig = None
    ollama: OllamaConfig = None
    analysis: AnalysisConfig = None
    
    def __post_init__(self):
        if self.deepseek is None:
            self.deepseek = DeepseekConfig()
        if self.ollama is None:
            self.ollama = OllamaConfig()
        if self.analysis is None:
            self.analysis = AnalysisConfig()


class ConfigManager:
    """配置管理器"""
    
    CONFIG_FILE = "genai_config.json"
    
    def __init__(self):
        self.config_path = Path.cwd() / self.CONFIG_FILE
        self.config = self.load_config()
        
    def load_config(self) -> GenAIConfig:
        """加载配置"""
        if not self.config_path.exists():
            # 创建默认配置
            return GenAIConfig()
            
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 创建配置对象
            deepseek_data = data.get('deepseek', {})
            ollama_data = data.get('ollama', {})
            analysis_data = data.get('analysis', {})
            
            config = GenAIConfig(
                enabled=data.get('enabled', False),
                default_provider=data.get('default_provider', 'ollama'),
                deepseek=DeepseekConfig(**deepseek_data),
                ollama=OllamaConfig(**ollama_data),
                analysis=AnalysisConfig(**analysis_data)
            )
            
            return config
            
        except Exception as e:
            # 配置文件损坏，返回默认配置
            return GenAIConfig()
            
    def save_config(self) -> bool:
        """保存配置"""
        try:
            data = {
                'enabled': self.config.enabled,
                'default_provider': self.config.default_provider,
                'deepseek': asdict(self.config.deepseek),
                'ollama': asdict(self.config.ollama),
                'analysis': asdict(self.config.analysis)
            }
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            return False
            
    def get_config(self) -> GenAIConfig:
        """获取当前配置"""
        return self.config
        
    def update_config(self, **kwargs) -> bool:
        """更新配置"""
        try:
            for key, value in kwargs.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
            return self.save_config()
        except Exception:
            return False
            
    def update_deepseek_config(self, **kwargs) -> bool:
        """更新Deepseek配置"""
        try:
            for key, value in kwargs.items():
                if hasattr(self.config.deepseek, key):
                    setattr(self.config.deepseek, key, value)
            return self.save_config()
        except Exception:
            return False
            
    def update_ollama_config(self, **kwargs) -> bool:
        """更新Ollama配置"""
        try:
            for key, value in kwargs.items():
                if hasattr(self.config.ollama, key):
                    setattr(self.config.ollama, key, value)
            return self.save_config()
        except Exception:
            return False
            
    def update_analysis_config(self, **kwargs) -> bool:
        """更新分析配置"""
        try:
            for key, value in kwargs.items():
                if hasattr(self.config.analysis, key):
                    setattr(self.config.analysis, key, value)
            return self.save_config()
        except Exception:
            return False
            
    def is_enabled(self) -> bool:
        """检查GenAI是否启用"""
        return self.config.enabled
        
    def get_active_provider_config(self) -> Optional[Dict]:
        """获取当前活动的提供者配置"""
        if not self.config.enabled:
            return None
            
        if self.config.default_provider == "deepseek" and self.config.deepseek.enabled:
            return {
                "provider": "deepseek",
                "config": self.config.deepseek
            }
        elif self.config.default_provider == "ollama" and self.config.ollama.enabled:
            return {
                "provider": "ollama", 
                "config": self.config.ollama
            }
            
        # 如果默认提供者不可用，尝试其他可用的提供者
        if self.config.deepseek.enabled:
            return {
                "provider": "deepseek",
                "config": self.config.deepseek
            }
        elif self.config.ollama.enabled:
            return {
                "provider": "ollama",
                "config": self.config.ollama
            }
            
        return None 