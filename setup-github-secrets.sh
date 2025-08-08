#!/bin/bash
# GitHub Secrets 设置指南和脚本
# 用于配置CI/CD所需的敏感信息

echo "🔐 GitHub Secrets 配置指南"
echo "================================"
echo ""
echo "为了使CI/CD正常工作，需要在GitHub仓库中设置以下Secrets:"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}[步骤]${NC} $1"
}

print_secret() {
    echo -e "${GREEN}[SECRET]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[注意]${NC} $1"
}

print_step "1. 访问GitHub仓库设置页面"
echo "   https://github.com/tyj1987/gupiao/settings/secrets/actions"
echo ""

print_step "2. 添加以下Repository Secrets:"
echo ""

print_secret "DOCKER_USERNAME"
echo "   值: tuoyongjun1987"
echo "   说明: Docker Hub用户名"
echo ""

print_secret "DOCKER_PASSWORD"
echo "   值: [您的Docker Hub密码或Access Token]"
echo "   说明: Docker Hub密码或访问令牌"
echo "   获取方式: https://hub.docker.com/settings/security"
echo ""

print_secret "PRODUCTION_USER"
echo "   值: root"
echo "   说明: 生产服务器SSH用户名"
echo ""

print_secret "PRODUCTION_SSH_KEY"
echo "   值: [SSH私钥内容]"
echo "   说明: 用于连接生产服务器的SSH私钥"
echo ""

print_step "3. 生成SSH密钥对 (如果还没有):"
echo ""
echo "在本地执行以下命令:"
echo "ssh-keygen -t rsa -b 4096 -C 'github-actions@gupiao-deploy'"
echo "cat ~/.ssh/id_rsa.pub  # 复制公钥到服务器 ~/.ssh/authorized_keys"
echo "cat ~/.ssh/id_rsa      # 复制私钥内容到PRODUCTION_SSH_KEY secret"
echo ""

print_step "4. 验证服务器SSH配置:"
echo ""
echo "在生产服务器上执行:"
echo "# 确保SSH目录权限正确"
echo "mkdir -p ~/.ssh"
echo "chmod 700 ~/.ssh"
echo "chmod 600 ~/.ssh/authorized_keys"
echo ""
echo "# 测试SSH连接"
echo "ssh root@47.94.225.76 'echo \"SSH连接成功\"'"
echo ""

print_step "5. 设置GitHub环境保护 (可选):"
echo ""
echo "1. 访问: https://github.com/tyj1987/gupiao/settings/environments"
echo "2. 创建 'production' 环境"
echo "3. 添加保护规则 (如需要手动审批部署)"
echo ""

print_step "6. 测试CI/CD流水线:"
echo ""
echo "配置完成后，推送代码到main分支将自动触发部署:"
echo "git add ."
echo "git commit -m 'setup: 配置CI/CD自动部署'"
echo "git push origin main"
echo ""

print_warning "重要提醒:"
echo "1. 确保生产服务器防火墙开放8501端口"
echo "2. 确保Docker Hub账号有推送权限"
echo "3. 首次部署可能需要较长时间下载依赖"
echo "4. 保护好SSH私钥，不要泄露"
echo ""

print_step "7. 手动触发部署 (可选):"
echo ""
echo "访问: https://github.com/tyj1987/gupiao/actions"
echo "选择 '🚀 生产环境CI/CD部署' workflow"
echo "点击 'Run workflow' 手动触发"
echo ""

echo "🎯 配置完成后，每次推送到main分支都会自动:"
echo "✅ 代码质量检查"
echo "✅ 构建优化Docker镜像"
echo "✅ 自动部署到生产服务器"
echo "✅ 健康检查验证"
echo "✅ 生成部署报告"
echo ""

echo "🌐 部署成功后访问地址:"
echo "http://47.94.225.76:8501"

# 检查gh CLI是否已安装 (可选使用)
if command -v gh &> /dev/null; then
    echo ""
    echo "� 检测到GitHub CLI，可以使用命令行设置Secrets:"
    echo "gh auth login  # 首先登录"
    echo "gh secret set DOCKER_USERNAME --body 'tuoyongjun1987'"
    echo "gh secret set DOCKER_PASSWORD --body '[您的密码]'"
    echo "gh secret set PRODUCTION_USER --body 'root'"
    echo "gh secret set PRODUCTION_SSH_KEY --body '[SSH私钥内容]'"
else
    echo ""
    echo "� 也可以安装GitHub CLI来快速设置: https://cli.github.com/"
fi

echo ""
echo "📖 详细配置指南已保存到当前目录"
echo "🚀 配置完成后即可使用CI/CD自动部署！"
