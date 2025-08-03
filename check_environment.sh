#!/bin/bash
# 系统环境检查脚本

echo "🔍 CentOS 7.9 环境检查"
echo "====================="

# 基本系统信息
echo "📋 系统信息："
echo "  操作系统: $(cat /etc/redhat-release)"
echo "  内核版本: $(uname -r)"
echo "  架构: $(uname -m)"
echo "  主机名: $(hostname)"
echo "  当前用户: $(whoami)"
echo ""

# Python环境检查
echo "🐍 Python环境："
if command -v python3 &> /dev/null; then
    echo "  ✅ Python3: $(python3 --version)"
else
    echo "  ❌ Python3 未安装"
fi

if command -v pip3 &> /dev/null; then
    echo "  ✅ Pip3: $(pip3 --version | awk '{print $1, $2}')"
else
    echo "  ❌ Pip3 未安装"
fi
echo ""

# 宝塔面板检查
echo "🎛️ 宝塔面板："
if [ -f "/etc/init.d/bt" ]; then
    BT_STATUS=$(/etc/init.d/bt status)
    echo "  ✅ 宝塔面板已安装"
    echo "  状态: $BT_STATUS"
    
    # 获取宝塔面板访问信息
    if command -v bt &> /dev/null; then
        echo "  面板地址: $(bt default | grep '面板地址' | awk '{print $2}' || echo '请运行 bt default 查看')"
    fi
else
    echo "  ❌ 宝塔面板未安装"
fi
echo ""

# 网络和防火墙
echo "🌐 网络和防火墙："
echo "  IP地址: $(hostname -I | awk '{print $1}')"

if systemctl is-active --quiet firewalld; then
    echo "  ✅ Firewalld 服务运行中"
    echo "  开放端口: $(firewall-cmd --list-ports)"
else
    echo "  ❌ Firewalld 服务未运行"
fi
echo ""

# 系统资源
echo "💻 系统资源："
echo "  CPU: $(nproc) 核心"
echo "  内存: $(free -h | grep Mem | awk '{print $2}') (可用: $(free -h | grep Mem | awk '{print $7}'))"
echo "  磁盘: $(df -h / | tail -1 | awk '{print $2}') (可用: $(df -h / | tail -1 | awk '{print $4}'))"
echo ""

# 必要的软件包检查
echo "📦 必要软件包："
packages=("wget" "curl" "git" "vim" "gcc" "gcc-c++" "make")
for pkg in "${packages[@]}"; do
    if rpm -q $pkg &> /dev/null; then
        echo "  ✅ $pkg"
    else
        echo "  ❌ $pkg (未安装)"
    fi
done
echo ""

# SELinux 状态
echo "🔒 安全配置："
echo "  SELinux: $(getenforce)"
echo ""

# 时区和时间
echo "⏰ 时间配置："
echo "  时区: $(timedatectl | grep 'Time zone' | awk '{print $3}')"
echo "  当前时间: $(date)"
echo ""

# 检查是否有其他服务占用8501端口
echo "🔌 端口占用检查："
if netstat -tlnp | grep -q ":8501 "; then
    echo "  ⚠️ 端口8501已被占用："
    netstat -tlnp | grep ":8501 "
else
    echo "  ✅ 端口8501可用"
fi
echo ""

# 建议和下一步
echo "💡 部署建议："
echo "=================="

# 检查系统是否满足最低要求
memory_gb=$(free -g | grep Mem | awk '{print $2}')
if [ $memory_gb -lt 2 ]; then
    echo "  ⚠️ 建议内存至少2GB，当前: ${memory_gb}GB"
fi

disk_gb=$(df -BG / | tail -1 | awk '{print $4}' | sed 's/G//')
if [ $disk_gb -lt 10 ]; then
    echo "  ⚠️ 建议可用磁盘空间至少10GB，当前: ${disk_gb}GB"
fi

echo ""
echo "🚀 准备部署："
echo "  1. 确保宝塔面板正常运行"
echo "  2. 上传项目文件到 /www/wwwroot/gupiao"
echo "  3. 运行部署脚本: chmod +x deploy.sh && ./deploy.sh"
echo "  4. 在宝塔面板中开放8501端口"
echo "  5. 配置API密钥并测试系统"
echo ""

echo "✅ 环境检查完成！"
