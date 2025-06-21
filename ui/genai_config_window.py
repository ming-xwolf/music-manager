#!/usr/bin/env python3
"""
GenAI配置窗口
用于配置LLM提供者设置
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from typing import Dict, Optional

try:
    from genai.config import ConfigManager
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    ConfigManager = None


class GenAIConfigWindow(ctk.CTkToplevel):
    """GenAI配置窗口"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.parent = parent
        self.config_manager = None
        
        if not GENAI_AVAILABLE:
            messagebox.showerror("错误", "GenAI模块不可用")
            self.destroy()
            return
            
        try:
            self.config_manager = ConfigManager()
        except Exception as e:
            messagebox.showerror("错误", f"无法加载配置: {str(e)}")
            self.destroy()
            return
            
        self.setup_window()
        self.create_widgets()
        self.load_current_config()
        
    def setup_window(self):
        """设置窗口属性"""
        self.title("GenAI 配置")
        self.geometry("600x700")
        self.resizable(False, False)
        
        # 设置窗口居中
        self.transient(self.parent)
        self.grab_set()
        
    def create_widgets(self):
        """创建UI组件"""
        # 主框架
        main_frame = ctk.CTkScrollableFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 标题
        title_label = ctk.CTkLabel(
            main_frame,
            text="GenAI 智能文件名分析配置",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # 总开关
        self._create_general_settings(main_frame)
        
        # Deepseek配置
        self._create_deepseek_settings(main_frame)
        
        # Ollama配置
        self._create_ollama_settings(main_frame)
        
        # 按钮区域
        self._create_buttons(main_frame)
        
    def _create_general_settings(self, parent):
        """创建通用设置"""
        general_frame = ctk.CTkFrame(parent)
        general_frame.pack(fill="x", pady=(0, 20))
        
        # 标题
        general_title = ctk.CTkLabel(
            general_frame,
            text="🔧 通用设置",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        general_title.pack(pady=(15, 10))
        
        # 启用开关
        enable_frame = ctk.CTkFrame(general_frame)
        enable_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        enable_label = ctk.CTkLabel(enable_frame, text="启用GenAI功能:")
        enable_label.pack(side="left", padx=10, pady=10)
        
        self.enable_var = tk.BooleanVar()
        self.enable_switch = ctk.CTkSwitch(
            enable_frame,
            text="",
            variable=self.enable_var,
            command=self._on_enable_changed
        )
        self.enable_switch.pack(side="right", padx=10, pady=10)
        
        # 默认提供者选择
        provider_frame = ctk.CTkFrame(general_frame)
        provider_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        provider_label = ctk.CTkLabel(provider_frame, text="默认提供者:")
        provider_label.pack(side="left", padx=10, pady=10)
        
        self.provider_var = tk.StringVar(value="ollama")
        self.provider_menu = ctk.CTkOptionMenu(
            provider_frame,
            variable=self.provider_var,
            values=["deepseek", "ollama"]
        )
        self.provider_menu.pack(side="right", padx=10, pady=10)
        
    def _create_deepseek_settings(self, parent):
        """创建Deepseek设置"""
        deepseek_frame = ctk.CTkFrame(parent)
        deepseek_frame.pack(fill="x", pady=(0, 20))
        
        # 标题
        deepseek_title = ctk.CTkLabel(
            deepseek_frame,
            text="🤖 Deepseek 配置",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        deepseek_title.pack(pady=(15, 10))
        
        # 启用开关
        deepseek_enable_frame = ctk.CTkFrame(deepseek_frame)
        deepseek_enable_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        deepseek_enable_label = ctk.CTkLabel(deepseek_enable_frame, text="启用Deepseek:")
        deepseek_enable_label.pack(side="left", padx=10, pady=10)
        
        self.deepseek_enable_var = tk.BooleanVar()
        self.deepseek_enable_switch = ctk.CTkSwitch(
            deepseek_enable_frame,
            text="",
            variable=self.deepseek_enable_var
        )
        self.deepseek_enable_switch.pack(side="right", padx=10, pady=10)
        
        # API密钥
        api_key_frame = ctk.CTkFrame(deepseek_frame)
        api_key_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        api_key_label = ctk.CTkLabel(api_key_frame, text="API密钥:")
        api_key_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.deepseek_api_key_entry = ctk.CTkEntry(
            api_key_frame,
            placeholder_text="请输入Deepseek API密钥",
            show="*"
        )
        self.deepseek_api_key_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # API基础URL
        api_base_frame = ctk.CTkFrame(deepseek_frame)
        api_base_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        api_base_label = ctk.CTkLabel(api_base_frame, text="API基础URL:")
        api_base_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.deepseek_api_base_entry = ctk.CTkEntry(
            api_base_frame,
            placeholder_text="https://api.deepseek.com/v1"
        )
        self.deepseek_api_base_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # 模型
        model_frame = ctk.CTkFrame(deepseek_frame)
        model_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        model_label = ctk.CTkLabel(model_frame, text="模型:")
        model_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.deepseek_model_entry = ctk.CTkEntry(
            model_frame,
            placeholder_text="deepseek-chat"
        )
        self.deepseek_model_entry.pack(fill="x", padx=10, pady=(0, 10))
        
    def _create_ollama_settings(self, parent):
        """创建Ollama设置"""
        ollama_frame = ctk.CTkFrame(parent)
        ollama_frame.pack(fill="x", pady=(0, 20))
        
        # 标题
        ollama_title = ctk.CTkLabel(
            ollama_frame,
            text="🦙 Ollama 配置",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        ollama_title.pack(pady=(15, 10))
        
        # 启用开关
        ollama_enable_frame = ctk.CTkFrame(ollama_frame)
        ollama_enable_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        ollama_enable_label = ctk.CTkLabel(ollama_enable_frame, text="启用Ollama:")
        ollama_enable_label.pack(side="left", padx=10, pady=10)
        
        self.ollama_enable_var = tk.BooleanVar()
        self.ollama_enable_switch = ctk.CTkSwitch(
            ollama_enable_frame,
            text="",
            variable=self.ollama_enable_var
        )
        self.ollama_enable_switch.pack(side="right", padx=10, pady=10)
        
        # API基础URL
        ollama_api_base_frame = ctk.CTkFrame(ollama_frame)
        ollama_api_base_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        ollama_api_base_label = ctk.CTkLabel(ollama_api_base_frame, text="API基础URL:")
        ollama_api_base_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.ollama_api_base_entry = ctk.CTkEntry(
            ollama_api_base_frame,
            placeholder_text="http://localhost:11434"
        )
        self.ollama_api_base_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # 模型
        ollama_model_frame = ctk.CTkFrame(ollama_frame)
        ollama_model_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        ollama_model_label = ctk.CTkLabel(ollama_model_frame, text="模型:")
        ollama_model_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.ollama_model_entry = ctk.CTkEntry(
            ollama_model_frame,
            placeholder_text="qwen2.5:7b"
        )
        self.ollama_model_entry.pack(fill="x", padx=10, pady=(0, 10))
        
    def _create_buttons(self, parent):
        """创建按钮区域"""
        button_frame = ctk.CTkFrame(parent)
        button_frame.pack(fill="x", pady=20)
        
        # 按钮容器
        button_container = ctk.CTkFrame(button_frame)
        button_container.pack(pady=15)
        
        # 测试连接按钮
        self.test_button = ctk.CTkButton(
            button_container,
            text="测试连接",
            command=self._test_connection,
            width=100
        )
        self.test_button.pack(side="left", padx=(20, 10), pady=10)
        
        # 保存按钮
        self.save_button = ctk.CTkButton(
            button_container,
            text="保存配置",
            command=self._save_config,
            width=100
        )
        self.save_button.pack(side="left", padx=(10, 10), pady=10)
        
        # 取消按钮
        self.cancel_button = ctk.CTkButton(
            button_container,
            text="取消",
            command=self.destroy,
            width=100
        )
        self.cancel_button.pack(side="left", padx=(10, 20), pady=10)
        
    def load_current_config(self):
        """加载当前配置"""
        config = self.config_manager.get_config()
        
        # 通用设置
        self.enable_var.set(config.enabled)
        self.provider_var.set(config.default_provider)
        
        # Deepseek设置
        self.deepseek_enable_var.set(config.deepseek.enabled)
        self.deepseek_api_key_entry.insert(0, config.deepseek.api_key)
        self.deepseek_api_base_entry.insert(0, config.deepseek.api_base)
        self.deepseek_model_entry.insert(0, config.deepseek.model)
        
        # Ollama设置
        self.ollama_enable_var.set(config.ollama.enabled)
        self.ollama_api_base_entry.insert(0, config.ollama.api_base)
        self.ollama_model_entry.insert(0, config.ollama.model)
        
        self._update_ui_state()
        
    def _on_enable_changed(self):
        """启用状态改变时的回调"""
        self._update_ui_state()
        
    def _update_ui_state(self):
        """更新UI状态"""
        enabled = self.enable_var.get()
        
        # 根据总开关状态启用/禁用相关控件
        widgets_to_toggle = [
            self.provider_menu,
            self.deepseek_enable_switch,
            self.deepseek_api_key_entry,
            self.deepseek_api_base_entry,
            self.deepseek_model_entry,
            self.ollama_enable_switch,
            self.ollama_api_base_entry,
            self.ollama_model_entry
        ]
        
        for widget in widgets_to_toggle:
            if enabled:
                widget.configure(state="normal")
            else:
                widget.configure(state="disabled")
                
    def _test_connection(self):
        """测试连接"""
        if not self.enable_var.get():
            messagebox.showwarning("警告", "请先启用GenAI功能")
            return
            
        # 临时保存当前配置进行测试
        temp_config = self._get_current_form_data()
        if not temp_config:
            return
            
        # 测试当前选中的提供者
        provider = self.provider_var.get()
        
        try:
            if provider == "deepseek":
                if not self.deepseek_enable_var.get():
                    messagebox.showwarning("警告", "Deepseek未启用")
                    return
                    
                from genai.deepseek_provider import DeepseekProvider
                provider_obj = DeepseekProvider(
                    api_key=temp_config["deepseek"]["api_key"],
                    api_base=temp_config["deepseek"]["api_base"],
                    model=temp_config["deepseek"]["model"]
                )
                
            elif provider == "ollama":
                if not self.ollama_enable_var.get():
                    messagebox.showwarning("警告", "Ollama未启用")
                    return
                    
                from genai.ollama_provider import OllamaProvider
                provider_obj = OllamaProvider(
                    api_base=temp_config["ollama"]["api_base"],
                    model=temp_config["ollama"]["model"]
                )
                
            # 测试连接
            self.test_button.configure(text="测试中...", state="disabled")
            self.update()
            
            if provider_obj.is_available():
                messagebox.showinfo("成功", f"{provider.capitalize()} 连接测试成功！")
            else:
                messagebox.showerror("失败", f"{provider.capitalize()} 连接测试失败")
                
        except Exception as e:
            messagebox.showerror("错误", f"测试连接时出错: {str(e)}")
        finally:
            self.test_button.configure(text="测试连接", state="normal")
            
    def _get_current_form_data(self) -> Optional[Dict]:
        """获取当前表单数据"""
        # 验证必填字段
        if self.enable_var.get():
            if self.deepseek_enable_var.get():
                if not self.deepseek_api_key_entry.get().strip():
                    messagebox.showerror("错误", "Deepseek API密钥不能为空")
                    return None
                    
        return {
            "enabled": self.enable_var.get(),
            "default_provider": self.provider_var.get(),
            "deepseek": {
                "enabled": self.deepseek_enable_var.get(),
                "api_key": self.deepseek_api_key_entry.get().strip(),
                "api_base": self.deepseek_api_base_entry.get().strip() or "https://api.deepseek.com/v1",
                "model": self.deepseek_model_entry.get().strip() or "deepseek-chat"
            },
            "ollama": {
                "enabled": self.ollama_enable_var.get(),
                "api_base": self.ollama_api_base_entry.get().strip() or "http://localhost:11434",
                "model": self.ollama_model_entry.get().strip() or "qwen2.5:7b"
            }
        }
        
    def _save_config(self):
        """保存配置"""
        config_data = self._get_current_form_data()
        if not config_data:
            return
            
        try:
            # 更新配置
            self.config_manager.update_config(
                enabled=config_data["enabled"],
                default_provider=config_data["default_provider"]
            )
            
            self.config_manager.update_deepseek_config(**config_data["deepseek"])
            self.config_manager.update_ollama_config(**config_data["ollama"])
            
            messagebox.showinfo("成功", "配置已保存！")
            
            # 通知父窗口重新初始化GenAI
            if hasattr(self.parent, 'audio_manager'):
                self.parent.audio_manager._init_genai()
                
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("错误", f"保存配置时出错: {str(e)}") 