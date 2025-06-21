#!/usr/bin/env python3
"""
UI组件类
包含各种UI组件的创建和管理
"""

import customtkinter as ctk
import tkinter as tk
from typing import List, Dict
from utils.formatters import format_file_size, format_time, format_status


class StatusCards:
    """状态卡片组件"""
    
    def __init__(self, parent):
        self.parent = parent
        self.cards = {}
        
    def create_status_cards(self):
        """创建状态卡片区域"""
        status_frame = ctk.CTkFrame(self.parent)
        status_frame.pack(fill="x", padx=20, pady=(10, 15))
        
        # 创建四个状态卡片
        self.cards['total'] = self._create_status_card(
            status_frame, "音频文件总数", "0", 0
        )
        self.cards['needs_rename'] = self._create_status_card(
            status_frame, "需要处理文件", "0", 1
        )
        self.cards['continuous'] = self._create_status_card(
            status_frame, "编号连续性", "未检查", 2
        )
        self.cards['unique'] = self._create_status_card(
            status_frame, "编号唯一性", "未检查", 3
        )
        
        return status_frame
        
    def _create_status_card(self, parent, title: str, value: str, column: int):
        """创建单个状态卡片"""
        card_frame = ctk.CTkFrame(parent)
        card_frame.grid(row=0, column=column, padx=10, pady=10, sticky="ew")
        parent.grid_columnconfigure(column, weight=1)
        
        title_label = ctk.CTkLabel(
            card_frame, 
            text=title, 
            font=ctk.CTkFont(size=12)
        )
        title_label.pack(pady=(10, 5))
        
        value_label = ctk.CTkLabel(
            card_frame, 
            text=value, 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        value_label.pack(pady=(0, 10))
        
        return value_label
        
    def update_status(self, analysis: Dict):
        """更新状态卡片"""
        self.cards['total'].configure(text=str(analysis['total_files']))
        self.cards['needs_rename'].configure(text=str(analysis['needs_rename_count']))
        
        # 更新连续性状态
        if analysis['has_gaps']:
            continuous_text = "❌ 有间隙"
            continuous_color = "red"
        else:
            continuous_text = "✅ 连续"
            continuous_color = "green"
        
        self.cards['continuous'].configure(
            text=continuous_text, 
            text_color=continuous_color
        )
        
        # 更新唯一性状态
        if analysis['duplicate_numbers']:
            unique_text = "❌ 有重复"
            unique_color = "red"
        else:
            unique_text = "✅ 唯一"
            unique_color = "green"
        
        self.cards['unique'].configure(
            text=unique_text, 
            text_color=unique_color
        )


class FileList:
    """文件列表组件"""
    
    def __init__(self, parent):
        self.parent = parent
        self.treeview = None
        
    def create_file_list(self):
        """创建文件列表"""
        # 文件列表标题
        list_label = ctk.CTkLabel(
            self.parent, 
            text="文件列表", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        list_label.pack(pady=(15, 10))
        
        # 创建Treeview容器
        files_frame = ctk.CTkFrame(self.parent)
        files_frame.pack(fill="both", expand=True, padx=20, pady=10, ipady=10)
        
        # 创建Treeview
        columns = ("序号", "LLM建议", "原文件名", "状态", "文件大小")
        self.treeview = tk.ttk.Treeview(files_frame, columns=columns, show="headings", height=15)
        
        # 设置列标题
        for col in columns:
            self.treeview.heading(col, text=col)
        
        # 设置列宽
        self.treeview.column("序号", width=60, anchor="center")
        self.treeview.column("LLM建议", width=200, anchor="w")
        self.treeview.column("原文件名", width=200, anchor="w")
        self.treeview.column("状态", width=100, anchor="center")
        self.treeview.column("文件大小", width=80, anchor="center")
        
        # 创建滚动条
        scrollbar = tk.ttk.Scrollbar(files_frame, orient="vertical", command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.treeview.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)
        
        return files_frame
        
    def update_file_list(self, files: List[Dict]):
        """更新文件列表"""
        # 清空现有数据
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        
        # 添加新数据
        for idx, file_info in enumerate(files, 1):
            # 获取去除前缀的文件名（不含扩展名）
            original_name = file_info['original_name']
            clean_name = self._get_display_filename(original_name)
            
            # 获取LLM建议的文件名
            llm_suggestion = self._get_llm_suggestion(file_info)
            
            values = (
                str(idx),
                llm_suggestion,
                clean_name,
                format_status(file_info['status']),
                format_file_size(file_info['size'])
            )
            
            self.treeview.insert("", "end", values=values)
    
    def _get_display_filename(self, filename: str) -> str:
        """获取用于显示的文件名（去除序号前缀和扩展名）"""
        # 导入AudioFileManager来使用其方法
        import re
        from pathlib import Path
        
        # 去除序号前缀
        if re.match(r'^\d+-', filename):
            clean_name = re.sub(r'^\d+-', '', filename)
        else:
            clean_name = filename
        
        # 去除扩展名
        return Path(clean_name).stem
        
    def _get_llm_suggestion(self, file_info: Dict) -> str:
        """获取LLM建议的文件名显示"""
        genai_analysis = file_info.get('genai_analysis')
        if not genai_analysis:
            return "-"
            
        # 如果已经是标准格式，显示"已符合格式"
        if genai_analysis.get('is_standard_format', False):
            return "✅ 已符合格式"
            
        # 如果有错误，显示错误信息
        if 'error' in genai_analysis:
            return f"❌ {genai_analysis['error'][:20]}..."
            
        # 显示LLM建议的文件名
        suggested_name = genai_analysis.get('suggested_name', '')
        if suggested_name:
            confidence = genai_analysis.get('confidence', 0)
            if confidence > 0.7:
                confidence_icon = "🟢"
            elif confidence > 0.4:
                confidence_icon = "🟡"
            else:
                confidence_icon = "🔴"
            return f"{confidence_icon} {suggested_name}"
        
        return "-"


class SortOptions:
    """排序选项组件"""
    
    SORT_OPTIONS = [
        "LLM建议 (A-Z)",
        "LLM建议 (Z-A)",
        "文件名称 (A-Z)",
        "文件名称 (Z-A)",
        "文件大小 (小到大)",
        "文件大小 (大到小)"
    ]
    
    def __init__(self, parent, callback=None):
        self.parent = parent
        self.callback = callback
        self.sort_var = None
        
    def create_sort_options(self):
        """创建排序选项"""
        sort_frame = ctk.CTkFrame(self.parent)
        sort_frame.pack(fill="x", padx=20, pady=10)
        
        sort_label = ctk.CTkLabel(
            sort_frame, 
            text="排序方式:", 
            font=ctk.CTkFont(size=14)
        )
        sort_label.pack(side="left", padx=(20, 10), pady=10)
        
        self.sort_var = ctk.CTkOptionMenu(
            sort_frame,
            values=self.SORT_OPTIONS,
            command=self.callback
        )
        self.sort_var.pack(side="left", padx=(0, 20), pady=10)
        self.sort_var.set(self.SORT_OPTIONS[0])  # 默认选择第一个
        
        return sort_frame
        
    def get_selected_sort(self) -> str:
        """获取当前选择的排序方式"""
        return self.sort_var.get() if self.sort_var else self.SORT_OPTIONS[0] 