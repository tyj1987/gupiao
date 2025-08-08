#!/bin/bash

# 简易Token配置向导
# 使用方式：./scripts/configure-token-interactive.sh

set -e

echo "🔐 股票分析系统 - Token配置向导"
echo "=================================="
echo ""

ENV_FILE="/www/wwwroot/gupiao/.env"

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
  echo "❌ 请使用root用户运行此脚本"
  echo "   sudo /www/wwwroot/gupiao/scripts/configure-token-interactive.sh"
  exit 1
fi

echo "📖 关于Tushare Pro:"
echo "- Tushare是专业的金融数据接口"
echo "- 免费用户：每日500次调用"
echo "- 付费用户：无限制调用，更多数据"
echo "- 注册地址: https://tushare.pro/register"
echo ""

read -p "🤔 您是否已经有Tushare Pro账号？(y/n): " has_account

if [ "$has_account" = "n" ] || [ "$has_account" = "N" ]; then
    echo ""
    echo "📝 注册步骤："
    echo "1. 访问: https://tushare.pro/register"
    echo "2. 注册账号并完成邮箱验证"
    echo "3. 登录后访问: https://tushare.pro/user/token"
    echo "4. 复制您的Token"
    echo ""
    echo "⏳ 请完成注册后重新运行此脚本"
    exit 0
fi

echo ""
read -p "🔑 请输入您的Tushare Token: " tushare_token

if [ -z "$tushare_token" ]; then
    echo "❌ Token不能为空"
    exit 1
fi

# 验证token格式（简单检查）
if [ ${#tushare_token} -lt 20 ]; then
    echo "⚠️  Token长度似乎不正确，请确认"
    read -p "继续？(y/n): " continue_anyway
    if [ "$continue_anyway" != "y" ]; then
        exit 1
    fi
fi

echo ""
echo "📝 更新配置文件..."

# 备份现有配置
if [ -f "$ENV_FILE" ]; then
    cp "$ENV_FILE" "$ENV_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✅ 已备份现有配置"
fi

# 更新token
if [ -f "$ENV_FILE" ]; then
    sed -i "s/TUSHARE_TOKEN=.*/TUSHARE_TOKEN=$tushare_token/" "$ENV_FILE"
else
    # 创建新的配置文件
    cat > "$ENV_FILE" << EOF
# 生产环境API配置
TUSHARE_TOKEN=$tushare_token
AKSHARE_ENABLED=true
YFINANCE_ENABLED=true
ENVIRONMENT=production
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
EOF
fi

# 设置安全权限
chmod 600 "$ENV_FILE"
chown root:root "$ENV_FILE"

echo "✅ Token配置完成！"
echo ""

# 重启应用
echo "🚀 重启应用..."
cd /www/wwwroot/gupiao

if [ -f "docker-compose.yml" ]; then
    echo "停止当前容器..."
    docker-compose down || true
    
    echo "启动更新后的应用..."
    docker-compose --env-file .env up -d
    
    echo ""
    echo "⏳ 等待应用启动..."
    sleep 10
    
    # 健康检查
    if curl -f http://localhost:8501 &> /dev/null; then
        echo "✅ 应用启动成功！"
        echo "🌐 访问地址: http://$(curl -s ifconfig.me):8501"
    else
        echo "⚠️  应用可能还在启动中，请稍等几分钟后访问"
        echo "📊 查看日志: docker logs gupiao-app"
    fi
else
    echo "⚠️  未找到docker-compose.yml文件"
    echo "请先完成应用部署"
fi

echo ""
echo "🎉 配置完成！"
echo ""
echo "💡 提示："
echo "- Token已安全存储在 $ENV_FILE"
echo "- 文件权限已设置为仅root可读"
echo "- 如需修改，可直接编辑该文件"
echo "- 查看应用日志: docker logs gupiao-app"
