#!/bin/bash
# CentOS 7.9 + 宝塔环境自动部署脚本
# 使用方法: chmod +x deploy.sh && ./deploy.sh

set -e  # 遇到错误立即退出

echo "🚀 开始部署股票分析系统..."
echo "================================"

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用root用户运行此脚本"
    exit 1
fi

# 配置变量
PROJECT_DIR="/www/wwwroot/gupiao"
PYTHON_CMD="python3"
PIP_CMD="pip3"

echo "📋 系统信息检查..."
echo "操作系统: $(cat /etc/redhat-release)"
echo "Python版本: $(python3 --version)"
echo "当前用户: $(whoami)"
echo "项目目录: $PROJECT_DIR"

# 第一步：创建项目目录
echo ""
echo "📁 创建项目目录..."
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# 第二步：创建虚拟环境
echo ""
echo "🐍 创建Python虚拟环境..."
if [ ! -d "venv" ]; then
    $PYTHON_CMD -m virtualenv venv
    echo "✅ 虚拟环境创建成功"
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
    echo "⚠️ requirements.txt不存在，请确保项目文件已上传"
fi

# 第四步：设置权限
echo ""
echo "🔒 设置文件权限..."
chown -R www:www $PROJECT_DIR
chmod +x $PROJECT_DIR/start_app.sh 2>/dev/null || echo "start_app.sh未找到，稍后需要手动创建"

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

# 第六步：配置防火墙
echo ""
echo "🔥 配置防火墙..."
firewall-cmd --permanent --add-port=8501/tcp
firewall-cmd --reload
echo "✅ 防火墙端口8501已开放"

# 第七步：安装和配置Supervisor
echo ""
echo "🔄 配置进程管理..."
if ! command -v supervisorctl &> /dev/null; then
    pip3 install supervisor
    echo "✅ Supervisor安装完成"
fi

# 创建Supervisor配置目录
mkdir -p /etc/supervisor/conf.d

# 创建应用配置文件
cat > /etc/supervisor/conf.d/gupiao.conf << EOF
[program:gupiao]
command=$PROJECT_DIR/venv/bin/streamlit run src/ui/streamlit_app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
directory=$PROJECT_DIR
user=www
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/gupiao.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=3
environment=PATH="$PROJECT_DIR/venv/bin"
EOF

echo "✅ Supervisor配置完成"

# 第八步：启动服务
echo ""
echo "🚀 启动应用服务..."
if command -v supervisorctl &> /dev/null; then
    supervisorctl reread
    supervisorctl update
    supervisorctl start gupiao
    echo "✅ 应用服务启动成功"
    
    # 检查服务状态
    echo ""
    echo "📊 服务状态检查..."
    supervisorctl status gupiao
else
    echo "⚠️ Supervisor未正确安装，请手动启动应用"
fi

# 第九步：验证部署
echo ""
echo "🔍 部署验证..."
sleep 5

# 检查端口是否在监听
if netstat -tlnp | grep -q ":8501 "; then
    echo "✅ 应用端口8501正在监听"
else
    echo "❌ 应用端口8501未启动，请检查日志"
fi

# 第十步：显示部署结果
echo ""
echo "🎉 部署完成!"
echo "================================"
echo "📝 部署信息："
echo "  - 项目目录: $PROJECT_DIR"
echo "  - 访问地址: http://$(hostname -I | awk '{print $1}'):8501"
echo "  - 日志文件: /var/log/gupiao.log"
echo "  - 配置文件: /etc/supervisor/conf.d/gupiao.conf"
echo ""
echo "🔧 管理命令："
echo "  - 查看状态: supervisorctl status gupiao"
echo "  - 重启服务: supervisorctl restart gupiao"
echo "  - 查看日志: tail -f /var/log/gupiao.log"
echo "  - 停止服务: supervisorctl stop gupiao"
echo ""
echo "📋 下一步操作："
echo "  1. 在宝塔面板中开放8501端口"
echo "  2. 配置API密钥: vim $PROJECT_DIR/config/api_keys.py"
echo "  3. 访问 http://your-server-ip:8501 测试系统"
echo ""
echo "🎯 部署成功！享受5,728只股票的强大分析能力！"
