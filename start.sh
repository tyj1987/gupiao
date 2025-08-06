#!/bin/bash
# -*- coding: utf-8 -*-
# 股票分析系统快速启动脚本

cd "$(dirname "$0")"

export PYTHONPATH="$PYTHONPATH:$(pwd)"

echo "🚀 启动股票分析系统..."
echo "📊 访问地址: http://localhost:8501"
echo "⏹️  停止服务: Ctrl+C"
echo ""

streamlit run src/ui/streamlit_app.py --server.port=8501 --server.address=0.0.0.0
