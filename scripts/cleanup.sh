#!/bin/bash
# -*- coding: utf-8 -*-
# 股票分析系统项目清理脚本
# 清理临时文件、测试文件和Zone.Identifier文件

set -e

PROJECT_ROOT="/home/tyj/gupiao"
cd "$PROJECT_ROOT"

echo "🧹 开始清理项目临时文件..."

# 清理Zone.Identifier文件（Windows文件系统标识符）
echo "清理Zone.Identifier文件..."
find . -name "*:Zone.Identifier" -type f -delete
echo "✓ 已清理Zone.Identifier文件"

# 清理Python缓存文件
echo "清理Python缓存文件..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -type f -delete 2>/dev/null || true
find . -name "*.pyo" -type f -delete 2>/dev/null || true
find . -name "*.pyd" -type f -delete 2>/dev/null || true
echo "✓ 已清理Python缓存文件"

# 清理临时测试文件
echo "清理临时测试文件..."
temp_files=(
    "debug_risk_analysis.py"
    "verification_report.py"
    "test_dynamic_pool.py"
    "functional_test.py"
    "comprehensive_stock_info_test.py"
    "comprehensive_risk_test.py"
    "simple_risk_debug.py"
    "detailed_risk_debug.py"
    "test_ui_improvements.py"
    "test_expanded_stock_pool.py"
    "test_bank_search.py"
    "test_ai_fixes.py"
    "test_improvements.py"
    "test_system.py"
    "streamlit_simple.py"
    "simple_app.py"
    "start_app.py"
    "demo.py"
    "final_report.py"
    "COMPLETION_SUMMARY.py"
)

for file in "${temp_files[@]}"; do
    if [[ -f "$file" ]]; then
        rm -f "$file"
        echo "  - 删除: $file"
    fi
done
echo "✓ 已清理临时测试文件"

# 清理重复的文档文件
echo "清理重复文档文件..."
duplicate_docs=(
    "CHANGELOG.md"
    "LOCAL_TEST_REPORT.md"
    "DOCKER_PACKAGE_v2.1.0_GUIDE.md"
    "DOCKER_DEPLOYMENT_GUIDE.md"
    "CENTOS_DEPLOYMENT_GUIDE.md"
    "COMPLETE_SUMMARY.md"
    "FINAL_VERIFICATION_REPORT.md"
    "GIT_REPOSITORY_READY.md"
    "PROJECT_SUMMARY.md"
    "PROJECT_ENHANCEMENT_REPORT.md"
    "DEPLOYMENT_PACKAGE_GUIDE.md"
    "系统全面升级总结.md"
    "界面优化总结.md"
    "智能选股优化总结.md"
    "QUICK_START.md"
)

for doc in "${duplicate_docs[@]}"; do
    if [[ -f "$doc" ]]; then
        # 移动到archive目录而不是删除
        mkdir -p archive/docs
        mv "$doc" "archive/docs/" 2>/dev/null || true
        echo "  - 归档: $doc -> archive/docs/"
    fi
done
echo "✓ 已归档重复文档文件"

# 清理未使用的脚本文件
echo "清理未使用的脚本文件..."
unused_scripts=(
    "create_deployment_package.sh"
    "create_docker_package.sh"
    "docker-quick-deploy.sh"
    "run_web.sh"
    "enhanced_stock_search.py"
    "create_enhanced_stock_pool.py"
    "stock_search_tool.py"
)

for script in "${unused_scripts[@]}"; do
    if [[ -f "$script" ]]; then
        mkdir -p archive/scripts
        mv "$script" "archive/scripts/" 2>/dev/null || true
        echo "  - 归档: $script -> archive/scripts/"
    fi
done
echo "✓ 已归档未使用的脚本文件"

# 清理日志文件
echo "清理日志文件..."
find . -name "*.log" -type f -delete 2>/dev/null || true
find . -name "logs" -type d -exec rm -rf {} + 2>/dev/null || true
echo "✓ 已清理日志文件"

# 清理临时目录
echo "清理临时目录..."
temp_dirs=(
    "tmp"
    "temp"
    ".pytest_cache"
    ".coverage"
    "htmlcov"
    "build"
    "dist"
    "*.egg-info"
)

for dir in "${temp_dirs[@]}"; do
    if [[ -d "$dir" ]]; then
        rm -rf "$dir"
        echo "  - 删除目录: $dir"
    fi
done
echo "✓ 已清理临时目录"

# 更新.gitignore
echo "更新.gitignore文件..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# 环境文件
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# 日志文件
*.log
logs/

# 数据库文件
*.db
*.sqlite

# 缓存文件
cache/
*.cache

# 配置文件（包含敏感信息）
config/api_keys.py

# 临时文件
tmp/
temp/
*.tmp

# 系统文件
.DS_Store
Thumbs.db
*:Zone.Identifier

# 测试文件
.coverage
htmlcov/
.pytest_cache/

# Streamlit
.streamlit/secrets.toml
EOF
echo "✓ 已更新.gitignore文件"

# 统计清理结果
echo ""
echo "📊 清理统计:"
echo "  项目目录: $(pwd)"
echo "  剩余文件数: $(find . -type f | wc -l)"
echo "  剩余目录数: $(find . -type d | wc -l)"
echo ""
echo "🎉 项目清理完成！"
echo ""
echo "📁 保留的核心目录结构:"
echo "├── src/               # 源代码目录"
echo "├── config/            # 配置文件"
echo "├── scripts/           # 部署脚本"
echo "├── archive/           # 归档文件"
echo "├── .streamlit/        # Streamlit配置"
echo "├── .github/           # GitHub工作流"
echo "└── docs/              # 文档目录"
echo ""
echo "🔥 建议下一步操作:"
echo "1. 检查归档文件是否还需要"
echo "2. 运行部署测试确保功能正常"
echo "3. 提交清理后的代码到版本控制"
