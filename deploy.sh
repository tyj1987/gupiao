#!/bin/bash
# 通用自动部署脚本 - 支持多种Linux发行版
# 使用方法: chmod +x deploy.sh && ./deploy.sh

set -e  # 遇到错误立即退出

echo "🚀 开始部署股票分析系统..."
echo "================================"

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用root用户运行此脚本"
    exit 1
fi

# 自动检测系统类型
detect_system() {
    if [ -f /etc/redhat-release ]; then
        DISTRO="redhat"
        OS_INFO=$(cat /etc/redhat-release)
    elif [ -f /etc/debian_version ]; then
        DISTRO="debian"
        OS_INFO=$(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)
    else
        DISTRO="unknown"
        OS_INFO="Unknown Linux"
    fi
}

# 检测系统
detect_system

# 配置变量
PROJECT_DIR="/www/wwwroot/gupiao"
PYTHON_CMD="python3"
PIP_CMD="pip3"

echo "📋 系统信息检查..."
echo "操作系统: $OS_INFO"
echo "发行版类型: $DISTRO"
echo "Python版本: $(python3 --version 2>/dev/null || echo 'Python未安装')"
echo "当前用户: $(whoami)"
echo "项目目录: $PROJECT_DIR"

# 自动安装系统依赖
install_system_dependencies() {
    echo ""
    echo "� 安装系统依赖..."
    
    if [ "$DISTRO" = "redhat" ]; then
        # RedHat系列 (CentOS, AlmaLinux, RHEL)
        echo "检测到RedHat系列系统，安装依赖..."
        
        # 更新包管理器
        if command -v dnf >/dev/null 2>&1; then
            PKG_MGR="dnf"
        else
            PKG_MGR="yum"
        fi
        
        # 安装基础工具
        $PKG_MGR install -y epel-release
        $PKG_MGR update -y
        
        # 安装Python和相关工具
        # AlmaLinux/RHEL 9+ 中venv是内置的，不需要单独安装python3-venv包
        $PKG_MGR install -y python3 python3-pip python3-devel
        $PKG_MGR install -y gcc gcc-c++ make git curl wget
        
        # 尝试安装supervisor和firewalld（可能在不同仓库中）
        $PKG_MGR install -y firewalld || echo "⚠️ firewalld安装失败，稍后手动配置"
        $PKG_MGR install -y supervisor || echo "⚠️ supervisor安装失败，将使用pip安装"
        
        # 对于AlmaLinux 9.x，确保有virtualenv（如果venv不可用）
        if ! python3 -m venv --help >/dev/null 2>&1; then
            echo "内置venv不可用，安装virtualenv..."
            python3 -m pip install --user virtualenv
        else
            echo "✅ 检测到内置venv模块"
        fi
        
    elif [ "$DISTRO" = "debian" ]; then
        # Debian系列 (Ubuntu, Debian)
        echo "检测到Debian系列系统，安装依赖..."
        apt-get update -y
        apt-get install -y python3 python3-pip python3-venv python3-dev
        apt-get install -y build-essential git curl wget
        apt-get install -y supervisor ufw
        
    else
        echo "⚠️ 未识别的系统类型，尝试通用安装..."
        # 尝试通用方法
        python3 -m pip install --user virtualenv
    fi
    
    echo "✅ 系统依赖安装完成"
}

# 检查并安装Python依赖
check_python_environment() {
    echo ""
    echo "🐍 检查Python环境..."
    
    # 检查Python版本
    if ! command -v python3 >/dev/null 2>&1; then
        echo "❌ Python3 未安装"
        install_system_dependencies
    fi
    
    # 检查pip
    if ! command -v pip3 >/dev/null 2>&1; then
        echo "安装pip3..."
        if [ "$DISTRO" = "redhat" ]; then
            # 确保使用正确的包管理器变量
            if command -v dnf >/dev/null 2>&1; then
                dnf install -y python3-pip
            else
                yum install -y python3-pip
            fi
        else
            apt-get install -y python3-pip
        fi
    fi
    
    # 升级pip
    python3 -m pip install --upgrade pip
    
    echo "✅ Python环境检查完成"
}

