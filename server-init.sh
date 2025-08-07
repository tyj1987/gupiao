#!/bin/bash

# 服务器初始化部署脚本
# 在生产服务器和测试服务器上运行

set -e

echo "🚀 初始化服务器环境..."

# 更新系统
echo "📦 更新系统包..."
apt update && apt upgrade -y

# 安装Docker
echo "🐳 安装Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl enable docker
    systemctl start docker
    rm get-docker.sh
fi

# 安装Docker Compose
echo "🔧 安装Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# 安装curl (健康检查需要)
echo "🌐 安装curl..."
apt install -y curl

# 创建应用目录
echo "📁 创建应用目录..."
mkdir -p /var/log/gupiao
mkdir -p /opt/gupiao/data

# 设置防火墙
echo "🔥 配置防火墙..."
ufw --force enable
ufw allow ssh
ufw allow 8501/tcp
ufw allow 80/tcp
ufw allow 443/tcp

# 登录Docker Hub
echo "🔐 登录Docker Hub..."
echo "请手动执行以下命令登录Docker Hub:"
echo "docker login -u tuoyongjun1987"
echo "密码: [使用您的Docker Hub访问令牌]"

# 拉取应用镜像
echo "📥 拉取应用镜像..."
docker pull tuoyongjun1987/gupiao-stock-analysis:latest || echo "镜像将在首次CI/CD部署时拉取"

echo "✅ 服务器初始化完成！"
echo ""
echo "📋 服务器信息:"
echo "- Docker版本: $(docker --version)"
echo "- Docker Compose版本: $(docker-compose --version)"
echo "- 系统版本: $(lsb_release -d)"
echo ""
echo "🔗 后续步骤:"
echo "1. 手动登录Docker Hub"
echo "2. 推送代码到GitHub触发自动部署"
echo "3. 访问应用: http://$(curl -s ifconfig.me):8501"
