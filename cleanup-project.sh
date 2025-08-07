#!/bin/bash

# 项目清理脚本 - 移除无用文件和目录
# 保留核心功能，移除冗余内容

set -e

echo "🧹 开始清理项目..."

# 记录清理前的状态
echo "📊 清理前项目大小:"
du -sh . 2>/dev/null || echo "无法计算大小"

# 1. 移除虚拟环境 (会重新创建)
echo "🗑️ 移除虚拟环境..."
rm -rf venv/ || true

# 2. 移除Python缓存文件
echo "🗑️ 清理Python缓存..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
find . -name "*.pyd" -delete 2>/dev/null || true
find . -name ".Python" -delete 2>/dev/null || true

# 3. 移除临时和备份文件
echo "🗑️ 清理临时文件..."
find . -name "*.tmp" -delete 2>/dev/null || true
find . -name "*.bak" -delete 2>/dev/null || true
find . -name "*.swp" -delete 2>/dev/null || true
find . -name "*.swo" -delete 2>/dev/null || true
find . -name "*~" -delete 2>/dev/null || true
find . -name ".DS_Store" -delete 2>/dev/null || true

# 4. 移除重复和冗余的依赖文件 (保留最终版本)
echo "🗑️ 清理重复的依赖文件..."
rm -f requirements_compatible.txt || true
rm -f requirements_lite.txt || true
rm -f requirements_minimal.txt || true
rm -f requirements_fixed.txt || true
# 保留: requirements.txt (原始), requirements_minimal_fixed.txt (最终)

# 5. 移除重复的部署脚本 (保留最新版本)
echo "🗑️ 清理重复的部署脚本..."
rm -f quick_deploy_fix.sh || true
rm -f user_deploy.sh || true
rm -f check_environment.sh || true
rm -f manage.sh || true
rm -f docker-manage.sh || true
rm -f complete_fix.sh || true
rm -f fix_talib.sh || true
# 保留: deploy.sh (增强版), quick_start.sh, server-init.sh, push-and-deploy.sh

# 6. 移除重复的Docker配置 (保留生产版本)
echo "🗑️ 清理重复的Docker配置..."
rm -f docker-compose.simple.yml || true
rm -f docker-compose.yml || true
# 保留: docker-compose.production.yml

# 7. 移除空的和过期的文档文件
echo "🗑️ 清理空的文档文件..."
find . -name "*.md" -size 0 -delete 2>/dev/null || true
rm -f CONTRIBUTING.md || true
rm -f DEPLOYMENT_GUIDE.md || true
rm -f DOCKER_SUMMARY.md || true
rm -f PROJECT_OPTIMIZATION_REPORT.md || true
rm -f QUICK_DEPLOY_CHECKLIST.md || true
rm -f run_demo.sh || true
rm -f start_app.sh || true

# 8. 移除测试和调试文件
echo "🗑️ 清理测试文件..."
rm -f comprehensive_risk_test.py || true
rm -f comprehensive_stock_info_test.py || true
rm -f debug_risk_analysis.py || true
rm -f detailed_risk_debug.py || true
rm -f functional_test.py || true
rm -f local_test.py || true
rm -f final_report.py || true
rm -f FINAL_STATUS_REPORT.py || true
rm -f COMPLETION_SUMMARY.py || true
rm -f demo.py || true
rm -f main.py || true
rm -f test_*.py || true

# 9. 移除旧的报告文件 (保留最重要的)
echo "🗑️ 清理旧报告文件..."
rm -f AUTO_TRADING_IMPLEMENTATION_REPORT.md || true
rm -f CHINESE_LEVELS_REPORT.md || true
rm -f HOT_SECTORS_FIX_REPORT.md || true
rm -f SCORING_SYSTEM_OPTIMIZATION_REPORT.md || true
rm -f UI_CHINESE_MARKET_COLORS.md || true
rm -f PROJECT_STATUS_REPORT.md || true
# 保留: README.md, CI-CD-GUIDE.md, CI-CD-SUMMARY.md

# 10. 移除不必要的数据文件
echo "🗑️ 清理数据文件..."
rm -f create_enhanced_stock_pool.py || true
rm -f enhanced_stock_search.py || true

# 11. 移除其他杂项文件
echo "🗑️ 清理杂项文件..."
find . -name "*.Zone.Identifier" -delete 2>/dev/null || true
rm -f LICENSE:Zone.Identifier || true
rm -f CHANGELOG.md* || true
rm -f CENTOS_* || true
rm -f COMPLETE_SUMMARY.md* || true
rm -f DEPLOYMENT_PACKAGE_GUIDE.md* || true
rm -f DOCKER_PACKAGE_* || true
rm -f FINAL_VERIFICATION_REPORT.md* || true
rm -f GIT_REPOSITORY_READY.md* || true
rm -f LOCAL_TEST_REPORT.md* || true

# 12. 清理archive目录中的重复内容
echo "🗑️ 清理archive目录..."
if [ -d "archive" ]; then
    # 保留archive目录但清理重复文件
    find archive/ -name "*.pyc" -delete 2>/dev/null || true
    find archive/ -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
fi

# 13. 清理logs目录
echo "🗑️ 清理日志文件..."
rm -rf logs/ || true
mkdir -p logs

# 14. 创建新的虚拟环境
echo "🔧 创建新的虚拟环境..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements_minimal_fixed.txt

echo "✅ 项目清理完成！"

# 记录清理后的状态
echo "📊 清理后项目大小:"
du -sh . 2>/dev/null || echo "无法计算大小"

echo ""
echo "📋 保留的核心文件:"
echo "📁 src/ - 核心应用代码"
echo "📁 config/ - 配置文件"
echo "📁 scripts/ - 脚本文件"
echo "📁 data/ - 数据文件"
echo "📁 .github/ - CI/CD配置"
echo "📄 requirements_minimal_fixed.txt - 最小化依赖"
echo "📄 requirements.txt - 原始依赖"
echo "📄 Dockerfile - 开发环境Docker"
echo "📄 Dockerfile.production - 生产环境Docker"
echo "📄 docker-compose.production.yml - 生产环境编排"
echo "📄 deploy.sh - 增强部署脚本"
echo "📄 quick_start.sh - 快速启动脚本"
echo "📄 server-init.sh - 服务器初始化"
echo "📄 push-and-deploy.sh - Git推送部署"
echo "📄 setup-github-secrets.sh - GitHub配置"
echo "📄 README.md - 项目说明"
echo "📄 CI-CD-GUIDE.md - CI/CD指南"
echo "📄 CI-CD-SUMMARY.md - CI/CD总结"
