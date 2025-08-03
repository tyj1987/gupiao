#!/bin/bash
# Docker快速部署脚本

echo "🐳 股票分析系统 Docker 快速部署"
echo "================================"

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装Docker"
    echo "💡 运行以下命令安装: ./docker-manage.sh install"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装Docker Compose"
    exit 1
fi

echo "✅ Docker环境检查通过"

# 检查配置文件
if [ ! -f "config/api_keys.py" ]; then
    echo "⚠️ 配置文件不存在，正在创建..."
    cp config/api_keys.example.py config/api_keys.py
    echo "📝 请编辑 config/api_keys.py 设置您的API密钥"
    echo "💡 主要需要设置: TUSHARE_TOKEN"
    read -p "按回车键继续，或Ctrl+C退出先配置API密钥..."
fi

echo "🔨 构建Docker镜像..."
docker-compose -f docker-compose.simple.yml build

echo "🚀 启动服务..."
docker-compose -f docker-compose.simple.yml up -d

echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "📊 检查服务状态..."
docker-compose -f docker-compose.simple.yml ps

echo ""
echo "🎉 部署完成！"
echo "========================="
echo "🌐 访问地址: http://localhost:8501"
echo "📊 系统特性:"
echo "  - 5,728只股票全市场覆盖"
echo "  - 智能搜索和风险评估"
echo "  - 实时数据分析"
echo ""
echo "🔧 管理命令:"
echo "  查看状态: docker-compose -f docker-compose.simple.yml ps"
echo "  查看日志: docker-compose -f docker-compose.simple.yml logs -f"
echo "  停止服务: docker-compose -f docker-compose.simple.yml down"
echo "  重启服务: docker-compose -f docker-compose.simple.yml restart"
echo ""
echo "📝 如需修改配置，请编辑 config/api_keys.py 后重启服务"
