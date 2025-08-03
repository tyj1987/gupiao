#!/bin/bash
# 系统管理脚本 - 用于日常维护和管理

PROJECT_DIR="/www/wwwroot/gupiao"

function show_help() {
    echo "🔧 股票分析系统管理工具"
    echo "========================="
    echo "使用方法: ./manage.sh [命令]"
    echo ""
    echo "可用命令："
    echo "  start     - 启动应用"
    echo "  stop      - 停止应用"
    echo "  restart   - 重启应用"
    echo "  status    - 查看状态"
    echo "  logs      - 查看日志"
    echo "  update    - 更新股票数据"
    echo "  backup    - 备份数据"
    echo "  health    - 健康检查"
    echo "  help      - 显示帮助"
    echo ""
}

function start_app() {
    echo "🚀 启动股票分析系统..."
    supervisorctl start gupiao
    echo "✅ 启动完成"
}

function stop_app() {
    echo "🛑 停止股票分析系统..."
    supervisorctl stop gupiao
    echo "✅ 停止完成"
}

function restart_app() {
    echo "🔄 重启股票分析系统..."
    supervisorctl restart gupiao
    echo "✅ 重启完成"
}

function show_status() {
    echo "📊 系统状态检查..."
    echo "==================="
    
    # 应用状态
    echo "🔧 应用进程状态:"
    supervisorctl status gupiao
    echo ""
    
    # 端口状态
    echo "🌐 端口监听状态:"
    netstat -tlnp | grep ":8501 " || echo "❌ 端口8501未监听"
    echo ""
    
    # 系统资源
    echo "💻 系统资源使用:"
    echo "内存使用: $(free -h | grep Mem | awk '{print $3"/"$2}')"
    echo "磁盘使用: $(df -h $PROJECT_DIR | tail -1 | awk '{print $3"/"$2" ("$5")"}')"
    echo ""
    
    # 最近日志
    echo "📝 最近日志 (最后10行):"
    tail -10 /var/log/gupiao.log
}

function show_logs() {
    echo "📖 实时日志监控 (按Ctrl+C退出)..."
    tail -f /var/log/gupiao.log
}

function update_data() {
    echo "📊 更新股票数据..."
    cd $PROJECT_DIR
    source venv/bin/activate
    
    python -c "
from src.data.universal_stock_fetcher import UniversalStockFetcher
import os
print('🔄 开始更新股票数据...')
try:
    fetcher = UniversalStockFetcher()
    fetcher.refresh_all_data()
    print('✅ 股票数据更新完成')
    
    # 获取统计信息
    stats = fetcher.get_market_statistics()
    print(f'📈 更新统计:')
    print(f'   总计: {stats[\"total\"]} 只股票')
    print(f'   A股: {stats[\"a_stocks\"]} 只')
    print(f'   港股: {stats[\"hk_stocks\"]} 只')
    print(f'   美股: {stats[\"us_stocks\"]} 只')
except Exception as e:
    print(f'❌ 数据更新失败: {e}')
"
    
    echo "🔄 重启应用以加载新数据..."
    restart_app
}

function backup_data() {
    echo "💾 备份系统数据..."
    
    # 创建备份目录
    BACKUP_DIR="/var/backup/gupiao"
    mkdir -p $BACKUP_DIR
    
    # 备份文件名（包含时间戳）
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/gupiao_backup_$TIMESTAMP.tar.gz"
    
    # 创建备份
    cd /www/wwwroot
    tar -czf $BACKUP_FILE \
        --exclude='gupiao/venv' \
        --exclude='gupiao/.git' \
        --exclude='gupiao/__pycache__' \
        --exclude='gupiao/src/__pycache__' \
        --exclude='gupiao/src/*/__pycache__' \
        gupiao/
    
    echo "✅ 备份完成: $BACKUP_FILE"
    echo "📊 备份大小: $(du -h $BACKUP_FILE | cut -f1)"
    
    # 清理旧备份（保留最近7个）
    cd $BACKUP_DIR
    ls -t gupiao_backup_*.tar.gz | tail -n +8 | xargs -r rm
    echo "🧹 旧备份清理完成"
}

function health_check() {
    echo "🏥 系统健康检查..."
    echo "==================="
    
    # 检查项目目录
    if [ -d "$PROJECT_DIR" ]; then
        echo "✅ 项目目录存在"
    else
        echo "❌ 项目目录不存在"
        return 1
    fi
    
    # 检查虚拟环境
    if [ -d "$PROJECT_DIR/venv" ]; then
        echo "✅ Python虚拟环境存在"
    else
        echo "❌ Python虚拟环境不存在"
    fi
    
    # 检查配置文件
    if [ -f "$PROJECT_DIR/config/api_keys.py" ]; then
        echo "✅ API配置文件存在"
    else
        echo "⚠️ API配置文件不存在，请配置"
    fi
    
    # 检查进程状态
    if supervisorctl status gupiao | grep -q "RUNNING"; then
        echo "✅ 应用进程正常运行"
    else
        echo "❌ 应用进程未运行"
    fi
    
    # 检查端口监听
    if netstat -tlnp | grep -q ":8501 "; then
        echo "✅ 端口8501正常监听"
    else
        echo "❌ 端口8501未监听"
    fi
    
    # 检查磁盘空间
    DISK_USAGE=$(df $PROJECT_DIR | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ $DISK_USAGE -lt 80 ]; then
        echo "✅ 磁盘空间充足 ($DISK_USAGE%)"
    else
        echo "⚠️ 磁盘空间不足 ($DISK_USAGE%)"
    fi
    
    # 检查内存使用
    MEM_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
    if [ $MEM_USAGE -lt 80 ]; then
        echo "✅ 内存使用正常 ($MEM_USAGE%)"
    else
        echo "⚠️ 内存使用偏高 ($MEM_USAGE%)"
    fi
    
    echo ""
    echo "🎯 健康检查完成"
}

# 主程序
case "$1" in
    start)
        start_app
        ;;
    stop)
        stop_app
        ;;
    restart)
        restart_app
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    update)
        update_data
        ;;
    backup)
        backup_data
        ;;
    health)
        health_check
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
