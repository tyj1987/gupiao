#!/bin/bash
# Docker环境管理脚本

set -e

COMPOSE_FILE="docker-compose.yml"
PROJECT_NAME="gupiao"

function show_help() {
    echo "🐳 股票分析系统 Docker 管理工具"
    echo "================================="
    echo "使用方法: ./docker-manage.sh [命令]"
    echo ""
    echo "可用命令："
    echo "  build     - 构建Docker镜像"
    echo "  up        - 启动所有服务"
    echo "  down      - 停止所有服务"
    echo "  restart   - 重启所有服务"
    echo "  status    - 查看服务状态"
    echo "  logs      - 查看日志"
    echo "  shell     - 进入容器Shell"
    echo "  update    - 更新并重启服务"
    echo "  clean     - 清理容器和镜像"
    echo "  backup    - 备份数据"
    echo "  help      - 显示帮助"
    echo ""
}

function build_image() {
    echo "🔨 构建Docker镜像..."
    docker-compose -f $COMPOSE_FILE build --no-cache
    echo "✅ 镜像构建完成"
}

function start_services() {
    echo "🚀 启动Docker服务..."
    
    # 检查配置文件
    if [ ! -f "config/api_keys.py" ]; then
        echo "⚠️ 警告: config/api_keys.py 不存在"
        echo "请先配置API密钥:"
        echo "cp config/api_keys.example.py config/api_keys.py"
        echo "vim config/api_keys.py"
        read -p "是否继续启动? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "❌ 启动取消"
            exit 1
        fi
    fi
    
    docker-compose -f $COMPOSE_FILE up -d
    echo "✅ 服务启动完成"
    echo ""
    echo "🌐 访问地址:"
    echo "  - 直接访问: http://localhost:8501"
    echo "  - Nginx代理: http://localhost:80"
}

function stop_services() {
    echo "🛑 停止Docker服务..."
    docker-compose -f $COMPOSE_FILE down
    echo "✅ 服务停止完成"
}

function restart_services() {
    echo "🔄 重启Docker服务..."
    docker-compose -f $COMPOSE_FILE restart
    echo "✅ 服务重启完成"
}

function show_status() {
    echo "📊 Docker服务状态..."
    echo "===================="
    
    # 容器状态
    echo "🐳 容器状态:"
    docker-compose -f $COMPOSE_FILE ps
    echo ""
    
    # 网络状态
    echo "🌐 网络状态:"
    docker network ls | grep $PROJECT_NAME || echo "❌ 项目网络未创建"
    echo ""
    
    # 存储卷状态
    echo "💾 存储卷状态:"
    docker volume ls | grep $PROJECT_NAME || echo "❌ 项目存储卷未创建"
    echo ""
    
    # 镜像信息
    echo "📦 镜像信息:"
    docker images | grep $PROJECT_NAME || echo "❌ 项目镜像未找到"
}

function show_logs() {
    echo "📖 Docker服务日志..."
    
    if [ -n "$2" ]; then
        # 查看特定服务的日志
        docker-compose -f $COMPOSE_FILE logs -f "$2"
    else
        # 查看所有服务的日志
        docker-compose -f $COMPOSE_FILE logs -f
    fi
}

function enter_shell() {
    echo "🔧 进入容器Shell..."
    
    # 检查容器是否运行
    if ! docker-compose -f $COMPOSE_FILE ps | grep -q "Up"; then
        echo "❌ 容器未运行，请先启动服务"
        exit 1
    fi
    
    docker-compose -f $COMPOSE_FILE exec gupiao /bin/bash
}

function update_services() {
    echo "🔄 更新Docker服务..."
    
    # 停止服务
    docker-compose -f $COMPOSE_FILE down
    
    # 重新构建镜像
    docker-compose -f $COMPOSE_FILE build --no-cache
    
    # 启动服务
    docker-compose -f $COMPOSE_FILE up -d
    
    echo "✅ 服务更新完成"
}

function clean_environment() {
    echo "🧹 清理Docker环境..."
    
    read -p "⚠️ 这将删除所有容器、镜像和数据，确定继续? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ 清理取消"
        exit 1
    fi
    
    # 停止并删除容器
    docker-compose -f $COMPOSE_FILE down -v --rmi all
    
    # 清理悬挂的镜像和容器
    docker system prune -f
    
    echo "✅ 环境清理完成"
}

function backup_data() {
    echo "💾 备份Docker数据..."
    
    # 创建备份目录
    BACKUP_DIR="./backups"
    mkdir -p $BACKUP_DIR
    
    # 备份文件名
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/gupiao_docker_backup_$TIMESTAMP.tar.gz"
    
    # 备份存储卷数据
    docker run --rm \
        -v ${PROJECT_NAME}_gupiao_cache:/data/cache \
        -v ${PROJECT_NAME}_gupiao_logs:/data/logs \
        -v ${PROJECT_NAME}_gupiao_redis_data:/data/redis \
        -v $(pwd)/$BACKUP_DIR:/backup \
        alpine tar -czf /backup/$(basename $BACKUP_FILE) -C /data .
    
    echo "✅ 备份完成: $BACKUP_FILE"
    echo "📊 备份大小: $(du -h $BACKUP_FILE | cut -f1)"
}

function install_docker() {
    echo "🐳 安装Docker和Docker Compose..."
    
    # 检查操作系统
    if [ -f /etc/redhat-release ]; then
        # CentOS/RHEL
        echo "检测到CentOS/RHEL系统"
        
        # 安装Docker
        sudo yum install -y yum-utils
        sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
        sudo yum install -y docker-ce docker-ce-cli containerd.io
        
        # 启动Docker
        sudo systemctl start docker
        sudo systemctl enable docker
        
        # 安装Docker Compose
        sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        
    elif [ -f /etc/debian_version ]; then
        # Ubuntu/Debian
        echo "检测到Ubuntu/Debian系统"
        
        # 更新包索引
        sudo apt-get update
        
        # 安装依赖
        sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
        
        # 添加Docker官方GPG密钥
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
        
        # 添加Docker仓库
        echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        # 安装Docker
        sudo apt-get update
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io
        
        # 安装Docker Compose
        sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        
    else
        echo "❌ 不支持的操作系统"
        exit 1
    fi
    
    # 验证安装
    docker --version
    docker-compose --version
    
    echo "✅ Docker安装完成"
    echo "💡 建议将当前用户添加到docker组: sudo usermod -aG docker $USER"
}

# 主程序
case "$1" in
    build)
        build_image
        ;;
    up)
        start_services
        ;;
    down)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "$@"
        ;;
    shell)
        enter_shell
        ;;
    update)
        update_services
        ;;
    clean)
        clean_environment
        ;;
    backup)
        backup_data
        ;;
    install)
        install_docker
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "❌ 未知命令: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
