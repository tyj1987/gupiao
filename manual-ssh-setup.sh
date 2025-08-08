#!/bin/bash
# 手动SSH密钥安装脚本

echo "🔑 手动配置SSH密钥到生产服务器"
echo "=================================="

echo "📋 SSH公钥内容 (需要添加到生产服务器):"
echo ""
cat ~/.ssh/gupiao_deploy.pub
echo ""

echo "🔧 请手动执行以下命令："
echo ""
echo "1. SSH连接到生产服务器:"
echo "   ssh root@47.94.225.76"
echo "   密码: Tyj_198729"
echo ""
echo "2. 在服务器上执行:"
echo "   mkdir -p ~/.ssh"
echo "   chmod 700 ~/.ssh"
echo ""
echo "3. 将上面的公钥内容添加到 ~/.ssh/authorized_keys:"
echo "   echo '$(cat ~/.ssh/gupiao_deploy.pub)' >> ~/.ssh/authorized_keys"
echo "   chmod 600 ~/.ssh/authorized_keys"
echo ""
echo "4. 验证配置:"
echo "   exit  # 退出服务器"
echo "   ssh -i ~/.ssh/gupiao_deploy root@47.94.225.76 'echo \"SSH密钥配置成功\"'"
echo ""

# 测试当前SSH连接
echo "🧪 测试SSH连接..."
if ssh -i ~/.ssh/gupiao_deploy -o ConnectTimeout=5 -o StrictHostKeyChecking=no root@47.94.225.76 'echo "SSH密钥已配置成功!"' 2>/dev/null; then
    echo "✅ SSH密钥配置成功！"
    return 0
else
    echo "❌ SSH密钥尚未配置，请按上述步骤手动配置"
    return 1
fi
