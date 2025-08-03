#!/bin/bash
# 股票AI分析助手 - 智能启动脚本
cd "$(dirname "$0")"

echo "🚀 股票AI分析助手启动器"
echo "=================================="

# 检查streamlit是否安装
check_streamlit() {
    if python -c "import streamlit" 2>/dev/null; then
        echo "✅ Streamlit 已安装"
        return 0
    else
        echo "❌ Streamlit 未安装"
        return 1
    fi
}

# 检查其他依赖
check_dependencies() {
    local missing_deps=()
    
    for dep in pandas numpy plotly; do
        if ! python -c "import $dep" 2>/dev/null; then
            missing_deps+=("$dep")
        fi
    done
    
    if [ ${#missing_deps[@]} -eq 0 ]; then
        echo "✅ 基础依赖完整"
        return 0
    else
        echo "⚠️  缺少依赖: ${missing_deps[*]}"
        return 1
    fi
}

# 检查高级依赖
check_advanced_deps() {
    local missing_deps=()
    
    for dep in loguru click; do
        if ! python -c "import $dep" 2>/dev/null; then
            missing_deps+=("$dep")
        fi
    done
    
    if [ ${#missing_deps[@]} -eq 0 ]; then
        echo "✅ 高级依赖完整"
        return 0
    else
        echo "⚠️  缺少高级依赖: ${missing_deps[*]}"
        return 1
    fi
}

# 主菜单
show_menu() {
    echo ""
    echo "请选择启动方式："
    echo "1) 🌐 Web界面版本 (推荐)"
    echo "2) 📱 简化Web版本"
    echo "3) 💻 命令行版本"
    echo "4) 🔧 安装依赖"
    echo "5) 📖 查看说明"
    echo "0) 退出"
    echo ""
    read -p "请选择 (0-5): " choice
}

# 启动Web版本
start_web_full() {
    echo "🌐 启动完整Web版本..."
    if check_dependencies && check_advanced_deps; then
        echo "✅ 依赖检查通过"
        streamlit run src/ui/streamlit_app.py --server.port 8501
    else
        echo "❌ 依赖不完整，启动简化版本..."
        start_web_simple
    fi
}

# 启动简化Web版本
start_web_simple() {
    echo "📱 启动简化Web版本..."
    if check_streamlit; then
        streamlit run streamlit_simple.py --server.port 8502
    else
        echo "❌ Streamlit未安装，启动命令行版本..."
        start_cli
    fi
}

# 启动命令行版本
start_cli() {
    echo "💻 启动命令行版本..."
    python demo.py
}

# 安装依赖
install_deps() {
    echo "🔧 安装依赖包..."
    echo ""
    echo "选择安装类型："
    echo "1) 基础依赖 (streamlit, pandas, numpy, plotly)"
    echo "2) 完整依赖 (所有功能)"
    echo "0) 返回主菜单"
    echo ""
    read -p "请选择: " install_choice
    
    case $install_choice in
        1)
            echo "安装基础依赖..."
            pip install streamlit pandas numpy plotly
            ;;
        2)
            echo "安装完整依赖..."
            pip install -r requirements_minimal.txt
            ;;
        0)
            return
            ;;
        *)
            echo "无效选择"
            ;;
    esac
}

# 显示说明
show_help() {
    echo ""
    echo "📖 使用说明"
    echo "=================================="
    echo ""
    echo "🌐 Web界面版本:"
    echo "   - 功能最完整，界面最友好"
    echo "   - 需要安装所有依赖包"
    echo "   - 适合日常使用"
    echo ""
    echo "📱 简化Web版本:"
    echo "   - 只需要streamlit等基础依赖"
    echo "   - 使用模拟数据演示功能"
    echo "   - 适合快速体验"
    echo ""
    echo "💻 命令行版本:"
    echo "   - 无需任何外部依赖"
    echo "   - 使用纯Python实现"
    echo "   - 适合学习和了解功能"
    echo ""
    echo "💡 建议:"
    echo "   1. 新手先用命令行版本了解功能"
    echo "   2. 然后尝试简化Web版本"
    echo "   3. 最后安装完整依赖使用完整版"
    echo ""
    read -p "按回车键返回主菜单..."
}

# 主循环
while true; do
    clear
    echo "🚀 股票AI分析助手启动器"
    echo "=================================="
    
    # 系统检查
    echo "📋 系统检查:"
    check_streamlit
    check_dependencies
    check_advanced_deps
    
    show_menu
    
    case $choice in
        1)
            start_web_full
            break
            ;;
        2)
            start_web_simple
            break
            ;;
        3)
            start_cli
            break
            ;;
        4)
            install_deps
            ;;
        5)
            show_help
            ;;
        0)
            echo "👋 再见！"
            exit 0
            ;;
        *)
            echo "❌ 无效选择，请重试"
            sleep 2
            ;;
    esac
done