# 智能创建虚拟环境
create_virtual_environment() {
    echo ""
    echo "� 创建Python虚拟环境..."
    
    cd $PROJECT_DIR
    
    if [ ! -d "venv" ]; then
        # 尝试多种方法创建虚拟环境
        if python3 -m venv --help >/dev/null 2>&1; then
            python3 -m venv venv
            echo "✅ 使用内置venv创建虚拟环境成功"
        elif python3 -m virtualenv --help >/dev/null 2>&1; then
            python3 -m virtualenv venv
            echo "✅ 使用virtualenv创建虚拟环境成功"
        elif command -v virtualenv >/dev/null 2>&1; then
            virtualenv -p python3 venv
            echo "✅ 使用系统virtualenv创建虚拟环境成功"
        else
            # 最后尝试安装virtualenv
            echo "安装virtualenv..."
            python3 -m pip install virtualenv
            python3 -m virtualenv venv
            echo "✅ 安装virtualenv后创建虚拟环境成功"
        fi
    else
        echo "⚠️ 虚拟环境已存在，跳过创建"
    fi
}

# 安装系统依赖
install_system_dependencies

# 检查Python环境  
check_python_environment

# 第一步：系统初始化
echo ""
echo "🚀 开始智能部署..."

# 创建项目目录
echo ""
echo "📁 创建项目目录..."
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# 创建虚拟环境
create_virtual_environment

