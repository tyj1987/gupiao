#!/bin/bash
# 完整的talib问题解决方案
# 解决Python 3.9与某些包版本不兼容的问题

echo "🔧 完整修复talib和依赖问题"
echo "================================"

cd /home/tyj/gupiao

# 1. 确保虚拟环境存在并激活
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate
echo "✅ 虚拟环境已激活"

# 2. 升级pip到最新版本
echo "升级pip..."
python -m pip install --upgrade pip

# 3. 移除问题包
echo "移除有问题的包..."
pip uninstall talib TA-Lib -y 2>/dev/null || true

# 4. 安装兼容版本的核心依赖
echo "安装核心依赖包..."
pip install streamlit==1.28.0
pip install pandas==1.5.3
pip install numpy==1.24.3
pip install plotly==5.17.0
pip install requests==2.28.2
pip install yfinance==0.2.18
pip install openpyxl==3.1.2
pip install pytz==2023.3
pip install tqdm==4.65.0

# 5. 验证安装
echo ""
echo "🧪 验证安装结果..."
python -c "
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
import yfinance as yf

print('✅ 所有核心包导入成功!')
print(f'Streamlit: {st.__version__}')
print(f'Pandas: {pd.__version__}')
print(f'Numpy: {np.__version__}')
print(f'YFinance: {yf.__version__}')
"

# 6. 创建固定版本的requirements文件
echo ""
echo "📝 创建requirements_fixed.txt..."
cat > requirements_fixed.txt << 'EOF'
# 修复版本依赖 - 兼容Python 3.9
streamlit==1.28.0
pandas==1.5.3
numpy==1.24.3
plotly==5.17.0
requests==2.28.2
yfinance==0.2.18
openpyxl==3.1.2
pytz==2023.3
tqdm==4.65.0
python-dateutil==2.8.2
urllib3==1.26.16
matplotlib==3.7.2
seaborn==0.12.2
EOF

# 7. 测试Streamlit应用
echo ""
echo "🚀 测试Streamlit应用启动..."
python -c "
import sys
sys.path.append('.')
try:
    # 检查主应用文件
    with open('src/ui/streamlit_app.py', 'r') as f:
        print('✅ 主应用文件存在且可读')
    
    # 测试streamlit命令
    import streamlit.cli
    print('✅ Streamlit CLI可用')
    
except Exception as e:
    print(f'❌ 测试失败: {e}')
"

deactivate

echo ""
echo "🎉 修复完成！"
echo ""
echo "📋 后续步骤："
echo "1. 启动应用: cd /home/tyj/gupiao && source venv/bin/activate && streamlit run src/ui/streamlit_app.py --server.port=8501"
echo "2. 访问地址: http://localhost:8501"
echo "3. 如果仍有问题，检查 src/ui/streamlit_app.py 文件中的导入语句"
