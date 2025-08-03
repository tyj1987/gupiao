#!/bin/bash
# =============================================================================
# 股票分析系统 - Docker 快速部署脚本
# 一键部署，5分钟上线
# =============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    log_info "检查系统依赖..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi    
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi    
    
    log_success "依赖检查通过"
}

# 检查端口
check_ports() {
    log_info "检查端口占用..."
    
    if netstat -tlnp 2>/dev/null | grep :8501 > /dev/null; then
        log_warning "端口 8501 已被占用，将尝试停止现有服务"
        docker-compose down 2>/dev/null || true
    fi    
    
    if netstat -tlnp 2>/dev/null | grep :80 > /dev/null; then
        log_warning "端口 80 已被占用，可能影响 Nginx 服务"
    fi    
    
    log_success "端口检查完成"
}

# 配置API密钥
setup_api_keys() {
    log_info "配置 API 密钥..."
    
    if [ ! -f "config/api_keys.py" ]; then
        if [ -f "config/api_keys.example.py" ]; then
            cp config/api_keys.example.py config/api_keys.py
            log_success "已创建 API 密钥配置文件"
        else
            log_error "缺少 api_keys.example.py 文件"
            exit 1
        fi
    fi    
    
    # 检查是否已配置
    if grep -q "your_tushare_token_here" config/api_keys.py; then
        log_warning "请配置您的 Tushare Token："
        echo "1. 访问 https://tushare.pro/register 注册账号"
        echo "2. 获取 token"
        echo "3. 编辑 config/api_keys.py 文件，替换 your_tushare_token_here"
        echo ""
        read -p "是否现在配置 Token？(y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            read -p "请输入您的 Tushare Token: " token
            sed -i "s/your_tushare_token_here/$token/g" config/api_keys.py
            log_success "Token 配置完成"
        else
            log_warning "请稍后手动配置 Token"
        fi
    else
        log_success "API 密钥已配置"
    fi
}

# 选择部署模式
choose_deployment_mode() {
    log_info "选择部署模式..."
    echo ""
    echo "1. 简化模式 - 仅股票分析系统 (推荐新手)"
    echo "2. 完整模式 - 包含 Nginx + Redis (推荐生产)"
    echo ""
    read -p "请选择部署模式 (1/2): " -n 1 -r
    echo
    
    case $REPLY in
        1)
            COMPOSE_FILE="docker-compose.simple.yml"
            MODE="简化模式"
            PORTS="8501"
            ;; 
        2)
            COMPOSE_FILE="docker-compose.yml"
            MODE="完整模式"
            PORTS="80, 8501"
            ;; 
        *)
            log_warning "无效选择，使用简化模式"
            COMPOSE_FILE="docker-compose.simple.yml"
            MODE="简化模式"
            PORTS="8501"
            ;; 
    esac    
    
    log_success "选择了 $MODE"
}

# 构建镜像
build_images() {
    log_info "构建 Docker 镜像..."
    
    if [ "$COMPOSE_FILE" = "docker-compose.simple.yml" ]; then
        docker build -t stock-analyzer .
    else
        docker-compose -f $COMPOSE_FILE build
    fi    
    
    log_success "镜像构建完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    if [ "$COMPOSE_FILE" = "docker-compose.simple.yml" ]; then
        docker run -d \
            --name stock-analyzer \
            -p 8501:8501 \
            -v $(pwd)/config:/app/config \
            -v $(pwd)/data:/app/data \
            --restart unless-stopped \
            stock-analyzer
    else
        docker-compose -f $COMPOSE_FILE up -d
    fi    
    
    log_success "服务启动完成"
}

# 等待服务就绪
wait_for_service() {
    log_info "等待服务启动..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:8501/_stcore/health &> /dev/null; then
            log_success "服务已就绪"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    log_error "服务启动超时"
    return 1
}

# 显示部署信息
show_deployment_info() {
    log_success "🎉 部署完成！"
    echo ""
    echo "==============================================="
    echo "    股票分析系统部署成功"
    echo "==============================================="
    echo "部署模式: $MODE"
    echo "访问地址: http://localhost:8501"
    echo "开放端口: $PORTS"
    echo "股票数量: 5,728 只股票 (A股+港股+美股)"
    echo ""
    echo "🌟 主要功能:"
    echo "  • 全市场股票搜索"
    echo "  • 智能风险评估"
    echo "  • 实时数据获取"
    echo "  • 投资建议分析"
    echo ""
    echo "�️  管理命令:"
    echo "  查看状态: docker ps"
    echo "  查看日志: docker logs stock-analyzer"
    echo "  重启服务: docker restart stock-analyzer"
    echo "  停止服务: docker stop stock-analyzer"
    echo ""
    if [ "$COMPOSE_FILE" = "docker-compose.yml" ]; then
        echo "  或使用 docker-compose 命令:"
        echo "  docker-compose -f $COMPOSE_FILE ps"
        echo "  docker-compose -f $COMPOSE_FILE logs"
        echo "  docker-compose -f $COMPOSE_FILE restart"
        echo "  docker-compose -f $COMPOSE_FILE down"
        echo ""
    fi
    echo "📚 完整文档: 查看 DEPLOYMENT_GUIDE.md"
    echo "==============================================="
}

# 错误处理
cleanup_on_error() {
    log_error "部署失败，正在清理..."
    
    if [ "$COMPOSE_FILE" = "docker-compose.simple.yml" ]; then
        docker stop stock-analyzer 2>/dev/null || true
        docker rm stock-analyzer 2>/dev/null || true
    else
        docker-compose -f $COMPOSE_FILE down 2>/dev/null || true
    fi    
    
    exit 1
}

# 主函数
main() {
    echo ""
    echo "🚀 股票分析系统 - Docker 快速部署"
    echo "=================================="
    echo ""
    
    # 设置错误处理
    trap cleanup_on_error ERR
    
    # 执行部署步骤
    check_dependencies
    check_ports
    setup_api_keys
    choose_deployment_mode
    build_images
    start_services
    
    # 等待服务就绪
    if wait_for_service; then
        show_deployment_info
    else
        cleanup_on_error
    fi
}

# 执行主函数
main "$@"
