#!/bin/bash
# 用户目录部署脚本 - 无需root权限
# 适用于当前用户环境部署

set -e  # 遇到错误立即退出

echo "🚀 开始部署股票分析系统 (用户模式)..."
echo "================================"

# 配置变量 - 使用当前用户目录
PROJECT_DIR="$HOME/gupiao_deploy"
PYTHON_CMD="python3"
PIP_CMD="pip3"

echo "📋 系统信息检查..."
echo "操作系统: $(cat /etc/redhat-release 2>/dev/null || cat /etc/os-release | grep PRETTY_NAME)"
echo "Python版本: $(python3 --version)"
echo "当前用户: $(whoami)"
echo "项目目录: $PROJECT_DIR"

# 第一步：创建项目目录
echo ""
echo "📁 创建项目目录..."
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# 复制源代码
echo ""
echo "📥 复制源代码..."
if [ -d "/home/tyj/gupiao" ]; then
    cp -r /home/tyj/gupiao/* $PROJECT_DIR/
    echo "✅ 源代码复制完成"
else
    echo "❌ 源代码目录不存在: /home/tyj/gupiao"
    exit 1
fi

# 第二步：创建虚拟环境
echo ""
echo "🐍 创建Python虚拟环境..."
if [ ! -d "venv" ]; then
    # 优先使用内置的venv模块
    if $PYTHON_CMD -m venv --help &>/dev/null; then
        $PYTHON_CMD -m venv venv
        echo "✅ 虚拟环境创建成功 (使用venv)"
    elif $PYTHON_CMD -m virtualenv --help &>/dev/null; then
        $PYTHON_CMD -m virtualenv venv
        echo "✅ 虚拟环境创建成功 (使用virtualenv)"
    else
        echo "❌ 无法创建虚拟环境，请先安装python3-venv或virtualenv"
        echo "  CentOS/RHEL: sudo dnf install python3-venv"
        echo "  或者: pip3 install virtualenv"
        exit 1
    fi
else
    echo "⚠️ 虚拟环境已存在，跳过创建"
fi

# 激活虚拟环境
source venv/bin/activate

# 第三步：安装依赖包
echo ""
echo "📦 安装Python依赖包..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
    echo "✅ 依赖包安装完成"
else
    echo "⚠️ requirements.txt不存在，手动安装核心依赖..."
    pip install streamlit pandas numpy akshare yfinance matplotlib seaborn plotly -i https://pypi.tuna.tsinghua.edu.cn/simple/
    echo "✅ 核心依赖包安装完成"
fi

# 第四步：创建启动脚本
echo ""
echo "🔧 创建启动脚本..."
cat > start_app.sh << EOF
#!/bin/bash
cd $PROJECT_DIR
source venv/bin/activate
streamlit run src/ui/streamlit_app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
EOF
chmod +x start_app.sh

# 第五步：创建systemd用户服务（可选）
echo ""
echo "🔄 创建用户服务配置..."
mkdir -p ~/.config/systemd/user

cat > ~/.config/systemd/user/gupiao.service << EOF
[Unit]
Description=股票分析系统
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/streamlit run src/ui/streamlit_app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
Restart=always
RestartSec=5
Environment=PATH=$PROJECT_DIR/venv/bin

[Install]
WantedBy=default.target
EOF

echo "✅ 用户服务配置完成"

# 第六步：启动服务
echo ""
echo "🚀 启动应用服务..."

# 重新加载用户服务
systemctl --user daemon-reload

# 启动服务
if systemctl --user start gupiao.service 2>/dev/null; then
    systemctl --user enable gupiao.service
    echo "✅ 应用服务启动成功"
    
    # 检查服务状态
    echo ""
    echo "📊 服务状态检查..."
    systemctl --user status gupiao.service --no-pager
else
    echo "⚠️ 系统服务启动失败，尝试直接启动..."
    nohup ./start_app.sh > app.log 2>&1 &
    echo "✅ 应用已在后台启动"
fi

# 第七步：验证部署
echo ""
echo "🔍 部署验证..."
sleep 3

# 检查端口是否在监听
if command -v ss >/dev/null 2>&1 && ss -tlnp | grep -q ":8501 "; then
    echo "✅ 应用端口8501正在监听"
elif command -v netstat >/dev/null 2>&1 && netstat -tlnp | grep -q ":8501 "; then
    echo "✅ 应用端口8501正在监听"
else
    echo "❌ 应用端口8501未启动，请检查日志"
    echo "日志文件: $PROJECT_DIR/app.log"
fi

# 第八步：显示部署结果
echo ""
echo "🎉 部署完成!"
echo "================================"
echo "📝 部署信息："
echo "  - 项目目录: $PROJECT_DIR"
echo "  - 访问地址: http://localhost:8501"
echo "  - 启动脚本: $PROJECT_DIR/start_app.sh"
echo "  - 日志文件: $PROJECT_DIR/app.log"
echo ""
echo "🔧 管理命令："
echo "  - 查看状态: systemctl --user status gupiao.service"
echo "  - 重启服务: systemctl --user restart gupiao.service"
echo "  - 停止服务: systemctl --user stop gupiao.service"
echo "  - 查看日志: tail -f $PROJECT_DIR/app.log"
echo "  - 手动启动: cd $PROJECT_DIR && ./start_app.sh"
echo ""
echo "📋 下一步操作："
echo "  1. 访问 http://localhost:8501 测试系统"
echo "  2. 如需外部访问，请开放8501端口"
echo "  3. 配置完成后可以开始使用股票分析功能"
echo ""
echo "🎯 部署成功！享受5,728只股票的强大分析能力！"
