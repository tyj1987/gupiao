#!/bin/bash
# -*- coding: utf-8 -*-
# 股票分析系统管理脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# 日志函数
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 显示帮助
show_help() {
    cat << EOF
🚀 股票分析系统管理脚本

用法: $0 <命令> [选项]

命令:
    install         安装/部署系统
    start          启动服务
    stop           停止服务
    restart        重启服务
    status         查看状态
    logs           查看日志
    update         更新系统
    backup         备份数据
    restore        恢复数据
    cleanup        清理系统
    health         健康检查

选项:
    -h, --help     显示帮助
    -m, --mode     部署模式 (traditional|docker)
    -p, --port     服务端口
    -f, --force    强制执行

示例:
    $0 install              # 智能安装
    $0 install -m docker    # Docker模式安装
    $0 start                # 启动服务
    $0 logs                 # 查看日志
    $0 health               # 健康检查

EOF
}

# 检测部署模式
detect_deploy_mode() {
    if [[ -f "docker-compose.yml" ]] && command -v docker-compose &> /dev/null; then
        echo "docker"
    elif [[ -f "venv/bin/activate" ]] && [[ -f "start_traditional.sh" ]]; then
        echo "traditional"
    else
        echo "unknown"
    fi
}

# 安装系统
install_system() {
    log_info "开始安装股票分析系统..."
    
    # 检查部署脚本
    if [[ ! -f "scripts/deploy.sh" ]]; then
        log_error "部署脚本不存在"
        return 1
    fi
    
    # 执行部署脚本
    chmod +x scripts/deploy.sh
    bash scripts/deploy.sh "$@"
}

# 启动服务
start_service() {
    local mode=$(detect_deploy_mode)
    
    case $mode in
        docker)
            log_info "启动Docker服务..."
            docker-compose up -d
            ;;
        traditional)
            log_info "启动传统服务..."
            if systemctl is-active --quiet stock-analysis; then
                log_warning "服务已在运行"
            else
                systemctl start stock-analysis || ./start_traditional.sh &
            fi
            ;;
        *)
            log_error "未知部署模式，请先安装系统"
            return 1
            ;;
    esac
}

# 停止服务
stop_service() {
    local mode=$(detect_deploy_mode)
    
    case $mode in
        docker)
            log_info "停止Docker服务..."
            docker-compose down
            ;;
        traditional)
            log_info "停止传统服务..."
            systemctl stop stock-analysis 2>/dev/null || pkill -f streamlit || true
            ;;
        *)
            log_warning "未知部署模式"
            ;;
    esac
}

# 重启服务
restart_service() {
    log_info "重启服务..."
    stop_service
    sleep 2
    start_service
}

# 查看状态
show_status() {
    local mode=$(detect_deploy_mode)
    
    echo "=== 系统状态 ==="
    echo "部署模式: $mode"
    echo "项目目录: $PROJECT_DIR"
    echo
    
    case $mode in
        docker)
            echo "=== Docker服务状态 ==="
            docker-compose ps
            ;;
        traditional)
            echo "=== 系统服务状态 ==="
            systemctl status stock-analysis --no-pager -l || echo "系统服务未配置"
            echo
            echo "=== 进程状态 ==="
            pgrep -f streamlit >/dev/null && echo "Streamlit进程运行中" || echo "Streamlit进程未运行"
            ;;
        *)
            echo "未知部署模式"
            ;;
    esac
    
    echo
    echo "=== 端口监听 ==="
    netstat -tlnp 2>/dev/null | grep :8501 || echo "端口8501未监听"
}