# 智能检测并安装Python依赖
install_python_dependencies() {
    echo ""
    echo "📦 安装Python依赖..."
    
    # 激活虚拟环境
    source $PROJECT_DIR/venv/bin/activate
    
    # 检查Python版本兼容性
    PYTHON_VERSION=$(python -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
    echo "检测到Python版本: $PYTHON_VERSION"
    
    # 根据Python版本选择合适的依赖文件
    if [ -f "$PROJECT_DIR/requirements_minimal_fixed.txt" ]; then
        echo "使用兼容性修复版依赖列表..."
        pip install -r requirements_minimal_fixed.txt
    elif [ -f "$PROJECT_DIR/requirements_compatible.txt" ]; then
        echo "使用兼容版依赖列表..."
        pip install -r requirements_compatible.txt
    elif [ -f "$PROJECT_DIR/requirements_lite.txt" ]; then
        echo "使用轻量版依赖列表..."
        # 先尝试安装，如果失败则使用备用方案
        if ! pip install -r requirements_lite.txt; then
            echo "⚠️ 轻量版依赖安装失败，使用核心依赖..."
            install_core_dependencies
        fi
    elif [ -f "$PROJECT_DIR/requirements.txt" ]; then
        echo "使用标准依赖列表..."
        
        # 先安装基础依赖
        pip install streamlit pandas numpy plotly
        
        # 检查网络连接，决定是否安装完整依赖
        if curl -Is --connect-timeout 5 pypi.org >/dev/null 2>&1; then
            echo "网络连接正常，尝试安装完整依赖..."
            # 过滤掉问题依赖，尝试安装
            if ! pip install -r requirements.txt; then
                echo "⚠️ 完整依赖安装失败，使用核心依赖..."
                install_core_dependencies
            fi
        else
            echo "网络连接受限，只安装核心依赖..."
            install_core_dependencies
        fi
    else
        echo "未找到依赖文件，安装核心依赖..."
        install_core_dependencies
    fi
    
    echo "✅ Python依赖安装完成"
    deactivate
}

# 安装核心依赖的备用函数
install_core_dependencies() {
    echo "安装核心依赖包..."
    
    # 创建临时的最小依赖文件
    cat > $PROJECT_DIR/requirements_core.txt << EOF
streamlit==1.28.0
pandas==1.5.3
numpy==1.24.3
plotly==5.17.0
requests==2.28.2
pytz==2023.3
tqdm==4.65.0
yfinance==0.2.18
openpyxl==3.1.2
EOF
    
    # 逐个安装，避免单个包失败影响整体
    while IFS= read -r package; do
        if [[ ! "$package" =~ ^#.* ]] && [[ -n "$package" ]]; then
            echo "安装: $package"
            pip install "$package" || echo "⚠️ $package 安装失败，跳过"
        fi
    done < $PROJECT_DIR/requirements_core.txt
    
    # 检查关键包是否安装成功
    python -c "import streamlit, pandas, numpy, plotly; print('✅ 核心包验证成功')" || {
        echo "❌ 核心包验证失败，尝试最基础安装"
        pip install streamlit pandas numpy plotly requests
    }
}

# 安装Python依赖
install_python_dependencies

# 检测容器运行时环境
detect_container_runtime() {
    echo ""
    echo "🐳 检测容器运行时..."
    
    if command -v docker >/dev/null 2>&1 && systemctl is-active docker >/dev/null 2>&1; then
        CONTAINER_RUNTIME="docker"
        echo "✅ 检测到Docker运行时"
    elif command -v podman >/dev/null 2>&1; then
        CONTAINER_RUNTIME="podman"
        echo "✅ 检测到Podman运行时"
        # 对于Podman，创建docker别名
        if ! command -v docker >/dev/null 2>&1; then
            echo "创建Podman到Docker的别名..."
            echo 'alias docker=podman' >> ~/.bashrc
            alias docker=podman
        fi
    else
        CONTAINER_RUNTIME="none"
        echo "⚠️ 未检测到容器运行时，将跳过Docker相关配置"
    fi
}

# 配置容器环境（如果可用）
setup_container_environment() {
    if [ "$CONTAINER_RUNTIME" = "none" ]; then
        echo "⚠️ 跳过容器环境配置（无可用运行时）"
        return
    fi
    
    echo ""
    echo "🐳 配置容器环境..."
    
    cd $PROJECT_DIR
    
    # 创建简化的Dockerfile（如果不存在）
    if [ ! -f "Dockerfile" ]; then
        cat > Dockerfile << EOF
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y 
    gcc 
    g++ 
    && rm -rf /var/lib/apt/lists/*

# 复制并安装Python依赖
COPY requirements*.txt ./
RUN pip install --no-cache-dir -r requirements*.txt || 
    pip install streamlit pandas numpy plotly requests pytz tqdm

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8501

# 启动应用
CMD ["streamlit", "run", "src/ui/streamlit_app.py", "--server.address=0.0.0.0"]
EOF
        echo "✅ 创建Dockerfile"
    fi
    
    # 创建简化的docker-compose.yml
    if [ ! -f "docker-compose.simple.yml" ]; then
        cat > docker-compose.simple.yml << EOF
version: '3.8'

services:
  stockapp:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - PYTHONPATH=/app
    restart: unless-stopped
EOF
        echo "✅ 创建docker-compose.simple.yml"
    fi
}

# 检测并配置容器环境
detect_container_runtime
setup_container_environment

# 设置文件权限
echo ""
echo "🔒 设置文件权限..."

# 检查www用户是否存在，如果不存在则创建
if ! id "www" &>/dev/null; then
    echo "创建www用户..."
    useradd -r -s /bin/false www
fi

# 设置目录权限
chown -R www:www $PROJECT_DIR 2>/dev/null || chown -R root:root $PROJECT_DIR
chmod +x $PROJECT_DIR/start_app.sh 2>/dev/null || echo "start_app.sh将稍后创建"

# 第五步：创建启动脚本
echo ""
echo "🔧 创建启动脚本..."
cat > start_app.sh << 'EOF'
#!/bin/bash
cd /www/wwwroot/gupiao
source venv/bin/activate
streamlit run src/ui/streamlit_app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
EOF
chmod +x start_app.sh

# 配置防火墙
configure_firewall() {
    echo ""
    echo "🔥 配置防火墙..."
    
    if [ "$DISTRO" = "redhat" ]; then
        # RedHat系列使用firewalld
        if systemctl is-active firewalld &>/dev/null; then
            firewall-cmd --permanent --add-port=8501/tcp
            firewall-cmd --reload
            echo "✅ firewalld端口8501已开放"
        elif systemctl is-available firewalld &>/dev/null; then
            systemctl start firewalld
            systemctl enable firewalld
            firewall-cmd --permanent --add-port=8501/tcp
            firewall-cmd --reload
            echo "✅ 启动firewalld并开放端口8501"
        else
            echo "⚠️ firewalld未安装，跳过防火墙配置"
        fi
    elif [ "$DISTRO" = "debian" ]; then
        # Debian系列使用ufw
        if command -v ufw >/dev/null 2>&1; then
            ufw allow 8501/tcp
            echo "✅ ufw端口8501已开放"
        else
            echo "⚠️ ufw未安装，跳过防火墙配置"
        fi
    else
        echo "⚠️ 未知系统，跳过防火墙配置"
    fi
}

# 配置防火墙
configure_firewall

# 智能配置进程管理
configure_process_management() {
    echo ""
    echo "🔄 配置进程管理..."
    
    # 检查是否已有进程管理工具
    if command -v supervisorctl >/dev/null 2>&1; then
        echo "✅ Supervisor已安装"
        PROCESS_MANAGER="supervisor"
    elif command -v systemctl >/dev/null 2>&1; then
        echo "使用systemd管理进程..."
        PROCESS_MANAGER="systemd"
    else
        echo "安装Supervisor..."
        # 在虚拟环境中安装supervisor
        source $PROJECT_DIR/venv/bin/activate
        pip install supervisor
        PROCESS_MANAGER="supervisor"
        deactivate
    fi
    
    if [ "$PROCESS_MANAGER" = "supervisor" ]; then
        setup_supervisor
    elif [ "$PROCESS_MANAGER" = "systemd" ]; then
        setup_systemd
    fi
}

# 配置Supervisor
setup_supervisor() {
    echo "配置Supervisor..."
    
    # 创建配置目录
    mkdir -p /etc/supervisor/conf.d/
    mkdir -p $PROJECT_DIR/logs
    
    # 确定运行用户
    if id "www" &>/dev/null; then
        RUN_USER="www"
    else
        RUN_USER="root"
    fi
    
    # 创建Supervisor配置
    cat > /etc/supervisor/conf.d/stockapp.conf << EOF
[program:stockapp]
command=$PROJECT_DIR/venv/bin/streamlit run src/ui/streamlit_app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
directory=$PROJECT_DIR
user=$RUN_USER
autostart=true
autorestart=true
stderr_logfile=$PROJECT_DIR/logs/stockapp.err.log
stdout_logfile=$PROJECT_DIR/logs/stockapp.out.log
environment=PYTHONPATH="$PROJECT_DIR"
EOF
    
    # 重载配置
    if command -v supervisorctl >/dev/null 2>&1; then
        supervisorctl reread 2>/dev/null || echo "⚠️ supervisorctl命令失败，请手动重载配置"
        supervisorctl update 2>/dev/null || echo "⚠️ supervisorctl update失败"
        supervisorctl start stockapp 2>/dev/null || echo "⚠️ supervisorctl start失败"
    fi
    
    echo "✅ Supervisor配置完成"
}

# 配置systemd服务
setup_systemd() {
    echo "配置systemd服务..."
    
    mkdir -p $PROJECT_DIR/logs
    
    # 确定运行用户
    if id "www" &>/dev/null; then
        RUN_USER="www"
    else
        RUN_USER="root"
    fi
    
    # 创建systemd服务文件
    cat > /etc/systemd/system/stockapp.service << EOF
[Unit]
Description=Stock Analysis Application
After=network.target

[Service]
Type=simple
User=$RUN_USER
WorkingDirectory=$PROJECT_DIR
Environment=PYTHONPATH=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/streamlit run src/ui/streamlit_app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
Restart=always
RestartSec=3
StandardOutput=file:$PROJECT_DIR/logs/stockapp.out.log
StandardError=file:$PROJECT_DIR/logs/stockapp.err.log

[Install]
WantedBy=multi-user.target
EOF
    
    # 启用并启动服务
    systemctl daemon-reload
    systemctl enable stockapp
    systemctl start stockapp
    
    echo "✅ systemd服务配置完成"
}

# 调用进程管理配置
configure_process_management

# 创建便捷启动脚本
echo ""
echo "📝 创建便捷启动脚本..."

# 创建直接启动脚本
cat > $PROJECT_DIR/start_direct.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
streamlit run src/ui/streamlit_app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
EOF
chmod +x $PROJECT_DIR/start_direct.sh

# 创建管理脚本
cat > $PROJECT_DIR/manage.sh << 'EOF'
#!/bin/bash

# 股票分析系统管理脚本
PROJECT_DIR="$(dirname "$0")"

case "$1" in
    start)
        echo "启动应用..."
        if command -v supervisorctl >/dev/null 2>&1; then
            supervisorctl start stockapp
        elif systemctl is-active stockapp >/dev/null 2>&1; then
            systemctl start stockapp
        else
            cd $PROJECT_DIR
            nohup ./start_direct.sh > logs/app.log 2>&1 &
            echo $! > stockapp.pid
        fi
        echo "✅ 应用启动完成"
        ;;
    stop)
        echo "停止应用..."
        if command -v supervisorctl >/dev/null 2>&1; then
            supervisorctl stop stockapp
        elif systemctl is-active stockapp >/dev/null 2>&1; then
            systemctl stop stockapp
        elif [ -f "$PROJECT_DIR/stockapp.pid" ]; then
            kill $(cat $PROJECT_DIR/stockapp.pid)
            rm -f $PROJECT_DIR/stockapp.pid
        fi
        echo "✅ 应用停止完成"
        ;;
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
    status)
        echo "检查应用状态..."
        if command -v supervisorctl >/dev/null 2>&1; then
            supervisorctl status stockapp
        elif systemctl is-active stockapp >/dev/null 2>&1; then
            systemctl status stockapp --no-pager
        elif [ -f "$PROJECT_DIR/stockapp.pid" ] && kill -0 $(cat $PROJECT_DIR/stockapp.pid) 2>/dev/null; then
            echo "应用正在运行 (PID: $(cat $PROJECT_DIR/stockapp.pid))"
        else
            echo "应用未运行"
        fi
        ;;
    logs)
        echo "查看应用日志..."
        if [ -f "$PROJECT_DIR/logs/stockapp.out.log" ]; then
            tail -f $PROJECT_DIR/logs/stockapp.out.log
        elif [ -f "$PROJECT_DIR/logs/app.log" ]; then
            tail -f $PROJECT_DIR/logs/app.log
        else
            echo "未找到日志文件"
        fi
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status|logs}"
        exit 1
        ;;
esac
EOF
chmod +x $PROJECT_DIR/manage.sh

echo "✅ 便捷脚本创建完成"

# 验证部署
echo ""
echo "🔍 部署验证..."
sleep 3

# 检查端口是否在监听
if command -v netstat >/dev/null 2>&1; then
    if netstat -tlnp | grep -q ":8501 "; then
        echo "✅ 应用端口8501正在监听"
    else
        echo "❌ 应用端口8501未启动，请检查日志"
    fi
elif command -v ss >/dev/null 2>&1; then
    if ss -tlnp | grep -q ":8501 "; then
        echo "✅ 应用端口8501正在监听"
    else
        echo "❌ 应用端口8501未启动，请检查日志"
    fi
else
    echo "⚠️ 无法检查端口状态，请手动验证"
fi

# 显示部署结果
echo ""
echo "🎉 智能部署完成!"
echo "================================"
echo "📝 部署信息："
echo "  - 操作系统: $OS_INFO"
echo "  - 项目目录: $PROJECT_DIR" 
echo "  - 容器运行时: $CONTAINER_RUNTIME"
echo "  - 访问地址: http://$(hostname -I | awk '{print $1}' 2>/dev/null || echo 'localhost'):8501"
echo ""
echo "🔧 管理命令："
echo "  - 启动应用: $PROJECT_DIR/manage.sh start"
echo "  - 停止应用: $PROJECT_DIR/manage.sh stop"
echo "  - 重启应用: $PROJECT_DIR/manage.sh restart"
echo "  - 查看状态: $PROJECT_DIR/manage.sh status"
echo "  - 查看日志: $PROJECT_DIR/manage.sh logs"
echo "  - 直接启动: $PROJECT_DIR/start_direct.sh"
echo ""
if [ "$CONTAINER_RUNTIME" != "none" ]; then
echo "🐳 容器部署："
echo "  - 构建镜像: $CONTAINER_RUNTIME build -t stockapp ."
echo "  - 启动容器: $CONTAINER_RUNTIME-compose -f docker-compose.simple.yml up -d"
echo ""
fi
echo "📋 下一步操作："
echo "  1. 如果使用防火墙，确保8501端口已开放"
echo "  2. 配置API密钥: vim $PROJECT_DIR/config/api_keys.py"
echo "  3. 访问 http://your-server-ip:8501 使用系统"
echo ""
echo "🎯 智能部署成功！支持多种Linux发行版的一键部署！"
