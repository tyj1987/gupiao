#!/bin/bash
# CI/CD部署状态监控脚本

echo "🔍 监控CI/CD部署状态"
echo "===================="

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

PRODUCTION_SERVER="47.94.225.76"
APP_PORT="8501"

print_status "检查CI/CD部署状态..."
echo ""

echo "📋 链接信息:"
echo "- GitHub Actions: https://github.com/tyj1987/gupiao/actions"
echo "- 生产环境: http://$PRODUCTION_SERVER:$APP_PORT"
echo "- GitHub仓库: https://github.com/tyj1987/gupiao"
echo ""

print_status "检查生产环境状态..."

# 检查服务器响应
max_attempts=5
attempt=1

while [ $attempt -le $max_attempts ]; do
    if curl -f http://$PRODUCTION_SERVER:$APP_PORT --connect-timeout 10 &> /dev/null; then
        print_success "✅ 生产环境正常运行"
        echo "   访问地址: http://$PRODUCTION_SERVER:$APP_PORT"
        break
    else
        print_warning "⏳ 生产环境暂不可达 ($attempt/$max_attempts)"
        if [ $attempt -lt $max_attempts ]; then
            echo "   等待5秒后重试..."
            sleep 5
        fi
        ((attempt++))
    fi
done

if [ $attempt -gt $max_attempts ]; then
    print_warning "⚠️ 生产环境暂时无法访问"
    echo ""
    echo "可能的原因:"
    echo "1. CI/CD部署正在进行中"
    echo "2. 需要配置GitHub Secrets"
    echo "3. 服务器或网络问题"
    echo ""
    echo "解决方案:"
    echo "1. 检查GitHub Actions状态"
    echo "2. 配置必需的Secrets (运行 ./setup-github-secrets.sh 查看指南)"
    echo "3. 手动触发部署 (在GitHub Actions页面)"
fi

echo ""
print_status "CI/CD配置检查清单:"
echo ""

echo "必需的GitHub Secrets:"
echo "□ DOCKER_USERNAME (Docker Hub用户名)"
echo "□ DOCKER_PASSWORD (Docker Hub密码/Token)"
echo "□ PRODUCTION_USER (生产服务器用户名)"
echo "□ PRODUCTION_SSH_KEY (SSH私钥)"
echo ""

echo "部署流程状态:"
echo "✅ GitHub仓库推送完成"
echo "✅ CI/CD工作流已配置"
echo "□ GitHub Secrets已配置"
echo "□ 自动部署已触发"
echo "□ 生产环境运行正常"
echo ""

print_status "下一步操作:"
echo "1. 访问 https://github.com/tyj1987/gupiao/settings/secrets/actions"
echo "2. 配置所需的GitHub Secrets"
echo "3. 访问 https://github.com/tyj1987/gupiao/actions 查看部署状态"
echo "4. 部署完成后访问 http://$PRODUCTION_SERVER:$APP_PORT"
echo ""

echo "🎯 CI/CD自动部署已配置完成！"
echo "推送代码到main分支将自动触发部署到生产环境。"
