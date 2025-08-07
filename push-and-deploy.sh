#!/bin/bash

# 快速推送到GitHub并触发CI/CD的脚本

set -e

echo "🚀 准备推送代码到GitHub..."

# 检查git是否已初始化
if [ ! -d ".git" ]; then
    echo "📝 初始化Git仓库..."
    git init
    git remote add origin https://github.com/tyj1987/gupiao.git
fi

# 配置Git用户信息
echo "👤 配置Git用户信息..."
git config user.name "tyj1987"
git config user.email "tuoyongjun1987@qq.com"

# 添加所有文件
echo "📁 添加文件到Git..."
git add .

# 提交代码
COMMIT_MESSAGE="${1:-"更新CI/CD配置和依赖文件"}"
echo "💾 提交代码: $COMMIT_MESSAGE"
git commit -m "$COMMIT_MESSAGE" || echo "没有新的更改需要提交"

# 推送到GitHub
echo "📤 推送到GitHub..."
git push -u origin main

echo "✅ 推送完成！"
echo ""
echo "🔗 查看GitHub Actions进度:"
echo "https://github.com/tyj1987/gupiao/actions"
echo ""
echo "📱 部署完成后的访问地址:"
echo "测试服务器: http://192.168.2.8:8501"
echo "生产服务器: http://47.94.225.76:8501"
