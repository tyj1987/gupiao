#!/bin/bash

# 生产环境API Token安全配置脚本
# 使用方式：./scripts/setup-production-tokens.sh

set -e

echo "🔐 配置生产环境API Tokens..."

# 创建安全的环境变量文件
ENV_FILE="/www/wwwroot/gupiao/.env"
ENV_DIR="/www/wwwroot/gupiao"

# 确保目录存在
mkdir -p "$ENV_DIR"

# 创建.env文件（如果不存在）
if [ ! -f "$ENV_FILE" ]; then
    echo "📝 创建环境变量配置文件..."
    cat > "$ENV_FILE" << 'EOF'
# 生产环境API配置
# 请填入您的真实API token

# Tushare Pro Token (必填，如果需要高质量金融数据)
# 注册地址: https://tushare.pro/register
TUSHARE_TOKEN=

# 数据源启用开关
AKSHARE_ENABLED=true
YFINANCE_ENABLED=true

# 数据库配置
ENVIRONMENT=production

# Streamlit配置
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
EOF
fi

# 设置文件权限
chmod 600 "$ENV_FILE"
chown root:root "$ENV_FILE"

echo "✅ 环境变量文件已创建: $ENV_FILE"
echo ""
echo "📋 配置步骤："
echo "1. 注册Tushare Pro账号: https://tushare.pro/register"
echo "2. 获取您的API Token"
echo "3. 编辑文件: vi $ENV_FILE"
echo "4. 填入您的TUSHARE_TOKEN"
echo "5. 重启应用: docker-compose down && docker-compose up -d"
echo ""
echo "🔒 安全提示："
echo "- .env文件已设置为只有root用户可读写"
echo "- 切勿将真实token提交到git仓库"
echo "- 定期更换API token"
echo ""

# 检查当前token状态
if [ -f "$ENV_FILE" ]; then
    echo "📊 当前配置状态："
    if grep -q "TUSHARE_TOKEN=$" "$ENV_FILE" || grep -q "TUSHARE_TOKEN=your" "$ENV_FILE"; then
        echo "❌ TUSHARE_TOKEN 未配置"
    else
        echo "✅ TUSHARE_TOKEN 已配置"
    fi
    
    if grep -q "AKSHARE_ENABLED=true" "$ENV_FILE"; then
        echo "✅ AkShare 已启用"
    else
        echo "⚠️  AkShare 已禁用"
    fi
    
    if grep -q "YFINANCE_ENABLED=true" "$ENV_FILE"; then
        echo "✅ YFinance 已启用"
    else
        echo "⚠️  YFinance 已禁用"
    fi
fi

echo ""
echo "🚀 如果您已经配置了token，可以重启应用："
echo "   cd /www/wwwroot/gupiao"
echo "   docker-compose --env-file .env up -d"
