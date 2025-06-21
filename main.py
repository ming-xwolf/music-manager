#!/usr/bin/env python3
"""
音频文件管理器 - 主入口文件
"""

import customtkinter as ctk
from ui.main_window import MusicManagerMainWindow


def setup_customtkinter():
    """设置CustomTkinter外观"""
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")


def main():
    """主函数"""
    setup_customtkinter()
    
    app = MusicManagerMainWindow()
    app.mainloop()


if __name__ == "__main__":
    main() 