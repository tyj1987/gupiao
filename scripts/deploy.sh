#!/bin/bash
# -*- coding: utf-8 -*-
# 股票分析系统智能部署脚本
# 支持传统模式和Docker模式，自动检测系统环境

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 脚本信息
SCRIPT_VERSION="2.0.0"
PROJECT_NAME="股票分析系统"
PROJECT_VERSION="2.1.0"

# 默认配置
DEFAULT_PORT=8501
DEFAULT_DOCKER_PORT=8501
DEFAULT_NGINX_PORT=80
DEPLOY_MODE=""
SYSTEM_TYPE=""
PANEL_TYPE=""

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

log_header() {
    echo -e "${BLUE}======================================${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}======================================${NC}"
}

# 显示帮助信息
show_help() {
    cat << EOF
🚀 ${PROJECT_NAME} 智能部署脚本 v${SCRIPT_VERSION}

用法: $0 [选项]

选项:
    -h, --help              显示此帮助信息
    -v, --version           显示版本信息
    -m, --mode MODE         部署模式 (traditional|docker|auto)
    -p, --port PORT         服务端口 (默认: ${DEFAULT_PORT})
    --docker-port PORT      Docker端口 (默认: ${DEFAULT_DOCKER_PORT})
    --nginx-port PORT       Nginx端口 (默认: ${DEFAULT_NGINX_PORT})
    --force                 强制重新部署
    --check                 仅检查环境，不部署

部署模式:
    traditional            传统部署模式 (直接运行)
    docker                 Docker容器模式
    auto                   自动选择最佳模式 (默认)

示例:
    $0                      # 自动部署
    $0 -m docker            # 使用Docker模式部署
    $0 -m traditional -p 8080  # 传统模式，端口8080
    $0 --check              # 仅检查环境

支持系统:
    - CentOS 7/8/9, AlmaLinux 8/9, Rocky Linux 8/9
    - Ubuntu 18.04/20.04/22.04, Debian 10/11/12
    - 宝塔面板、1Panel、aaPanel等面板环境

EOF
}

# 检测系统类型
detect_system() {
    log_info "检测系统类型..."
    
    if [[ -f /etc/os-release ]]; then
        source /etc/os-release
        case $ID in
            centos|rhel|almalinux|rocky)
                SYSTEM_TYPE="rhel"
                log_info "检测到: $PRETTY_NAME (RHEL系列)"
                ;;
            ubuntu|debian)
                SYSTEM_TYPE="debian"
                log_info "检测到: $PRETTY_NAME (Debian系列)"
                ;;
            *)
                SYSTEM_TYPE="unknown"
                log_warning "检测到未知系统: $PRETTY_NAME"
                ;;
        esac
    else
        SYSTEM_TYPE="unknown"
        log_warning "无法检测系统类型"
    fi
}

# 检测面板类型
detect_panel() {
    log_info "检测服务器面板..."
    
    if [[ -d /www/server/panel ]] && command -v bt &> /dev/null; then
        PANEL_TYPE="baota"
        log_info "检测到: 宝塔面板"
    elif [[ -d /opt/1panel ]] && command -v 1pctl &> /dev/null; then
        PANEL_TYPE="1panel"
        log_info "检测到: 1Panel面板"
    elif [[ -d /www/server/panel ]] && [[ -f /www/server/panel/data/admin_path.pl ]]; then
        PANEL_TYPE="aapanel"
        log_info "检测到: aaPanel面板"
    else
        PANEL_TYPE="none"
        log_info "未检测到服务器面板"
    fi
}

# 检查依赖
check_dependencies() {
    log_info "检查系统依赖..."
    
    local missing_deps=()
    
    # 基础工具检查
    local basic_tools=("curl" "wget" "git" "python3" "pip3")
    for tool in "${basic_tools[@]}"; do
        if ! command -v $tool &> /dev/null; then
            missing_deps+=($tool)
        fi
    done
    
    # Docker检查
    if ! command -v docker &> /dev/null; then
        log_warning "Docker未安装"
    else
        log_success "Docker已安装: $(docker --version)"
        if ! docker info &> /dev/null; then
            log_warning "Docker服务未运行"
        fi
    fi
    
    # Docker Compose检查
    if ! command -v docker-compose &> /dev/null; then
        log_warning "Docker Compose未安装"
    fi
    
    # Python环境检查
    if command -v python3 &> /dev/null; then
        local python_version=$(python3 --version | cut -d' ' -f2)
        log_success "Python版本: $python_version"
        
        # 检查pip
        if command -v pip3 &> /dev/null; then
            log_success "pip3已安装"
        else
            missing_deps+=("python3-pip")
        fi
    else
        missing_deps+=("python3")
    fi
    
    # 报告缺失依赖
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_warning "缺失依赖: ${missing_deps[*]}"
        return 1
    else
        log_success "所有基础依赖已满足"
        return 0
    fi
}

