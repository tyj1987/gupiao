#!/bin/bash
# =============================================================================
# 股票分析系统 - 环境检查脚本
# 检查系统环境是否满足部署要求
# =============================================================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# 检查结果
check_result=0

echo ""
echo "🔍 股票分析系统 - 环境检查"
echo "=========================="
echo ""

# 检查操作系统
log_info "检查操作系统..."
OS=$(uname -s)
ARCH=$(uname -m)
echo "操作系统: $OS $ARCH"

if [[ "$OS" == "Linux" ]]; then
    # 检查Linux发行版
    if [ -f /etc/os-release ]; then
        source /etc/os-release
        echo "发行版: $NAME $VERSION"
    fi
    log_success "操作系统检查通过"
elif [[ "$OS" == "Darwin" ]]; then
    echo "发行版: macOS $(sw_vers -productVersion)"
    log_success "操作系统检查通过"
else
    log_warning "未测试的操作系统: $OS"
fi

echo ""

# 检查内存
log_info "检查系统内存..."
if command -v free &> /dev/null; then
    MEMORY=$(free -m | awk 'NR==2{printf "%.0f", $2/1024}')
elif command -v vm_stat &> /dev/null; then
    # macOS
    MEMORY=$(echo "scale=0; $(vm_stat | grep "Pages free" | awk '{print $3}' | sed 's/\.//' ) * 4096 / 1024 / 1024 / 1024" | bc 2>/dev/null || echo "4")
else
    MEMORY="未知"
fi

echo "总内存: ${MEMORY}GB"
if [[ "$MEMORY" =~ ^[0-9]+$ ]] && [ "$MEMORY" -ge 2 ]; then
    log_success "内存充足 (推荐4GB+)"
else
    log_warning "内存可能不足，推荐4GB以上"
    check_result=1
fi

echo ""

# 检查磁盘空间
log_info "检查磁盘空间..."
DISK=$(df -h . | awk 'NR==2 {print $4}')
echo "可用空间: $DISK"
log_success "磁盘空间检查通过"

echo ""

# 检查网络连接
log_info "检查网络连接..."
if ping -c 1 baidu.com &> /dev/null; then
    log_success "网络连接正常"
else
    log_error "网络连接失败"
    check_result=1
fi

echo ""

# 检查Docker
log_info "检查 Docker..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | sed 's/,//')
    echo "Docker版本: $DOCKER_VERSION"
    
    # 检查Docker是否运行
    if docker ps &> /dev/null; then
        log_success "Docker运行正常"
    else
        log_error "Docker未运行，请启动Docker服务"
        check_result=1
    fi
else
    log_error "Docker未安装"
    echo "安装命令 (Ubuntu/Debian):"
    echo "  curl -fsSL https://get.docker.com -o get-docker.sh"
    echo "  sudo sh get-docker.sh"
    echo ""
    echo "安装命令 (CentOS/RHEL):"
    echo "  sudo yum install -y docker"
    echo "  sudo systemctl start docker"
    check_result=1
fi

echo ""

# 检查Docker Compose
log_info "检查 Docker Compose..."
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | sed 's/,//')
    echo "Docker Compose版本: $COMPOSE_VERSION"
    log_success "Docker Compose可用"
elif docker compose version &> /dev/null; then
    COMPOSE_VERSION=$(docker compose version | cut -d' ' -f3)
    echo "Docker Compose版本: $COMPOSE_VERSION (集成版)"
    log_success "Docker Compose可用"
else
    log_error "Docker Compose未安装"
    echo "安装命令:"
    echo "  sudo curl -L \"https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose"
    echo "  sudo chmod +x /usr/local/bin/docker-compose"
    check_result=1
fi

echo ""

# 检查端口占用
log_info "检查端口占用..."
ports_to_check=(8501 80 443)
occupied_ports=()

for port in "${ports_to_check[@]}"; do
    if netstat -tlnp 2>/dev/null | grep ":$port " > /dev/null || lsof -i ":$port" &> /dev/null; then
        occupied_ports+=($port)
    fi
done

if [ ${#occupied_ports[@]} -eq 0 ]; then
    log_success "所需端口均可用"
else
    log_warning "以下端口被占用: ${occupied_ports[*]}"
    echo "如果需要，请停止占用这些端口的服务"
fi

echo ""

# 检查Python（用于API密钥配置）
log_info "检查 Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "Python版本: $PYTHON_VERSION"
    log_success "Python可用"
else
    log_warning "Python3未安装（可选，用于高级配置）"
fi

echo ""

# 检查项目文件
log_info "检查项目文件..."
required_files=(
    "Dockerfile"
    "docker-compose.yml"
    "docker-compose.simple.yml"
    "config/api_keys.example.py"
    "requirements.txt"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=($file)
    fi
done

if [ ${#missing_files[@]} -eq 0 ]; then
    log_success "项目文件完整"
else
    log_error "缺少以下文件: ${missing_files[*]}"
    check_result=1
fi

echo ""

# 检查API密钥配置
log_info "检查 API 密钥配置..."
if [ -f "config/api_keys.py" ]; then
    if grep -q "your_tushare_token_here" config/api_keys.py; then
        log_warning "请配置 Tushare Token"
        echo "编辑 config/api_keys.py 文件，替换 your_tushare_token_here"
    else
        log_success "API密钥已配置"
    fi
else
    log_info "API密钥配置文件不存在，将在部署时创建"
fi

echo ""

# 总结
echo "=================================="
if [ $check_result -eq 0 ]; then
    log_success "🎉 环境检查通过！可以开始部署"
    echo ""
    echo "推荐部署方式:"
    echo "  1. Docker快速部署: ./docker-quick-deploy.sh"
    echo "  2. 手动Docker部署: docker-compose up -d"
    echo "  3. 查看完整指南: cat DEPLOYMENT_GUIDE.md"
else
    log_warning "⚠️  环境检查发现问题，请先解决上述问题"
    echo ""
    echo "常见解决方案:"
    echo "  1. 安装Docker: curl -fsSL https://get.docker.com | sh"
    echo "  2. 启动Docker: sudo systemctl start docker"
    echo "  3. 添加用户组: sudo usermod -aG docker \$USER"
    echo "  4. 重新登录或运行: newgrp docker"
fi

echo "=================================="
echo ""

exit $check_result
