#!/bin/bash

# 通过生产服务器中转部署到测试服务器的脚本
# 当测试服务器无法直接访问Docker Hub时使用

set -e

echo "🚀 开始通过生产服务器中转部署到测试服务器..."

# 配置信息
PROD_SERVER="47.94.225.76"
TEST_SERVER="ddns.52trz.com"
IMAGE_NAME="tuoyongjun1987/gupiao-stock-analysis:latest"
TARBALL_NAME="gupiao-app.tar"

echo "📦 步骤1: 在生产服务器上导出Docker镜像..."
ssh root@$PROD_SERVER << 'EOF'
# 拉取最新镜像
docker pull tuoyongjun1987/gupiao-stock-analysis:latest
# 导出镜像为tar文件
docker save -o /tmp/gupiao-app.tar tuoyongjun1987/gupiao-stock-analysis:latest
echo "✅ 镜像导出完成"
EOF

echo "📋 步骤2: 从生产服务器下载镜像文件..."
scp root@$PROD_SERVER:/tmp/gupiao-app.tar /tmp/

echo "📤 步骤3: 上传镜像文件到测试服务器..."
scp /tmp/gupiao-app.tar root@$TEST_SERVER:/tmp/

echo "🔄 步骤4: 在测试服务器上导入并部署..."
ssh root@$TEST_SERVER << 'EOF'
# 导入镜像
docker load -i /tmp/gupiao-app.tar
echo "✅ 镜像导入完成"

# 停止现有容器
docker stop gupiao-app || true
docker rm gupiao-app || true

# 启动新容器
docker run -d \
  --name gupiao-app \
  --restart unless-stopped \
  -p 8501:8501 \
  -e ENVIRONMENT=test \
  tuoyongjun1987/gupiao-stock-analysis:latest

echo "⏳ 等待应用启动..."
sleep 30

# 健康检查
if curl -f http://localhost:8501/_stcore/health; then
  echo "✅ 测试服务器部署成功"
  echo "🌐 访问地址: http://ddns.52trz.com:8501"
else
  echo "❌ 测试服务器部署失败"
  exit 1
fi

# 清理临时文件
rm -f /tmp/gupiao-app.tar
EOF

# 清理本地临时文件
rm -f /tmp/gupiao-app.tar

echo "🎉 测试服务器部署完成！"
echo "📱 测试服务器: http://ddns.52trz.com:8501"
echo "🌐 生产服务器: http://47.94.225.76:8501"