# 安装依赖
install_dependencies() {
    log_info "安装缺失的依赖..."
    
    case $SYSTEM_TYPE in
        rhel)
            # RHEL系列系统
            if command -v dnf &> /dev/null; then
                PKG_MANAGER="dnf"
            else
                PKG_MANAGER="yum"
            fi
            
            log_info "更新软件包列表..."
            $PKG_MANAGER update -y
            
            log_info "安装基础依赖..."
            $PKG_MANAGER install -y curl wget git python3 python3-pip
            
            # 安装Docker
            if ! command -v docker &> /dev/null; then
                log_info "安装Docker..."
                curl -fsSL https://get.docker.com | sh
                systemctl enable docker
                systemctl start docker
                usermod -aG docker $(whoami) 2>/dev/null || true
            fi
            ;;
            
        debian)
            # Debian系列系统
            log_info "更新软件包列表..."
            apt update
            
            log_info "安装基础依赖..."
            apt install -y curl wget git python3 python3-pip python3-venv
            
            # 安装Docker
            if ! command -v docker &> /dev/null; then
                log_info "安装Docker..."
                curl -fsSL https://get.docker.com | sh
                systemctl enable docker
                systemctl start docker
                usermod -aG docker $(whoami) 2>/dev/null || true
            fi
            ;;
            
        *)
            log_error "不支持的系统类型，请手动安装依赖"
            return 1
            ;;
    esac
    
    # 安装Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_info "安装Docker Compose..."
        local compose_version=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
        curl -L "https://github.com/docker/compose/releases/download/${compose_version}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
    fi
}

# 选择部署模式
select_deploy_mode() {
    if [[ -n "$DEPLOY_MODE" ]]; then
        return 0
    fi
    
    log_info "选择部署模式..."
    
    # 检查Docker可用性
    local docker_available=false
    if command -v docker &> /dev/null && docker info &> /dev/null; then
        docker_available=true
    fi
    
    # 自动选择模式
    if [[ "$DEPLOY_MODE" == "auto" || -z "$DEPLOY_MODE" ]]; then
        if [[ "$docker_available" == true ]]; then
            DEPLOY_MODE="docker"
            log_info "自动选择: Docker模式"
        else
            DEPLOY_MODE="traditional"
            log_info "自动选择: 传统模式"
        fi
    fi
    
    log_success "部署模式: $DEPLOY_MODE"
}

# 传统部署模式
deploy_traditional() {
    log_header "传统模式部署"
    
    # 创建虚拟环境
    log_info "创建Python虚拟环境..."
    if [[ ! -d "venv" ]]; then
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 升级pip
    log_info "升级pip..."
    pip install --upgrade pip
    
    # 安装依赖
    log_info "安装Python依赖..."
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt
    else
        log_error "requirements.txt文件不存在"
        return 1
    fi
    
    # 创建配置文件
    log_info "配置应用..."
    if [[ ! -f "config/api_keys.py" ]]; then
        if [[ -f "config/api_keys.example.py" ]]; then
            cp config/api_keys.example.py config/api_keys.py
            log_warning "请编辑 config/api_keys.py 配置API密钥"
        fi
    fi
    
    # 创建启动脚本
    cat > start_traditional.sh << EOF
#!/bin/bash
cd "\$(dirname "\$0")"
source venv/bin/activate
export PYTHONPATH="\$PYTHONPATH:\$(pwd)"
streamlit run src/ui/streamlit_app.py --server.port=$DEFAULT_PORT --server.address=0.0.0.0
EOF
    chmod +x start_traditional.sh
    
    # 创建服务文件
    create_systemd_service
    
    log_success "传统模式部署完成"
    log_info "启动命令: ./start_traditional.sh"
    log_info "或使用服务: systemctl start stock-analysis"
}

