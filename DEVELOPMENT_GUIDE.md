# 🛠️ 音频文件管理器 - 开发指南

本文档为开发者和IDE工具（如Cursor、VS Code等）提供正确的环境管理和开发流程指南。

## 📋 目录

- [环境管理](#环境管理)
- [正确的启动流程](#正确的启动流程)
- [常见问题解决](#常见问题解决)
- [IDE配置建议](#ide配置建议)
- [调试指南](#调试指南)

## 🐍 环境管理

### 创建虚拟环境

**方法一：使用Conda（推荐）**
```bash
# 创建专用环境
conda create -n music-manager python=3.9 -y

# 激活环境
conda activate music-manager

# 安装依赖
pip install -r requirements.txt
```

**方法二：使用venv**
```bash
# 创建虚拟环境
python -m venv venv

# 激活环境（macOS/Linux）
source venv/bin/activate

# 激活环境（Windows）
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 环境验证

确保环境正确设置：
```bash
# 检查Python路径
which python

# 检查环境名称
echo $CONDA_DEFAULT_ENV  # 应显示: music-manager

# 验证依赖
python -c "import customtkinter; print(f'CustomTkinter版本: {customtkinter.__version__}')"
```

## 🚀 正确的启动流程

### 自动启动（推荐）

使用提供的启动脚本：
```bash
# 赋予执行权限
chmod +x start_gui.sh

# 启动应用
./start_gui.sh
```

### 手动启动

**步骤1：激活环境**
```bash
conda activate music-manager
```

**步骤2：验证环境**
```bash
# 检查当前环境
echo "当前环境: $CONDA_DEFAULT_ENV"
echo "Python路径: $(which python)"
echo "工作目录: $(pwd)"
```

**步骤3：启动应用**
```bash
# 设置Python路径
export PYTHONPATH="${PWD}:${PYTHONPATH}"

# 启动应用
python main.py
```

## 🔧 IDE配置建议

### Cursor编辑器

在项目根目录创建 `.cursor-settings.json`：
```json
{
  "python.defaultInterpreterPath": "~/anaconda3/envs/music-manager/bin/python",
  "python.terminal.activateEnvironment": true,
  "terminal.integrated.env.osx": {
    "PYTHONPATH": "${workspaceFolder}:${env:PYTHONPATH}"
  },
  "terminal.integrated.env.linux": {
    "PYTHONPATH": "${workspaceFolder}:${env:PYTHONPATH}"
  },
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true
}
```

### VS Code

在项目根目录创建 `.vscode/settings.json`：
```json
{
  "python.defaultInterpreterPath": "~/anaconda3/envs/music-manager/bin/python",
  "python.terminal.activateEnvironment": true,
  "terminal.integrated.env.osx": {
    "PYTHONPATH": "${workspaceFolder}:${env:PYTHONPATH}"
  },
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true
}
```

## ❗ 常见问题解决

### 问题1：导入模块失败

**症状**：`ModuleNotFoundError: No module named 'core'`

**解决方案**：
```bash
# 确保在项目根目录
cd /path/to/music-manager

# 设置Python路径
export PYTHONPATH="${PWD}:${PYTHONPATH}"

# 或在Python代码中添加
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
```

### 问题2：CustomTkinter未安装

**症状**：`ModuleNotFoundError: No module named 'customtkinter'`

**解决方案**：
```bash
# 确认在正确环境中
conda activate music-manager

# 安装依赖
pip install customtkinter==5.2.0

# 或使用requirements.txt
pip install -r requirements.txt
```

### 问题3：环境激活失败

**症状**：conda activate 命令无效

**解决方案**：
```bash
# 初始化conda
conda init

# 重新加载shell配置
source ~/.bashrc  # 或 ~/.zshrc

# 再次尝试激活
conda activate music-manager
```

### 问题4：GUI无法显示

**症状**：应用启动但无窗口显示

**解决方案**：
```bash
# 检查显示环境变量（Linux/WSL）
echo $DISPLAY

# 安装tkinter支持（Ubuntu/Debian）
sudo apt-get install python3-tk

# 在macOS上确保有GUI权限
# 在终端设置中允许"全磁盘访问"
```

## 🐛 调试指南

### 启用调试模式

在 `main.py` 中添加调试信息：
```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info("应用启动...")
```

### 环境信息收集

创建环境诊断脚本：
```python
# debug_env.py
import sys
import os
import platform

print("=== 环境诊断信息 ===")
print(f"操作系统: {platform.system()} {platform.release()}")
print(f"Python版本: {sys.version}")
print(f"Python路径: {sys.executable}")
print(f"工作目录: {os.getcwd()}")
print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
print(f"Conda环境: {os.environ.get('CONDA_DEFAULT_ENV', 'Not set')}")

try:
    import customtkinter
    print(f"CustomTkinter版本: {customtkinter.__version__}")
except ImportError as e:
    print(f"CustomTkinter导入失败: {e}")

print("=== 模块路径检查 ===")
print(f"sys.path: {sys.path}")
```

## 📝 最佳实践

### 开发流程

1. **始终在虚拟环境中工作**
   ```bash
   conda activate music-manager
   ```

2. **使用启动脚本**
   ```bash
   ./start_gui.sh
   ```

3. **定期更新依赖**
   ```bash
   pip install -r requirements.txt --upgrade
   ```

4. **提交前测试**
   ```bash
   python -m pytest tests/  # 如果有测试
   python main.py  # 手动测试
   ```

### 代码规范

- 使用类型提示
- 遵循PEP 8代码风格
- 添加文档字符串
- 适当的错误处理

### 版本管理

```bash
# 记录确切的依赖版本
pip freeze > requirements.txt

# 使用git管理代码
git add .
git commit -m "feat: 改进排序功能，忽略序号前缀"
```

## 🔍 故障排除清单

当遇到问题时，按以下顺序检查：

- [ ] 是否在正确的虚拟环境中？
- [ ] 环境是否已激活？（检查终端提示符）
- [ ] 依赖是否已安装？
- [ ] Python路径是否正确设置？
- [ ] 项目文件是否完整？
- [ ] 是否有足够的系统权限？
- [ ] GUI环境是否可用？

## 🆘 获取帮助

如果仍有问题，请提供以下信息：

1. 操作系统和版本
2. Python版本
3. 虚拟环境类型和名称
4. 完整的错误消息
5. 执行的具体步骤

这将帮助快速诊断和解决问题。 