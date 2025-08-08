#!/bin/bash
# 生产环境部署脚本 - 使用优化后的干净项目结构
# 版本: v2.1.0 (优化版)

set -e  # 遇到错误立即退出

echo "🚀 开始部署干净优化版股票分析系统到生产环境..."
echo "=========================================================="

# 配置变量
DOCKER_IMAGE="tuoyongjun1987/gupiao-stock-analysis"
VERSION_TAG="v2.1.0-clean"
PRODUCTION_PORT="8501"
BACKUP_PORT="8502"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Docker环境
check_docker() {
    print_status "检查Docker环境..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker服务未运行，请启动Docker服务"
        exit 1
    fi
    
    print_success "Docker环境检查通过"
}

# 创建必要的目录
setup_directories() {
    print_status "创建生产环境目录结构..."
    
    mkdir -p logs data exports cache models
    chmod 755 logs data exports cache models
    
    print_success "目录结构创建完成"
}

# 备份当前运行的容器
backup_current_deployment() {
    print_status "备份当前部署..."
    
    if docker ps | grep -q "gupiao-app"; then
        print_warning "发现运行中的容器，创建备份..."
        
        # 停止当前容器并重新标记
        docker stop gupiao-app || true
        docker rename gupiao-app gupiao-app-backup-$(date +%Y%m%d_%H%M%S) || true
        
        print_success "当前部署已备份"
    else
        print_status "没有发现运行中的容器，跳过备份"
    fi
}

# 构建优化后的Docker镜像
build_optimized_image() {
    print_status "构建优化后的Docker镜像..."
    
    # 显示构建上下文大小
    print_status "检查构建上下文大小..."
    du -sh . | awk '{print "构建上下文大小: " $1}'
    
    # 运行项目清理脚本
    if [ -f "scripts/clean-project.sh" ]; then
        print_status "运行项目清理脚本..."
        bash scripts/clean-project.sh
    fi
    
    # 构建生产镜像
    print_status "开始构建Docker镜像 (标签: ${VERSION_TAG})..."
    
    # 使用优化后的Dockerfile
    docker build \
        --no-cache \
        --tag ${DOCKER_IMAGE}:${VERSION_TAG} \
        --tag ${DOCKER_IMAGE}:latest \
        --file Dockerfile \
        .
    
    # 显示镜像大小
    docker images ${DOCKER_IMAGE}:${VERSION_TAG} --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
    
    print_success "Docker镜像构建完成"
}

# 推送镜像到Docker Hub
push_image() {
    print_status "推送镜像到Docker Hub..."
    
    # 检查是否已登录Docker Hub
    if ! docker info | grep -q "Username"; then
        print_warning "请先登录Docker Hub:"
        echo "docker login -u tuoyongjun1987"
        read -p "是否已经登录? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_error "请先登录Docker Hub后再运行部署脚本"
            exit 1
        fi
    fi
    
    docker push ${DOCKER_IMAGE}:${VERSION_TAG}
    docker push ${DOCKER_IMAGE}:latest
    
    print_success "镜像推送完成"
}

# 使用docker-compose部署
deploy_with_compose() {
    print_status "使用Docker Compose部署生产环境..."
    
    # 创建生产环境的docker-compose配置
    cat > docker-compose.production.yml << EOF
version: '3.8'

services:
  gupiao-app:
    image: ${DOCKER_IMAGE}:${VERSION_TAG}
    container_name: gupiao-app
    restart: unless-stopped
    ports:
      - "${PRODUCTION_PORT}:8501"
    environment:
      - ENVIRONMENT=production
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
      - STREAMLIT_SERVER_HEADLESS=true
      - STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
      - ./exports:/app/exports
      - ./cache:/app/cache
      - ./models:/app/models
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    networks:
      - gupiao-network

networks:
  gupiao-network:
    driver: bridge
EOF

    # 启动服务
    docker-compose -f docker-compose.production.yml down || true
    docker-compose -f docker-compose.production.yml up -d
    
    print_success "生产环境部署完成"
}

# 健康检查
health_check() {
    print_status "执行健康检查..."
    
    # 等待服务启动
    sleep 10
    
    # 检查容器状态
    if docker ps | grep -q "gupiao-app"; then
        print_success "容器运行正常"
    else
        print_error "容器启动失败"
        docker logs gupiao-app
        exit 1
    fi
    
    # 检查HTTP响应
    max_attempts=30
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:${PRODUCTION_PORT}/healthz &> /dev/null; then
            print_success "应用健康检查通过"
            break
        else
            print_status "等待应用启动... (${attempt}/${max_attempts})"
            sleep 2
            ((attempt++))
        fi
    done
    
    if [ $attempt -gt $max_attempts ]; then
        print_error "应用健康检查失败"
        docker logs gupiao-app --tail 50
        exit 1
    fi
}

# 显示部署信息
show_deployment_info() {
    print_success "🎉 部署完成！"
    echo "=========================================================="
    echo "📊 部署信息:"
    echo "- 镜像版本: ${DOCKER_IMAGE}:${VERSION_TAG}"
    echo "- 访问地址: http://localhost:${PRODUCTION_PORT}"
    echo "- 容器名称: gupiao-app"
    echo ""
    echo "📁 数据目录:"
    echo "- 日志: ./logs"
    echo "- 数据: ./data"
    echo "- 导出: ./exports"
    echo "- 缓存: ./cache"
    echo "- 模型: ./models"
    echo ""
    echo "🔧 管理命令:"
    echo "- 查看日志: docker logs gupiao-app -f"
    echo "- 重启服务: docker-compose -f docker-compose.production.yml restart"
    echo "- 停止服务: docker-compose -f docker-compose.production.yml down"
    echo ""
    
    # 显示镜像大小对比
    print_status "镜像大小信息:"
    docker images ${DOCKER_IMAGE} --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedSince}}"
}

# 清理旧镜像和容器
cleanup_old_resources() {
    print_status "清理旧的Docker资源..."
    
    # 清理旧的镜像（保留最新3个版本）
    docker images ${DOCKER_IMAGE} --format "{{.ID}}" | tail -n +4 | xargs -r docker rmi || true
    
    # 清理未使用的镜像
    docker image prune -f || true
    
    print_success "Docker资源清理完成"
}

# 主部署流程
main() {
    echo "开始时间: $(date)"
    
    check_docker
    setup_directories
    backup_current_deployment
    build_optimized_image
    
    # 询问是否推送镜像
    read -p "是否推送镜像到Docker Hub? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        push_image
    fi
    
    deploy_with_compose
    health_check
    cleanup_old_resources
    show_deployment_info
    
    echo "完成时间: $(date)"
}

# 运行主流程
main "$@"
