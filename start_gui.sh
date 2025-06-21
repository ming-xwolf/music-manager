#!/bin/bash
"""
音频文件管理器桌面应用启动脚本
优化版 - 确保正确的环境管理
"""

# 设置脚本失败时立即退出
set -e

# 检查Python环境
echo "🎵 音频文件管理器 - 桌面应用启动器 (优化版)"
echo "========================================"

# 定义环境名称
ENV_NAME="music-manager"
PYTHON_VERSION="3.9"

# 检查conda环境
if command -v conda &> /dev/null; then
    echo "✅ 检测到conda环境管理器"
    
    # 初始化conda（确保在脚本中可用）
    source "$(conda info --base)/etc/profile.d/conda.sh" 2>/dev/null || true
    
    # 检查music-manager环境是否存在
    if conda env list | grep -q "^${ENV_NAME} "; then
        echo "✅ 发现${ENV_NAME}环境"
    else
        echo "🔄 创建${ENV_NAME}环境..."
        conda create -n ${ENV_NAME} python=${PYTHON_VERSION} -y
        echo "✅ ${ENV_NAME}环境创建成功"
    fi
    
    # 激活环境
    echo "🔄 激活${ENV_NAME}环境..."
    conda activate ${ENV_NAME}
    
    # 验证环境激活
    if [[ "$CONDA_DEFAULT_ENV" == "${ENV_NAME}" ]]; then
        echo "✅ 成功激活${ENV_NAME}环境"
        echo "📍 当前Python路径: $(which python)"
        echo "📍 Python版本: $(python --version)"
    else
        echo "❌ 环境激活失败，使用系统Python"
    fi
else
    echo "⚠️  未检测到conda，使用系统Python环境"
    echo "📍 Python路径: $(which python)"
    echo "📍 Python版本: $(python --version)"
fi

# 检查依赖
echo ""
echo "📦 检查依赖包..."

# 检查requirements.txt
if [[ -f "requirements.txt" ]]; then
    echo "📄 发现requirements.txt文件"
    
    # 安装或更新依赖
    echo "🔄 安装/更新依赖包..."
    pip install -r requirements.txt
    echo "✅ 依赖包安装完成"
else
    echo "⚠️  未找到requirements.txt，手动检查CustomTkinter..."
    
    # 手动检查CustomTkinter
    if python -c "import customtkinter" &> /dev/null; then
        echo "✅ CustomTkinter已安装"
        python -c "import customtkinter; print(f'   版本: {customtkinter.__version__}')"
    else
        echo "🔄 安装CustomTkinter..."
        pip install customtkinter==5.2.0
        echo "✅ CustomTkinter安装完成"
    fi
fi

# 验证项目文件
echo ""
echo "📁 检查项目文件..."
required_files=("main.py" "core/audio_manager.py" "ui/main_window.py")
missing_files=()

for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "✅ $file"
    else
        echo "❌ $file (缺失)"
        missing_files+=("$file")
    fi
done

if [[ ${#missing_files[@]} -gt 0 ]]; then
    echo "❌ 缺少必要文件，无法启动应用"
    echo "缺失文件: ${missing_files[*]}"
    exit 1
fi

# 启动应用
echo ""
echo "🚀 启动音频文件管理器桌面应用..."
echo "   - 使用环境: ${CONDA_DEFAULT_ENV:-系统Python}"
echo "   - 使用现代化GUI界面"
echo "   - 支持文件夹浏览和拖拽"
echo "   - 智能音频文件分析"
echo "   - 批量重命名功能"
echo "   - ✨ 新功能：排序时忽略序号前缀"
echo ""

# 设置Python路径以确保模块导入正确
export PYTHONPATH="${PWD}:${PYTHONPATH}"

# 启动应用，并捕获错误
if python main.py; then
    echo ""
    echo "👋 感谢使用音频文件管理器！"
else
    echo ""
    echo "❌ 应用启动失败"
    echo "请检查:"
    echo "  1. Python环境是否正确"
    echo "  2. 依赖包是否完整安装"
    echo "  3. 项目文件是否完整"
    echo "  4. 是否有GUI显示权限"
    exit 1
fi 