# 查看日志
show_logs() {
    local mode=$(detect_deploy_mode)
    
    case $mode in
        docker)
            docker-compose logs -f --tail=100
            ;;
        traditional)
            if systemctl is-active --quiet stock-analysis; then
                journalctl -u stock-analysis -f --lines=100
            else
                log_warning "系统服务未运行，尝试查看应用日志..."
                if [[ -d "logs" ]]; then
                    tail -f logs/*.log
                else
                    log_error "未找到日志文件"
                fi
            fi
            ;;
        *)
            log_error "未知部署模式"
            ;;
    esac
}

# 更新系统
update_system() {
    log_info "更新股票分析系统..."
    
    # 备份当前配置
    if [[ -f "config/api_keys.py" ]]; then
        cp config/api_keys.py config/api_keys.py.backup
        log_info "已备份API配置"
    fi
    
    # 拉取最新代码
    if [[ -d ".git" ]]; then
        git pull origin main
        log_info "代码已更新"
    fi
    
    local mode=$(detect_deploy_mode)
    
    case $mode in
        docker)
            log_info "重建Docker镜像..."
            docker-compose down
            docker-compose build --no-cache
            docker-compose up -d
            ;;
        traditional)
            log_info "更新Python依赖..."
            source venv/bin/activate
            pip install -r requirements.txt --upgrade
            restart_service
            ;;
        *)
            log_error "未知部署模式"
            return 1
            ;;
    esac
    
    log_success "系统更新完成"
}

# 备份数据
backup_data() {
    local backup_dir="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    log_info "创建数据备份: $backup_dir"
    
    # 备份配置文件
    if [[ -f "config/api_keys.py" ]]; then
        cp config/api_keys.py "$backup_dir/"
    fi
    
    # 备份数据库文件
    if [[ -d "data" ]]; then
        cp -r data "$backup_dir/"
    fi
    
    # 备份日志
    if [[ -d "logs" ]]; then
        cp -r logs "$backup_dir/"
    fi
    
    # 备份自定义配置
    if [[ -f ".streamlit/config.toml" ]]; then
        mkdir -p "$backup_dir/.streamlit"
        cp .streamlit/config.toml "$backup_dir/.streamlit/"
    fi
    
    # 创建备份信息文件
    cat > "$backup_dir/backup_info.txt" << EOF
备份时间: $(date)
项目版本: $(git describe --tags --always 2>/dev/null || echo "unknown")
部署模式: $(detect_deploy_mode)
系统信息: $(uname -a)
EOF
    
    log_success "备份完成: $backup_dir"
}

# 恢复数据
restore_data() {
    local backup_dir="$1"
    
    if [[ -z "$backup_dir" ]]; then
        log_error "请指定备份目录"
        echo "可用备份:"
        ls -la backups/ 2>/dev/null || echo "无备份文件"
        return 1
    fi
    
    if [[ ! -d "$backup_dir" ]]; then
        log_error "备份目录不存在: $backup_dir"
        return 1
    fi
    
    log_warning "即将恢复数据，当前数据将被覆盖"
    read -p "继续？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        return 0
    fi
    
    log_info "恢复数据从: $backup_dir"
    
    # 停止服务
    stop_service
    
    # 恢复文件
    if [[ -f "$backup_dir/config/api_keys.py" ]]; then
        cp "$backup_dir/config/api_keys.py" config/
    fi
    
    if [[ -d "$backup_dir/data" ]]; then
        rm -rf data
        cp -r "$backup_dir/data" .
    fi
    
    if [[ -d "$backup_dir/logs" ]]; then
        rm -rf logs
        cp -r "$backup_dir/logs" .
    fi
    
    if [[ -f "$backup_dir/.streamlit/config.toml" ]]; then
        cp "$backup_dir/.streamlit/config.toml" .streamlit/
    fi
    
    # 启动服务
    start_service
    
    log_success "数据恢复完成"
}

# 清理系统
cleanup_system() {
    log_info "清理系统文件..."
    
    # 运行清理脚本
    if [[ -f "scripts/cleanup.sh" ]]; then
        bash scripts/cleanup.sh
    fi
    
    # 清理Docker资源
    if command -v docker &> /dev/null; then
        log_info "清理Docker资源..."
        docker system prune -f
    fi
    
    # 清理旧备份
    if [[ -d "backups" ]]; then
        find backups -type d -mtime +30 -exec rm -rf {} + 2>/dev/null || true
        log_info "清理30天前的备份"
    fi
    
    log_success "系统清理完成"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    local errors=0
    
    # 检查服务状态
    if ! curl -s http://localhost:8501/healthz >/dev/null; then
        log_error "服务健康检查失败"
        ((errors++))
    else
        log_success "服务健康检查通过"
    fi
    
    # 检查磁盘空间
    local disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [[ $disk_usage -gt 90 ]]; then
        log_warning "磁盘使用率过高: ${disk_usage}%"
        ((errors++))
    else
        log_info "磁盘使用率: ${disk_usage}%"
    fi
    
    # 检查内存使用
    local mem_usage=$(free | awk 'NR==2{printf "%.1f", $3*100/($3+$4)}')
    log_info "内存使用率: ${mem_usage}%"
    
    # 检查配置文件
    if [[ ! -f "config/api_keys.py" ]]; then
        log_warning "API配置文件缺失"
        ((errors++))
    else
        log_success "配置文件检查通过"
    fi
    
    if [[ $errors -eq 0 ]]; then
        log_success "健康检查通过"
        return 0
    else
        log_error "发现 $errors 个问题"
        return 1
    fi
}

# 主函数
main() {
    case "${1:-}" in
        install)
            shift
            install_system "$@"
            ;;
        start)
            start_service
            ;;
        stop)
            stop_service
            ;;
        restart)
            restart_service
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        update)
            update_system
            ;;
        backup)
            backup_data
            ;;
        restore)
            restore_data "$2"
            ;;
        cleanup)
            cleanup_system
            ;;
        health)
            health_check
            ;;
        -h|--help|help)
            show_help
            ;;
        *)
            log_error "未知命令: ${1:-}"
            echo
            show_help
            exit 1
            ;;
    esac
}

# 脚本入口
main "$@"
