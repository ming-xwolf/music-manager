#!/usr/bin/env python3
"""
格式化工具函数
提供各种数据格式化功能
"""

from datetime import datetime


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小显示"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    if i == 0:
        return f"{int(size)} {size_names[i]}"
    else:
        return f"{size:.1f} {size_names[i]}"


def format_time(timestamp: float) -> str:
    """格式化时间戳显示"""
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return "未知"


def format_status(status: str) -> str:
    """格式化文件状态显示"""
    status_map = {
        'ok': '✓ 正常',
        'no_prefix': '❌ 缺少前缀',
        'duplicate_number': '⚠️ 编号重复'
    }
    return status_map.get(status, status) 