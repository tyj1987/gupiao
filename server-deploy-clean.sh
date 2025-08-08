#!/bin/bash
# 生产服务器部署脚本 - 远程执行版本
# 该脚本在生产服务器上执行

set -e

echo "🚀 生产服务器部署开始..."
echo "服务器IP: 47.94.225.76"
echo "时间: $(date)"

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
APP_DIR="/www/wwwroot/gupiao"
DOCKER_IMAGE="tuoyongjun1987/gupiao-stock-analysis"
VERSION_TAG="v2.1.0-clean"
CONTAINER_NAME="gupiao-app"
PORT="8501"

# 检查环境
check_environment() {
    print_status "检查生产服务器环境..."
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装"
        exit 1
    fi
    
    # 检查Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose 未安装"
        exit 1
    fi
    
    print_success "环境检查通过"
}

# 创建应用目录
setup_app_directory() {
    print_status "设置应用目录..."
    
    mkdir -p $APP_DIR
    cd $APP_DIR
    
    # 创建数据目录
    mkdir -p logs data exports cache models
    chmod 755 logs data exports cache models
    
    print_success "应用目录设置完成"
}

# 备份当前部署
backup_current() {
    print_status "备份当前部署..."
    
    if docker ps | grep -q $CONTAINER_NAME; then
        print_warning "停止现有容器..."
        docker stop $CONTAINER_NAME || true
        docker rename $CONTAINER_NAME ${CONTAINER_NAME}-backup-$(date +%Y%m%d_%H%M%S) || true
    fi
    
    print_success "备份完成"
}

# 从GitHub拉取最新代码
pull_latest_code() {
    print_status "从GitHub拉取最新代码..."
    
    if [ -d ".git" ]; then
        git pull origin main
    else
        git clone https://github.com/tyj1987/gupiao.git .
    fi
    
    print_success "代码拉取完成"
}

# 构建Docker镜像
build_image() {
    print_status "构建优化版Docker镜像..."
    
    # 显示构建上下文大小
    print_status "构建上下文大小: $(du -sh --exclude=venv --exclude=.git . | cut -f1)"
    
    # 构建镜像
    docker build \
        --no-cache \
        --tag $DOCKER_IMAGE:$VERSION_TAG \
        --tag $DOCKER_IMAGE:latest \
        --file Dockerfile \
        .
    
    # 显示镜像信息
    print_status "镜像信息:"
    docker images $DOCKER_IMAGE:$VERSION_TAG --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedSince}}"
    
    print_success "镜像构建完成"
}

# 部署应用
deploy_app() {
    print_status "部署应用..."
    
    # 创建docker-compose配置
    cat > docker-compose.production.yml << EOF
version: '3.8'

services:
  gupiao-app:
    image: $DOCKER_IMAGE:$VERSION_TAG
    container_name: $CONTAINER_NAME
    restart: unless-stopped
    ports:
      - "$PORT:8501"
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
    docker-compose -f docker-compose.production.yml up -d
    
    print_success "应用部署完成"
}

# 健康检查
health_check() {
    print_status "执行健康检查..."
    
    sleep 10
    
    # 检查容器状态
    if docker ps | grep -q $CONTAINER_NAME; then
        print_success "容器运行正常"
    else
        print_error "容器启动失败"
        docker logs $CONTAINER_NAME
        exit 1
    fi
    
    # 检查应用响应
    max_attempts=30
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:$PORT/healthz &> /dev/null || curl -f http://localhost:$PORT &> /dev/null; then
            print_success "应用健康检查通过"
            break
        else
            print_status "等待应用启动... ($attempt/$max_attempts)"
            sleep 2
            ((attempt++))
        fi
    done
    
    if [ $attempt -gt $max_attempts ]; then
        print_error "应用健康检查失败"
        docker logs $CONTAINER_NAME --tail 50
        exit 1
    fi
}

# 清理资源
cleanup() {
    print_status "清理旧资源..."
    
    # 清理旧镜像
    docker images $DOCKER_IMAGE --format "{{.ID}}" | tail -n +4 | xargs -r docker rmi || true
    docker image prune -f || true
    
    # 清理旧容器
    docker ps -a | grep "${CONTAINER_NAME}-backup" | awk '{print $1}' | head -n -2 | xargs -r docker rm || true
    
    print_success "资源清理完成"
}

# 显示部署结果
show_result() {
    print_success "🎉 部署成功完成！"
    echo "============================================"
    echo "📊 部署信息:"
    echo "- 镜像: $DOCKER_IMAGE:$VERSION_TAG"
    echo "- 容器: $CONTAINER_NAME"
    echo "- 端口: $PORT"
    echo "- 访问地址: http://47.94.225.76:$PORT"
    echo ""
    echo "📁 数据目录:"
    echo "- 应用目录: $APP_DIR"
    echo "- 日志: $APP_DIR/logs"
    echo "- 数据: $APP_DIR/data"
    echo ""
    echo "🔧 管理命令:"
    echo "- 查看日志: docker logs $CONTAINER_NAME -f"
    echo "- 重启: docker-compose -f docker-compose.production.yml restart"
    echo "- 停止: docker-compose -f docker-compose.production.yml down"
    echo ""
    echo "镜像大小信息:"
    docker images $DOCKER_IMAGE --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
}

# 主函数
main() {
    echo "部署开始时间: $(date)"
    
    check_environment
    setup_app_directory
    backup_current
    pull_latest_code
    build_image
    deploy_app
    health_check
    cleanup
    show_result
    
    echo "部署完成时间: $(date)"
}

# 执行主函数
main "$@"
