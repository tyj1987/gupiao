#!/bin/bash
# 轻量级部署脚本 - 快速启动版本

set -e

echo "🚀 开始轻量级部署股票分析系统..."
echo "================================"

# 配置变量
PROJECT_DIR="$HOME/gupiao_deploy"
PYTHON_CMD="python3"

echo "📋 环境检查..."
echo "Python版本: $(python3 --version)"
echo "项目目录: $PROJECT_DIR"

# 创建项目目录并复制代码
echo ""
echo "📁 准备项目文件..."
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# 复制核心源代码
cp -r /home/tyj/gupiao/src $PROJECT_DIR/ 2>/dev/null || echo "源代码已存在"
cp /home/tyj/gupiao/requirements_lite.txt $PROJECT_DIR/requirements.txt 2>/dev/null || echo "依赖文件已存在"

# 创建虚拟环境
echo ""
echo "🐍 创建虚拟环境..."
if [ ! -d "venv" ]; then
    $PYTHON_CMD -m venv venv
    echo "✅ 虚拟环境创建成功"
fi

# 激活虚拟环境
source venv/bin/activate

# 升级pip
echo ""
echo "⬆️ 升级pip..."
pip install --upgrade pip

# 安装依赖
echo ""
echo "📦 安装依赖包..."
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 创建启动脚本
echo ""
echo "🔧 创建启动脚本..."
cat > start.sh << 'EOF'
#!/bin/bash
cd ~/gupiao_deploy
source venv/bin/activate
streamlit run src/ui/streamlit_app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true --browser.gatherUsageStats false
EOF
chmod +x start.sh

# 创建配置目录
mkdir -p data/cache
mkdir -p logs

# 启动应用
echo ""
echo "🚀 启动应用..."
nohup ./start.sh > logs/app.log 2>&1 &
echo "应用正在后台启动，进程ID: $!"

# 等待启动
echo ""
echo "⏳ 等待应用启动..."
sleep 5

# 检查状态
if ps aux | grep -v grep | grep -q streamlit; then
    echo "✅ 应用启动成功!"
else
    echo "⚠️ 应用可能启动失败，请检查日志"
fi

# 检查端口
if command -v ss >/dev/null && ss -tlnp 2>/dev/null | grep -q ":8501"; then
    echo "✅ 端口8501正在监听"
elif command -v netstat >/dev/null && netstat -tlnp 2>/dev/null | grep -q ":8501"; then
    echo "✅ 端口8501正在监听"
else
    echo "⚠️ 端口8501可能未启动，请稍后重试"
fi

echo ""
echo "🎉 部署完成!"
echo "================================"
echo "📝 访问信息："
echo "  - 本地访问: http://localhost:8501"
echo "  - 局域网访问: http://$(hostname -I | awk '{print $1}'):8501"
echo ""
echo "🔧 管理命令："
echo "  - 启动应用: cd $PROJECT_DIR && ./start.sh"
echo "  - 查看进程: ps aux | grep streamlit"
echo "  - 查看日志: tail -f $PROJECT_DIR/logs/app.log"
echo "  - 停止应用: pkill -f streamlit"
echo ""
echo "🎯 轻量级部署成功！现在可以访问股票分析系统了！"
