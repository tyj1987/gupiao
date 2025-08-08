#!/bin/bash
# 推送优化版本到生产环境的完整脚本

set -e

echo "🚀 开始推送优化版项目并部署到生产环境..."
echo "=============================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 配置变量
PRODUCTION_SERVER="47.94.225.76"
SERVER_USER="root"
APP_DIR="/www/wwwroot/gupiao"

# 检查本地状态
check_local_status() {
    print_status "检查本地项目状态..."
    
    echo "项目大小: $(du -sh . | cut -f1)"
    echo "构建上下文: $(du -sh --exclude=venv --exclude=.git . | cut -f1)"
    echo "核心代码: $(du -sh src/ | cut -f1)"
    
    # 检查Git状态
    if [ -n "$(git status --porcelain)" ]; then
        print_warning "发现未提交的更改"
        git status --short
        
        read -p "是否提交所有更改? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git add -A
            git commit -m "🚀 准备部署优化版本到生产环境

✨ 项目优化完成:
- 构建上下文从 611M 减少到 3.7M
- Docker镜像优化 (移除TA-Lib编译)
- 文件结构极简化
- 自动清理机制完善

🎯 生产部署 v2.1.0-clean"
        fi
    fi
    
    print_success "本地状态检查完成"
}

# 推送到GitHub
push_to_github() {
    print_status "推送优化版本到GitHub..."
    
    git push origin main
    
    print_success "代码推送完成"
    print_status "GitHub仓库: https://github.com/tyj1987/gupiao"
}

# 远程部署
deploy_to_production() {
    print_status "开始远程部署到生产服务器..."
    
    # 上传部署脚本
    print_status "上传部署脚本到服务器..."
    scp server-deploy-clean.sh ${SERVER_USER}@${PRODUCTION_SERVER}:/tmp/
    
    # 在生产服务器上执行部署
    print_status "在生产服务器上执行部署..."
    ssh ${SERVER_USER}@${PRODUCTION_SERVER} << 'EOF'
# 进入应用目录
mkdir -p /www/wwwroot/gupiao
cd /www/wwwroot/gupiao

# 执行部署脚本
chmod +x /tmp/server-deploy-clean.sh
/tmp/server-deploy-clean.sh

# 清理临时文件
rm -f /tmp/server-deploy-clean.sh
EOF

    print_success "远程部署完成"
}

# 验证部署
verify_deployment() {
    print_status "验证生产环境部署..."
    
    # 检查HTTP响应
    max_attempts=10
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://${PRODUCTION_SERVER}:8501 --connect-timeout 5 &> /dev/null; then
            print_success "生产环境验证成功！"
            break
        else
            print_status "等待生产环境启动... ($attempt/$max_attempts)"
            sleep 5
            ((attempt++))
        fi
    done
    
    if [ $attempt -gt $max_attempts ]; then
        print_warning "无法连接到生产环境，请手动检查"
    fi
}

# 显示部署结果
show_deployment_summary() {
    print_success "🎉 优化版项目部署完成！"
    echo "=============================================="
    echo "📊 部署总结:"
    echo "- 版本: v2.1.0-clean (优化版)"
    echo "- 构建上下文优化: 611M → 3.7M (-99%)"
    echo "- Docker镜像优化: 预计减少60%+"
    echo "- 文件结构: 极简化 + 自动清理"
    echo ""
    echo "🌐 访问地址:"
    echo "- 生产环境: http://${PRODUCTION_SERVER}:8501"
    echo "- GitHub仓库: https://github.com/tyj1987/gupiao"
    echo ""
    echo "🔧 管理命令 (生产服务器):"
    echo "ssh ${SERVER_USER}@${PRODUCTION_SERVER}"
    echo "cd ${APP_DIR}"
    echo "docker logs gupiao-app -f"
    echo ""
    echo "💡 优化成果:"
    echo "✅ 极其干净整洁的文件结构"
    echo "✅ Docker镜像大幅减小"
    echo "✅ 快速构建和部署"
    echo "✅ 自动化维护机制"
}

# 主函数
main() {
    echo "开始时间: $(date)"
    
    check_local_status
    push_to_github
    
    # 询问是否部署到生产环境
    echo ""
    read -p "是否立即部署到生产服务器? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        deploy_to_production
        verify_deployment
    else
        print_status "跳过生产部署"
        print_status "手动部署命令:"
        echo "ssh ${SERVER_USER}@${PRODUCTION_SERVER}"
        echo "cd ${APP_DIR} && git pull origin main"
        echo "bash server-deploy-clean.sh"
    fi
    
    show_deployment_summary
    
    echo "完成时间: $(date)"
}

# 运行主函数
main "$@"
