#!/bin/bash

echo "=== Docker镜像拉取性能测试 ==="
echo "时间: $(date)"
echo "服务器: $(hostname)"
echo

# 清理已有镜像进行干净测试
echo "1. 清理测试镜像..."
docker rmi hello-world:latest 2>/dev/null || true

echo "2. 测试小镜像拉取速度..."
time docker pull hello-world:latest

echo
echo "3. 测试我们的股票分析镜像拉取速度..."
# 记录拉取前后的时间戳
start_time=$(date +%s.%N)
docker pull tuoyongjun1987/gupiao-stock-analysis:latest >/dev/null 2>&1
end_time=$(date +%s.%N)
elapsed=$(echo "$end_time - $start_time" | bc -l)

echo "股票分析镜像拉取耗时: ${elapsed}秒"

echo
echo "4. 检查镜像加速配置..."
cat /etc/docker/daemon.json 2>/dev/null || echo "未找到daemon.json"

echo
echo "5. 网络连接测试..."
echo "- 加速镜像连接: $(ping -c 1 docker.1ms.run >/dev/null 2>&1 && echo "✅ 正常" || echo "❌ 异常")"
echo "- Docker Hub直连: $(ping -c 1 registry-1.docker.io >/dev/null 2>&1 && echo "✅ 正常" || echo "❌ 异常")"
