# 🎵 音频文件管理器 - 项目结构

```
music-manager/
├── main.py                    # 应用入口文件
├── core/                      # 核心业务逻辑
│   ├── __init__.py
│   └── audio_manager.py       # 音频文件管理器核心类
├── ui/                        # 用户界面
│   ├── __init__.py
│   ├── main_window.py         # 主窗口类
│   └── components.py          # UI组件类
├── utils/                     # 工具函数
│   ├── __init__.py
│   └── formatters.py          # 格式化工具函数
├── requirements.txt           # Python依赖包列表
├── start_gui.sh              # 启动脚本
├── README.md                 # 项目说明文档
├── PROJECT_STRUCTURE.md      # 本文件（项目结构说明）
└── USAGE_EXAMPLE.md          # 使用示例
```

## 📁 文件说明

### 核心文件

**`main.py`** - 应用入口
- 🚀 应用启动点
- ⚙️ CustomTkinter配置
- 🔧 主窗口初始化

**`core/audio_manager.py`** - 核心业务逻辑
- 🔍 音频文件识别和筛选（12种格式）
- 📊 文件状态分析（前缀检查、编号验证）
- 🔄 批量文件重命名功能
- 📝 文件排序和元数据获取

**`ui/main_window.py`** - 主窗口类
- 🖼️ 主窗口界面管理
- 🔗 用户事件处理
- 🧵 后台线程管理
- 💬 错误处理和用户反馈

**`ui/components.py`** - UI组件库
- 📊 状态卡片组件（StatusCards）
- 📋 文件列表组件（FileList）
- 🔽 排序选项组件（SortOptions）

**`utils/formatters.py`** - 格式化工具
- 📏 文件大小格式化
- ⏰ 时间戳格式化
- 🏷️ 状态信息格式化

### 配置文件

**`requirements.txt`** - Python依赖
```
customtkinter==5.2.0
```

**`start_gui.sh`** - 启动脚本
- 🐍 自动检测Python环境
- 📦 依赖检查和安装
- 🚀 一键启动桌面应用

## 🚀 环境管理

### Conda环境（推荐）
```bash
# 创建环境
conda create -n music-manager python=3.9 -y

# 激活环境
conda activate music-manager

# 安装依赖
pip install -r requirements.txt

# 启动应用
python main.py
```

### 系统Python环境
```bash
# 安装依赖
pip3 install -r requirements.txt

# 启动应用
python3 main.py
```

### 一键启动（推荐）
```bash
chmod +x start_gui.sh
./start_gui.sh
```

## 🔧 技术架构

### 桌面应用技术栈
- **CustomTkinter 5.2.0** - 现代化GUI框架
- **Python 3.9+** - 运行环境
- **Tkinter** - 底层GUI支持
- **Threading** - 后台任务处理

### 设计模式
- **MVC架构** - 模型-视图-控制器分离
- **组件化设计** - 可复用的UI组件
- **单一职责原则** - 每个类专注一个功能

### 支持的音频格式
- 🎵 **有损压缩**：MP3, AAC, OGG, WMA, RA, MP2
- 🎼 **无损压缩**：FLAC, ALAC (M4A)
- 📻 **未压缩**：WAV, AIFF, AU
- 🆕 **现代格式**：OPUS

## 🔍 核心算法

### 文件筛选算法
1. 遍历文件夹中的所有文件
2. 根据文件扩展名识别音频文件（12种格式）
3. 支持8种排序方式（名称、大小、时间）

### 前缀分析算法
1. 使用正则表达式 `^\d+-` 检测数字前缀
2. 提取现有编号并检查重复和间隙
3. 生成连续的编号序列，保持已正确编号的文件

### 重命名策略
1. 两阶段重命名避免文件名冲突
2. 只重命名真正需要修改的文件
3. 完整的错误处理和用户反馈

### GUI事件处理
1. 后台线程处理耗时操作
2. 主线程负责UI更新
3. 实时状态反馈和进度提示

## 🎨 UI组件设计

### 模块化组件
- **StatusCards**: 状态信息展示
- **FileList**: 文件列表显示
- **SortOptions**: 排序选择器

### 响应式布局
- 自适应窗口大小
- 清晰的视觉层次
- 用户友好的交互设计 