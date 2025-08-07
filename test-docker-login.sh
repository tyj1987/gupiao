#!/bin/bash

# Docker Hub 令牌测试脚本

echo "🔐 测试Docker Hub连接..."

# 提示用户输入Docker Hub令牌进行测试
echo "请输入您的Docker Hub访问令牌进行测试:"
read -s DOCKER_TOKEN

# 测试登录
echo "正在测试Docker Hub登录..."
echo "$DOCKER_TOKEN" | docker login --username tuoyongjun1987 --password-stdin

if [ $? -eq 0 ]; then
    echo "✅ Docker Hub登录成功！"
    echo "📋 当前用户信息:"
    docker info | grep Username || echo "无法获取用户信息"
    
    # 退出登录
    docker logout
    echo "🔓 已退出登录"
else
    echo "❌ Docker Hub登录失败！"
    echo "请检查:"
    echo "1. 令牌是否正确"
    echo "2. 令牌是否有推送权限"
    echo "3. 用户名是否正确 (tuoyongjun1987)"
fi