# Docker部署模式
deploy_docker() {
    log_header "Docker模式部署"
    
    # 检查Dockerfile
    if [[ ! -f "Dockerfile" ]]; then
        create_dockerfile
    fi
    
    # 检查docker-compose.yml
    if [[ ! -f "docker-compose.yml" ]]; then
        create_docker_compose
    fi
    
    # 构建镜像
    log_info "构建Docker镜像..."
    docker-compose build
    
    # 启动服务
    log_info "启动Docker服务..."
    docker-compose up -d
    
    log_success "Docker模式部署完成"
    log_info "服务状态: docker-compose ps"
    log_info "查看日志: docker-compose logs -f"
    log_info "停止服务: docker-compose down"
}

# 创建Dockerfile
create_dockerfile() {
    log_info "创建Dockerfile..."
    cat > Dockerfile << 'EOF'
FROM python:3.9-slim

LABEL maintainer="Stock Analysis System"
LABEL version="2.1.0"

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建非root用户
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 8501

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/healthz || exit 1

# 启动命令
CMD ["streamlit", "run", "src/ui/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
EOF
}

# 创建docker-compose文件
create_docker_compose() {
    log_info "创建docker-compose.yml..."
    cat > docker-compose.yml << EOF
version: '3.8'

services:
  stock-analysis:
    build: .
    container_name: stock-analysis
    ports:
      - "${DEFAULT_DOCKER_PORT}:8501"
    environment:
      - PYTHONPATH=/app
      - TZ=Asia/Shanghai
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - stock-network

  nginx:
    image: nginx:alpine
    container_name: stock-analysis-nginx
    ports:
      - "${DEFAULT_NGINX_PORT}:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - stock-analysis
    restart: unless-stopped
    networks:
      - stock-network

networks:
  stock-network:
    driver: bridge
EOF
}

# 创建systemd服务
create_systemd_service() {
    log_info "创建systemd服务..."
    
    local service_file="/etc/systemd/system/stock-analysis.service"
    local current_user=$(whoami)
    local current_dir=$(pwd)
    
    cat > $service_file << EOF
[Unit]
Description=Stock Analysis System
After=network.target

[Service]
Type=simple
User=$current_user
WorkingDirectory=$current_dir
ExecStart=$current_dir/start_traditional.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable stock-analysis
}

# 面板集成配置
configure_panel() {
    case $PANEL_TYPE in
        baota)
            log_info "配置宝塔面板集成..."
            configure_baota_panel
            ;;
        1panel)
            log_info "配置1Panel集成..."
            configure_1panel
            ;;
        aapanel)
            log_info "配置aaPanel集成..."
            configure_aapanel
            ;;
        none)
            log_info "跳过面板配置"
            ;;
    esac
}

# 宝塔面板配置
configure_baota_panel() {
    local bt_site_path="/www/wwwroot/stock-analysis"
    
    # 创建站点目录软链接
    if [[ "$DEPLOY_MODE" == "traditional" ]]; then
        ln -sf $(pwd) $bt_site_path 2>/dev/null || true
        
        # 创建Nginx配置
        cat > bt_nginx.conf << EOF
location / {
    proxy_pass http://127.0.0.1:$DEFAULT_PORT;
    proxy_http_version 1.1;
    proxy_set_header Upgrade \$http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host \$host;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;
}
EOF
        log_info "宝塔Nginx配置已生成: bt_nginx.conf"
    fi
}

# 1Panel配置
configure_1panel() {
    log_info "生成1Panel应用配置..."
    # 1Panel通常使用Docker方式，配置会在面板中手动操作
    echo "请在1Panel面板中创建Docker应用，使用项目根目录的docker-compose.yml"
}

# 安全配置
configure_security() {
    log_info "配置安全设置..."
    
    # 防火墙配置
    if command -v firewall-cmd &> /dev/null; then
        # CentOS/RHEL 防火墙
        firewall-cmd --add-port=$DEFAULT_PORT/tcp --permanent 2>/dev/null || true
        firewall-cmd --reload 2>/dev/null || true
    elif command -v ufw &> /dev/null; then
        # Ubuntu/Debian 防火墙
        ufw allow $DEFAULT_PORT 2>/dev/null || true
    fi
    
    # SELinux配置
    if command -v setsebool &> /dev/null; then
        setsebool -P httpd_can_network_connect 1 2>/dev/null || true
    fi
}

