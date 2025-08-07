#!/bin/bash
# 快速修复部署问题脚本
# 针对AlmaLinux 9.6 + Python 3.13.5环境

set -e  # 遇到错误立即退出

echo "🛠️ 快速修复部署问题..."
echo "================================"

# 检查当前环境
echo "📋 当前环境信息："
echo "操作系统: $(cat /etc/redhat-release 2>/dev/null || cat /etc/os-release | grep PRETTY_NAME)"
echo "Python版本: $(python3 --version)"
echo "Python路径: $(which python3)"
echo "当前目录: $(pwd)"

# 解决virtualenv问题的几种方法
echo ""
echo "🔧 解决virtualenv问题..."

# 方法1：安装python3-venv包
echo "方法1: 安装系统venv模块..."
if command -v dnf >/dev/null 2>&1; then
    dnf install -y python3-venv 2>/dev/null || echo "venv可能已安装或需要不同的包名"
elif command -v yum >/dev/null 2>&1; then
    yum install -y python3-venv 2>/dev/null || echo "venv可能已安装或需要不同的包名"
fi

# 方法2：安装virtualenv模块
echo "方法2: 安装virtualenv模块..."
pip3 install virtualenv --break-system-packages 2>/dev/null || pip3 install virtualenv || echo "virtualenv安装可能失败"

# 方法3：检查可用的虚拟环境创建方法
echo ""
echo "🧪 测试虚拟环境创建方法..."

# 测试venv
echo "测试内置venv模块..."
if python3 -m venv --help >/dev/null 2>&1; then
    echo "✅ python3 -m venv 可用"
    VENV_CMD="python3 -m venv"
else
    echo "❌ python3 -m venv 不可用"
fi

# 测试virtualenv
echo "测试virtualenv模块..."
if python3 -m virtualenv --help >/dev/null 2>&1; then
    echo "✅ python3 -m virtualenv 可用"
    VENV_CMD="python3 -m virtualenv"
elif command -v virtualenv >/dev/null 2>&1; then
    echo "✅ virtualenv 命令可用"
    VENV_CMD="virtualenv"
else
    echo "❌ virtualenv 不可用"
fi

# 如果找到可用的方法，创建虚拟环境
if [ -n "$VENV_CMD" ]; then
    echo ""
    echo "🐍 使用 $VENV_CMD 创建虚拟环境..."
    cd /www/wwwroot/gupiao
    
    if [ ! -d "venv" ]; then
        $VENV_CMD venv
        echo "✅ 虚拟环境创建成功"
    else
        echo "⚠️ 虚拟环境已存在"
    fi
    
    # 激活虚拟环境并测试
    source venv/bin/activate
    echo "✅ 虚拟环境激活成功"
    echo "Python路径: $(which python)"
    echo "Pip路径: $(which pip)"
    
else
    echo "❌ 无法找到可用的虚拟环境创建方法"
    echo "请手动安装："
    echo "  方法1: dnf install python3-venv"
    echo "  方法2: pip3 install virtualenv --break-system-packages"
    exit 1
fi

echo ""
echo "🎉 虚拟环境问题已解决！"
echo "现在可以继续运行 ./deploy.sh"
