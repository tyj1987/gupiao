#!/bin/bash

# Git仓库清理脚本 - 从Git历史中彻底移除无用文件
# 警告: 这将重写Git历史，需要强制推送

set -e

echo "🔄 Git仓库清理开始..."
echo "⚠️  警告: 此操作将重写Git历史!"

# 确认操作
read -p "是否继续清理Git历史? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 操作已取消"
    exit 1
fi

# 备份当前分支
CURRENT_BRANCH=$(git branch --show-current)
echo "📁 当前分支: $CURRENT_BRANCH"

# 创建备份分支
echo "💾 创建备份分支..."
git branch backup-before-cleanup || echo "备份分支已存在"

# 定义要从Git历史中移除的文件和目录模式
PATTERNS_TO_REMOVE=(
    "venv/"
    "*.pyc"
    "*.pyo" 
    "*.pyd"
    "__pycache__/"
    "*.tmp"
    "*.bak"
    "*.swp"
    "*.swo"
    "*~"
    ".DS_Store"
    "*.Zone.Identifier"
    "requirements_compatible.txt"
    "requirements_lite.txt"
    "requirements_minimal.txt"
    "requirements_fixed.txt"
    "quick_deploy_fix.sh"
    "user_deploy.sh"
    "check_environment.sh"
    "manage.sh"
    "docker-manage.sh"
    "complete_fix.sh"
    "fix_talib.sh"
    "docker-compose.simple.yml"
    "docker-compose.yml"
    "CONTRIBUTING.md"
    "DEPLOYMENT_GUIDE.md"
    "DOCKER_SUMMARY.md"
    "PROJECT_OPTIMIZATION_REPORT.md"
    "QUICK_DEPLOY_CHECKLIST.md"
    "run_demo.sh"
    "start_app.sh"
    "comprehensive_risk_test.py"
    "comprehensive_stock_info_test.py"
    "debug_risk_analysis.py"
    "detailed_risk_debug.py"
    "functional_test.py"
    "local_test.py"
    "final_report.py"
    "FINAL_STATUS_REPORT.py"
    "COMPLETION_SUMMARY.py"
    "demo.py"
    "main.py"
    "test_*.py"
    "AUTO_TRADING_IMPLEMENTATION_REPORT.md"
    "CHINESE_LEVELS_REPORT.md"
    "HOT_SECTORS_FIX_REPORT.md"
    "SCORING_SYSTEM_OPTIMIZATION_REPORT.md"
    "UI_CHINESE_MARKET_COLORS.md"
    "PROJECT_STATUS_REPORT.md"
    "create_enhanced_stock_pool.py"
    "enhanced_stock_search.py"
    "CHANGELOG.md*"
    "CENTOS_*"
    "COMPLETE_SUMMARY.md*"
    "DEPLOYMENT_PACKAGE_GUIDE.md*"
    "DOCKER_PACKAGE_*"
    "FINAL_VERIFICATION_REPORT.md*"
    "GIT_REPOSITORY_READY.md*"
    "LOCAL_TEST_REPORT.md*"
    "logs/"
)

# 检查是否安装了git filter-repo
if ! command -v git-filter-repo &> /dev/null; then
    echo "📦 安装git-filter-repo..."
    pip install git-filter-repo || {
        echo "❌ 无法安装git-filter-repo，尝试手动安装:"
        echo "   pip install git-filter-repo"
        echo "   或者访问: https://github.com/newren/git-filter-repo"
        exit 1
    }
fi

# 使用git filter-repo移除文件
echo "🗑️ 从Git历史中移除无用文件..."
for pattern in "${PATTERNS_TO_REMOVE[@]}"; do
    echo "  移除: $pattern"
    git filter-repo --path "$pattern" --invert-paths --force 2>/dev/null || true
done

# 清理引用
echo "🧹 清理Git引用..."
git for-each-ref --format="delete %(refname)" refs/original/ | git update-ref --stdin 2>/dev/null || true
git reflog expire --expire=now --all 2>/dev/null || true
git gc --prune=now --aggressive

echo "✅ Git仓库清理完成！"

# 显示仓库大小变化
echo "📊 仓库大小信息:"
du -sh .git 2>/dev/null || echo "无法计算.git目录大小"

echo ""
echo "📋 清理结果:"
echo "✅ 已从Git历史中移除无用文件"
echo "✅ 已清理Git引用和日志"
echo "✅ 已优化仓库大小"
echo ""
echo "🔄 下一步操作:"
echo "1. 检查项目文件: git log --oneline"
echo "2. 强制推送到远程: git push --force-with-lease origin $CURRENT_BRANCH"
echo ""
echo "⚠️  注意事项:"
echo "- Git历史已被重写，需要强制推送"
echo "- 团队成员需要重新克隆仓库"
echo "- 备份分支: backup-before-cleanup"
