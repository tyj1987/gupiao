#!/bin/bash

# GitHub Secrets配置脚本
# 运行此脚本配置GitHub仓库的Secrets

set -e

REPO_OWNER="tyj1987"
REPO_NAME="gupiao"

echo "🔐 配置GitHub Secrets..."

# 检查gh CLI是否已安装
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI未安装，请先安装: https://cli.github.com/"
    exit 1
fi

# 检查是否已登录
if ! gh auth status &> /dev/null; then
    echo "📝 请先登录GitHub CLI:"
    gh auth login
fi

echo "🔧 设置Repository Secrets..."

# Docker Hub Token
echo "设置DOCKER_HUB_TOKEN..."
echo "请输入您的Docker Hub访问令牌:"
read -s DOCKER_TOKEN
echo "$DOCKER_TOKEN" | gh secret set DOCKER_HUB_TOKEN --repo="$REPO_OWNER/$REPO_NAME"

# 测试服务器密码
echo "设置TEST_SERVER_PASSWORD..."
echo "[您的测试服务器密码]" | gh secret set TEST_SERVER_PASSWORD --repo="$REPO_OWNER/$REPO_NAME"

# 生产服务器密码
echo "设置PROD_SERVER_PASSWORD..."
echo "[您的生产服务器密码]" | gh secret set PROD_SERVER_PASSWORD --repo="$REPO_OWNER/$REPO_NAME"

echo "✅ 所有Secrets配置完成！"

# 列出已配置的secrets
echo "📋 当前配置的Secrets:"
gh secret list --repo="$REPO_OWNER/$REPO_NAME"

echo ""
echo "🚀 CI/CD工作流配置完成！"
echo "📁 推送代码到main分支将自动触发部署流程"
echo "🔗 GitHub Actions: https://github.com/$REPO_OWNER/$REPO_NAME/actions"
