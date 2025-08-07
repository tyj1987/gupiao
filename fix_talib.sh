#!/bin/bash
# talib依赖问题修复脚本
# 针对Python 3.9版本的兼容性修复

set -e

echo "🔧 修复talib依赖问题..."
echo "================================"

PROJECT_DIR="/home/tyj/gupiao"
cd $PROJECT_DIR

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行deploy.sh"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

echo "📋 当前Python环境信息："
echo "Python版本: $(python --version)"
echo "pip版本: $(pip --version)"
echo ""

echo "🧹 清理problematic packages..."
packages_to_remove=("talib" "TA-Lib")
for pkg in "${packages_to_remove[@]}"; do
    pip uninstall "$pkg" -y 2>/dev/null || echo "$pkg 未安装"
done

echo ""
echo "📦 安装兼容的核心依赖..."

# 升级pip
pip install --upgrade pip

# 核心依赖列表 (Python 3.9兼容版本)
core_packages=(
    "streamlit==1.28.0"
    "pandas==1.5.3" 
    "numpy==1.24.3"
    "plotly==5.17.0"
    "requests==2.28.2"
    "pytz==2023.3"
    "tqdm==4.65.0"
    "yfinance==0.2.18"
    "openpyxl==3.1.2"
    "python-dateutil==2.8.2"
    "urllib3==1.26.16"
)

# 逐个安装包，避免单个失败影响整体
for package in "${core_packages[@]}"; do
    echo "安装: $package"
    if pip install "$package"; then
        echo "✅ $package 安装成功"
    else
        echo "⚠️ $package 安装失败，跳过"
    fi
done

echo ""
echo "🔍 验证核心包安装..."
python -c "
try:
    import streamlit
    import pandas
    import numpy
    import plotly
    import requests
    print('✅ 核心包验证成功')
    print(f'Streamlit版本: {streamlit.__version__}')
    print(f'Pandas版本: {pandas.__version__}')
    print(f'Numpy版本: {numpy.__version__}')
except ImportError as e:
    print(f'❌ 包导入失败: {e}')
    exit(1)
"

echo ""
echo "📝 创建兼容的requirements文件..."
cat > requirements_fixed.txt << 'EOF'
# Python 3.9兼容的股票分析系统依赖
streamlit==1.28.0
pandas==1.5.3
numpy==1.24.3
plotly==5.17.0
requests==2.28.2
pytz==2023.3
tqdm==4.65.0
yfinance==0.2.18
openpyxl==3.1.2
python-dateutil==2.8.2
urllib3==1.26.16
EOF

echo "✅ requirements_fixed.txt 创建完成"

echo ""
echo "🚀 测试Streamlit启动..."
if python -c "import streamlit; print('Streamlit可以正常导入')"; then
    echo "✅ Streamlit环境准备就绪"
    echo ""
    echo "📋 下一步操作："
    echo "1. 可以运行: ./start_direct.sh"
    echo "2. 或者运行: streamlit run src/ui/streamlit_app.py --server.port=8501"
    echo "3. 访问: http://localhost:8501"
else
    echo "❌ Streamlit环境仍有问题"
fi

deactivate
echo ""
echo "🎉 依赖修复完成！"
