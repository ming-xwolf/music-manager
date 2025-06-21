#!/usr/bin/env python3
"""
主窗口类
包含应用的主界面逻辑和事件处理
"""

import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from typing import Dict

from core.audio_manager import AudioFileManager
from ui.components import StatusCards, FileList, SortOptions

# GenAI相关导入
try:
    from ui.genai_config_window import GenAIConfigWindow
    GENAI_UI_AVAILABLE = True
except ImportError:
    GENAI_UI_AVAILABLE = False
    GenAIConfigWindow = None


class MusicManagerMainWindow(ctk.CTk):
    """音频文件管理器主窗口"""
    
    def __init__(self):
        super().__init__()
        
        # 初始化组件
        self.audio_manager = AudioFileManager()
        self.current_analysis = None
        
        # UI组件
        self.path_entry = None
        self.analyze_button = None
        self.rename_button = None
        self.status_cards = None
        self.file_list = None
        self.sort_options = None
        self.progress_frame = None
        self.progress_bar = None
        self.progress_label = None
        
        self.setup_window()
        self.create_widgets()
        
    def setup_window(self):
        """设置窗口属性"""
        self.title("音频文件管理器")
        self.geometry("1200x900")
        self.minsize(1000, 800)
        
        # 设置窗口图标（如果有的话）
        # self.iconbitmap("icon.ico")
        
    def create_widgets(self):
        """创建所有UI组件"""
        # 标题
        self._create_title()
        
        # 文件夹选择区域
        self._create_folder_selection()
        
        # 排序选项
        self.sort_options = SortOptions(self, callback=self.on_sort_changed)
        self.sort_options.create_sort_options()
        
        # 操作按钮（放在排序选项后面）
        self._create_buttons()
        
        # 进度条（初始隐藏，放在按钮和GenAI状态之间）
        self._create_progress_bar()
        
        # GenAI状态显示
        self._create_genai_status()
        
        # 状态卡片
        self.status_cards = StatusCards(self)
        self.status_cards.create_status_cards()
        
        # 文件列表
        self.file_list = FileList(self)
        self.file_list.create_file_list()
        
    def _create_title(self):
        """创建标题区域"""
        title_frame = ctk.CTkFrame(self)
        title_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="音频文件管理器",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=10)
        
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="为音频文件自动添加序号前缀，支持多种排序方式",
            font=ctk.CTkFont(size=14)
        )
        subtitle_label.pack(pady=(0, 10))
        
    def _create_folder_selection(self):
        """创建文件夹选择区域"""
        folder_frame = ctk.CTkFrame(self)
        folder_frame.pack(fill="x", padx=20, pady=10)
        
        folder_label = ctk.CTkLabel(
            folder_frame, 
            text="选择音频文件夹:", 
            font=ctk.CTkFont(size=14)
        )
        folder_label.pack(side="left", padx=(20, 10), pady=10)
        
        self.path_entry = ctk.CTkEntry(
            folder_frame, 
            placeholder_text="请选择包含音频文件的文件夹..."
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=10)
        
        browse_button = ctk.CTkButton(
            folder_frame,
            text="浏览",
            command=self.browse_folder,
            width=80
        )
        browse_button.pack(side="right", padx=(0, 20), pady=10)
        
    def _create_buttons(self):
        """创建操作按钮"""
        buttons_frame = ctk.CTkFrame(self)
        buttons_frame.pack(fill="x", padx=20, pady=10)
        
        # 创建按钮容器，居中显示
        button_container = ctk.CTkFrame(buttons_frame)
        button_container.pack(pady=15)
        
        self.analyze_button = ctk.CTkButton(
            button_container,
            text="分析文件夹",
            command=self.analyze_folder,
            width=140,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.analyze_button.pack(side="left", padx=(20, 15), pady=10)
        
        self.rename_button = ctk.CTkButton(
            button_container,
            text="执行重命名",
            command=self.rename_files,
            width=140,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            state="disabled"
        )
        self.rename_button.pack(side="left", padx=(15, 10), pady=10)
        
        # GenAI配置按钮
        if GENAI_UI_AVAILABLE:
            self.genai_config_button = ctk.CTkButton(
                button_container,
                text="GenAI设置",
                command=self.open_genai_config,
                width=100,
                height=40,
                font=ctk.CTkFont(size=14)
            )
            self.genai_config_button.pack(side="left", padx=(10, 20), pady=10)
    
    def _create_progress_bar(self):
        """创建进度条"""
        self.progress_frame = ctk.CTkFrame(self)
        # 初始时不显示进度条
        
        # 进度条标签
        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="正在分析...",
            font=ctk.CTkFont(size=12)
        )
        self.progress_label.pack(pady=(10, 5))
        
        # 进度条
        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            width=400,
            height=20
        )
        self.progress_bar.pack(pady=(0, 10), padx=20)
        self.progress_bar.set(0)
        
    def show_progress(self):
        """显示进度条"""
        self.progress_frame.pack(fill="x", padx=20, pady=5, before=self.genai_status_frame)
        self.progress_bar.set(0)
        
    def hide_progress(self):
        """隐藏进度条"""
        self.progress_frame.pack_forget()
        
    def update_progress(self, progress: int, message: str):
        """更新进度条
        
        Args:
            progress: 进度百分比 (0-100)
            message: 进度消息
        """
        self.progress_bar.set(progress / 100.0)
        self.progress_label.configure(text=message)
        self.update_idletasks()  # 强制更新UI
        
    def _create_genai_status(self):
        """创建GenAI状态显示"""
        self.genai_status_frame = ctk.CTkFrame(self)
        self.genai_status_frame.pack(fill="x", padx=20, pady=5)
        
        # GenAI状态标签
        self.genai_status_label = ctk.CTkLabel(
            self.genai_status_frame,
            text="GenAI状态: 检查中...",
            font=ctk.CTkFont(size=12)
        )
        self.genai_status_label.pack(pady=8)
        
        # 初始更新状态
        self.update_genai_status()
        
    def update_genai_status(self):
        """更新GenAI状态显示"""
        if hasattr(self.audio_manager, 'get_genai_status'):
            status_info = self.audio_manager.get_genai_status()
            status = status_info.get("status", "unknown")
            message = status_info.get("message", "未知状态")
            
            # 根据状态设置不同的颜色
            color_map = {
                "available": "green",
                "disabled": "gray", 
                "unavailable": "red",
                "not_configured": "orange",
                "no_provider": "orange",
                "provider_unavailable": "red",
                "error": "red"
            }
            
            color = color_map.get(status, "gray")
            self.genai_status_label.configure(
                text=f"GenAI状态: {message}",
                text_color=color
            )
        else:
            self.genai_status_label.configure(
                text="GenAI状态: 不可用",
                text_color="red"
            )
            
    def open_genai_config(self):
        """打开GenAI配置窗口"""
        if GENAI_UI_AVAILABLE:
            config_window = GenAIConfigWindow(self)
            # 配置窗口关闭后更新状态
            self.wait_window(config_window)
            self.update_genai_status()
        
    def browse_folder(self):
        """浏览文件夹"""
        folder_path = filedialog.askdirectory(title="选择音频文件夹")
        if folder_path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder_path)
            # 自动分析文件夹
            self.analyze_folder()
            
    def on_sort_changed(self, value):
        """排序方式改变时的回调"""
        if self.path_entry.get().strip():
            self.refresh_analysis()
            
    def analyze_folder(self):
        """分析文件夹"""
        folder_path = self.path_entry.get().strip()
        if not folder_path:
            messagebox.showwarning("警告", "请先选择一个文件夹")
            return
            
        # 禁用按钮并显示进度条
        self.analyze_button.configure(state="disabled", text="分析中...")
        self.rename_button.configure(state="disabled")
        self.show_progress()
        
        def progress_callback(progress, message):
            """进度回调函数"""
            self.after(0, lambda: self.update_progress(progress, message))
        
        def analyze_thread():
            try:
                sort_method = self.sort_options.get_selected_sort()
                analysis = self.audio_manager.analyze_files(folder_path, sort_method, progress_callback)
                # 在主线程中更新UI
                self.after(0, lambda: self.update_analysis_results(analysis))
            except Exception as e:
                self.after(0, lambda: self.show_analysis_error(str(e)))
                
        threading.Thread(target=analyze_thread, daemon=True).start()
        
    def update_analysis_results(self, analysis: Dict):
        """更新分析结果"""
        self.current_analysis = analysis
        
        # 隐藏进度条
        self.hide_progress()
        
        # 更新状态卡片
        self.status_cards.update_status(analysis)
        
        # 更新文件列表
        self.file_list.update_file_list(analysis['files'])
        
        # 恢复按钮状态
        self.analyze_button.configure(state="normal", text="分析文件夹")
        
        # 根据需要重命名的文件数量决定是否启用重命名按钮
        if analysis['needs_rename_count'] > 0:
            self.rename_button.configure(state="normal")
        else:
            self.rename_button.configure(state="disabled")
            
    def show_analysis_error(self, error_msg: str):
        """显示分析错误"""
        # 隐藏进度条
        self.hide_progress()
        
        self.analyze_button.configure(state="normal", text="分析文件夹")
        messagebox.showerror("错误", f"分析文件夹时出错：{error_msg}")
        
    def rename_files(self):
        """重命名文件"""
        if not self.current_analysis:
            messagebox.showwarning("警告", "请先分析文件夹")
            return
            
        # 检查是否有文件需要重命名
        file_mappings = {}
        for file_info in self.current_analysis['files']:
            if file_info['original_name'] != file_info['suggested_name']:
                file_mappings[file_info['original_name']] = file_info['suggested_name']
                
        if not file_mappings:
            messagebox.showinfo("信息", "没有文件需要重命名")
            return
            
        # 确认对话框
        count = len(file_mappings)
        if not messagebox.askyesno(
            "确认重命名", 
            f"即将重命名 {count} 个文件，是否继续？"
        ):
            return
            
        # 禁用按钮并显示进度条
        self.rename_button.configure(state="disabled", text="重命名中...")
        self.analyze_button.configure(state="disabled")
        self.show_progress()
        
        def progress_callback(progress, message):
            """重命名进度回调函数"""
            self.after(0, lambda: self.update_progress(progress, message))
        
        def rename_thread():
            try:
                success_count, errors = self.audio_manager.rename_files(
                    self.current_analysis['folder_path'], 
                    file_mappings,
                    progress_callback
                )
                self.after(0, lambda: self.show_rename_results(success_count, errors))
            except Exception as e:
                self.after(0, lambda: self.show_rename_error(str(e)))
                
        threading.Thread(target=rename_thread, daemon=True).start()
        
    def show_rename_results(self, success_count: int, errors: list):
        """显示重命名结果"""
        # 隐藏进度条
        self.hide_progress()
        
        self.rename_button.configure(state="disabled", text="执行重命名")
        self.analyze_button.configure(state="normal")
        
        if errors:
            error_msg = f"成功重命名 {success_count} 个文件\n\n出现以下错误：\n" + "\n".join(errors)
            messagebox.showwarning("重命名完成", error_msg)
        else:
            messagebox.showinfo("重命名完成", f"成功重命名 {success_count} 个文件")
            
        # 重新分析文件夹
        self.refresh_analysis()
        
    def refresh_analysis(self):
        """刷新分析结果"""
        folder_path = self.path_entry.get().strip()
        if not folder_path:
            return
            
        def analyze_thread():
            try:
                sort_method = self.sort_options.get_selected_sort()
                analysis = self.audio_manager.analyze_files(folder_path, sort_method)
                self.after(0, lambda: self.update_analysis_results_silent(analysis))
            except Exception as e:
                # 静默处理错误，不显示错误对话框
                pass
                
        threading.Thread(target=analyze_thread, daemon=True).start()
        
    def update_analysis_results_silent(self, analysis: Dict):
        """静默更新分析结果（不恢复按钮状态）"""
        self.current_analysis = analysis
        
        # 更新状态卡片
        self.status_cards.update_status(analysis)
        
        # 更新文件列表
        self.file_list.update_file_list(analysis['files'])
        
        # 根据需要重命名的文件数量决定是否启用重命名按钮
        if analysis['needs_rename_count'] > 0:
            self.rename_button.configure(state="normal")
        else:
            self.rename_button.configure(state="disabled")
            
    def show_rename_error(self, error_msg: str):
        """显示重命名错误"""
        # 隐藏进度条
        self.hide_progress()
        
        self.rename_button.configure(state="disabled", text="执行重命名")
        self.analyze_button.configure(state="normal")
        messagebox.showerror("错误", f"重命名文件时出错：{error_msg}") 