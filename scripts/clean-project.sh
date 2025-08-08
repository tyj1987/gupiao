#!/bin/bash
# =============================================
# 项目清理脚本 - 保持项目干净整洁
# =============================================

set -e

echo "🧹 开始清理项目..."

# 当前目录
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# 清理 Python 缓存
echo "📦 清理 Python 缓存..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
find . -type f -name "*.pyd" -delete 2>/dev/null || true

# 清理临时文件
echo "🗑️ 清理临时文件..."
find . -type f -name "*.tmp" -delete 2>/dev/null || true
find . -type f -name "*.temp" -delete 2>/dev/null || true
find . -type f -name "*.bak" -delete 2>/dev/null || true
find . -type f -name "*.backup" -delete 2>/dev/null || true
find . -type f -name "*.orig" -delete 2>/dev/null || true
find . -type f -name "*~" -delete 2>/dev/null || true

# 清理日志文件
echo "📋 清理日志文件..."
find . -type f -name "*.log" -delete 2>/dev/null || true
find . -type f -name "*.out" -delete 2>/dev/null || true

# 清理系统文件
echo "🖥️ 清理系统文件..."
find . -type f -name ".DS_Store" -delete 2>/dev/null || true
find . -type f -name "Thumbs.db" -delete 2>/dev/null || true
find . -type f -name "desktop.ini" -delete 2>/dev/null || true
find . -type f -name "*.Zone.Identifier" -delete 2>/dev/null || true

# 清理数据目录
echo "📊 清理数据目录..."
rm -rf data/* 2>/dev/null || true
rm -rf cache/* 2>/dev/null || true
rm -rf logs/* 2>/dev/null || true
rm -rf exports/* 2>/dev/null || true
rm -rf models/* 2>/dev/null || true

# 保持目录结构
touch data/.gitkeep cache/.gitkeep logs/.gitkeep exports/.gitkeep models/.gitkeep

# 清理测试覆盖率文件
echo "🧪 清理测试文件..."
rm -rf .coverage htmlcov/ .pytest_cache/ .tox/ .nox/ 2>/dev/null || true

# 清理 IDE 文件
echo "💻 清理 IDE 文件..."
rm -rf .vscode/ .idea/ *.swp *.swo 2>/dev/null || true

# 显示清理后的大小
echo "📏 清理完成！项目大小："
du -sh . 2>/dev/null || echo "无法计算大小"

echo "✅ 项目清理完成！"