# 部署后检查
post_deploy_check() {
    log_info "部署后检查..."
    
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -s http://localhost:$DEFAULT_PORT > /dev/null; then
            log_success "服务启动成功！"
            log_info "访问地址: http://localhost:$DEFAULT_PORT"
            if [[ "$PANEL_TYPE" != "none" ]]; then
                log_info "面板代理配置后可通过域名访问"
            fi
            return 0
        fi
        
        log_info "等待服务启动... ($attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
    
    log_error "服务启动失败，请检查日志"
    return 1
}

# 显示部署信息
show_deploy_info() {
    log_header "部署完成信息"
    
    echo -e "${GREEN}🎉 ${PROJECT_NAME} 部署成功！${NC}"
    echo
    echo -e "${BLUE}访问信息:${NC}"
    echo -e "  本地访问: http://localhost:$DEFAULT_PORT"
    
    if [[ "$DEPLOY_MODE" == "docker" ]]; then
        echo -e "  Docker服务: docker-compose ps"
        echo -e "  查看日志: docker-compose logs -f"
        echo -e "  重启服务: docker-compose restart"
        echo -e "  停止服务: docker-compose down"
    else
        echo -e "  服务管理: systemctl {start|stop|restart|status} stock-analysis"
        echo -e "  直接启动: ./start_traditional.sh"
    fi
    
    echo
    echo -e "${BLUE}系统信息:${NC}"
    echo -e "  系统类型: $SYSTEM_TYPE"
    echo -e "  面板类型: $PANEL_TYPE"
    echo -e "  部署模式: $DEPLOY_MODE"
    echo -e "  服务端口: $DEFAULT_PORT"
    
    echo
    echo -e "${YELLOW}注意事项:${NC}"
    echo -e "  1. 首次使用请配置API密钥 (config/api_keys.py)"
    echo -e "  2. 确保防火墙已开放端口 $DEFAULT_PORT"
    echo -e "  3. 生产环境建议使用Nginx反向代理"
    echo -e "  4. 定期更新依赖包保持安全性"
    
    if [[ "$PANEL_TYPE" != "none" ]]; then
        echo
        echo -e "${BLUE}面板集成:${NC}"
        echo -e "  已检测到 $PANEL_TYPE 面板"
        echo -e "  请参考生成的配置文件进行面板设置"
    fi
}

# 主函数
main() {
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--version)
                echo "${PROJECT_NAME} 部署脚本 v${SCRIPT_VERSION}"
                exit 0
                ;;
            -m|--mode)
                DEPLOY_MODE="$2"
                shift 2
                ;;
            -p|--port)
                DEFAULT_PORT="$2"
                shift 2
                ;;
            --docker-port)
                DEFAULT_DOCKER_PORT="$2"
                shift 2
                ;;
            --nginx-port)
                DEFAULT_NGINX_PORT="$2"
                shift 2
                ;;
            --force)
                FORCE_DEPLOY="true"
                shift
                ;;
            --check)
                CHECK_ONLY="true"
                shift
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 显示标题
    log_header "${PROJECT_NAME} 智能部署脚本 v${SCRIPT_VERSION}"
    
    # 检查权限
    if [[ $EUID -eq 0 ]] && [[ -z "$ALLOW_ROOT" ]]; then
        log_warning "建议使用非root用户运行此脚本"
        read -p "继续执行？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # 系统检测
    detect_system
    detect_panel
    
    # 检查依赖
    if ! check_dependencies; then
        if [[ "$CHECK_ONLY" == "true" ]]; then
            log_info "仅检查模式，退出"
            exit 0
        fi
        
        log_info "正在安装缺失的依赖..."
        install_dependencies
    fi
    
    if [[ "$CHECK_ONLY" == "true" ]]; then
        log_success "环境检查通过"
        exit 0
    fi
    
    # 选择部署模式
    select_deploy_mode
    
    # 执行部署
    case $DEPLOY_MODE in
        traditional)
            deploy_traditional
            ;;
        docker)
            deploy_docker
            ;;
        *)
            log_error "不支持的部署模式: $DEPLOY_MODE"
            exit 1
            ;;
    esac
    
    # 面板集成配置
    configure_panel
    
    # 安全配置
    configure_security
    
    # 部署后检查
    post_deploy_check
    
    # 显示部署信息
    show_deploy_info
    
    log_success "部署完成！"
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
