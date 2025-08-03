#!/bin/bash
# 股票AI分析助手启动脚本

echo "🎉 欢迎使用股票AI分析助手!"
echo "专为新手股民设计的智能投资工具"
echo ""

# 检查Python版本
python_version=$(python3 --version 2>&1)
if [ $? -eq 0 ]; then
    echo "✅ Python环境: $python_version"
else
    echo "❌ 未找到Python3，请先安装Python"
    exit 1
fi

echo ""
echo "请选择启动模式:"
echo "1. 🚀 快速演示 (纯Python，无需安装依赖)"
echo "2. 🌐 完整Web界面 (需要安装依赖)"
echo "3. 📦 安装依赖包"
echo "0. 退出"
echo ""

read -p "请输入选择 (0-3): " choice

case $choice in
    1)
        echo ""
        echo "🚀 启动快速演示版本..."
        python3 demo.py
        ;;
    2)
        echo ""
        echo "🌐 检查依赖..."
        
        # 检查是否安装了streamlit
        if python3 -c "import streamlit" 2>/dev/null; then
            echo "✅ 依赖已安装，启动Web界面..."
            echo "🌐 请在浏览器中访问: http://localhost:8501"
            python3 -m streamlit run src/ui/streamlit_app.py
        else
            echo "❌ 缺少依赖，请先选择选项3安装依赖"
            echo "或者选择选项1使用快速演示版本"
        fi
        ;;
    3)
        echo ""
        echo "� 安装依赖包..."
        
        if command -v pip &> /dev/null; then
            echo "正在安装基础依赖..."
            pip install -r requirements_minimal.txt
            
            if [ $? -eq 0 ]; then
                echo "✅ 依赖安装成功!"
                echo "现在可以选择选项2启动Web界面"
            else
                echo "❌ 依赖安装失败，请检查网络连接"
                echo "建议使用选项1的快速演示版本"
            fi
        else
            echo "❌ 未找到pip，请先安装pip"
        fi
        ;;
    0)
        echo ""
        echo "👋 再见!"
        exit 0
        ;;
    *)
        echo ""
        echo "❌ 无效选择"
        exit 1
        ;;
esac
echo "   Python版本: $python_version"

# 检查必要的包
echo "   检查依赖包..."
python3 -c "import pandas, numpy, streamlit" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ 基础依赖包已安装"
else
    echo "   ❌ 缺少基础依赖包"
    echo "   请运行: pip install pandas numpy streamlit plotly"
    exit 1
fi

echo ""
echo "🚀 启动选项:"
echo "1. 🎮 运行演示程序 (推荐新手)"
echo "2. 🌐 启动Web界面"
echo "3. 📊 分析指定股票"
echo "4. 🎯 智能选股"
echo "5. ⚡ 模拟交易"
echo ""

read -p "请选择启动选项 (1-5): " choice

case $choice in
    1)
        echo "🎮 启动演示程序..."
        python3 simple_app.py
        ;;
    2)
        echo "🌐 启动Web界面..."
        echo "浏览器将在几秒后自动打开 http://localhost:8501"
        python3 -m streamlit run src/ui/streamlit_app.py --server.port 8501 --server.address localhost
        ;;
    3)
        read -p "请输入股票代码 (例如: 000001.SZ): " symbol
        echo "📊 分析股票 $symbol..."
        python3 main.py analyze --symbol "$symbol" --period 1y
        ;;
    4)
        echo "🎯 开始智能选股..."
        python3 main.py screen
        ;;
    5)
        echo "⚡ 启动模拟交易..."
        echo "⚠️  注意: 这是模拟交易，不会产生真实交易"
        python3 main.py trade --mode simulate --strategy conservative
        ;;
    *)
        echo "❌ 无效选择，启动演示程序..."
        python3 simple_app.py
        ;;
esac
