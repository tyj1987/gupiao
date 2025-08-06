#!/bin/bash
# 股票AI分析助手 - 简化Web版本启动脚本
cd "$(dirname "$0")"

echo "🚀 启动股票AI分析助手Web版本..."
echo "📝 注意: 这是简化版本，只需要streamlit依赖"
echo ""

# 检查streamlit是否安装
if ! python -c "import streamlit" 2>/dev/null; then
    echo "❌ 未找到streamlit，正在尝试安装..."
    pip install streamlit
    if [ $? -ne 0 ]; then
        echo "❌ streamlit安装失败，请手动安装："
        echo "   pip install streamlit"
        echo ""
        echo "🔄 使用演示版本代替..."
        python demo.py
        exit 1
    fi
fi

echo "✅ 启动Web界面..."
echo "🌐 请在浏览器中访问显示的地址"
echo ""

streamlit run streamlit_simple.py
