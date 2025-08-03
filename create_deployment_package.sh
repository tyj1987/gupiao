#!/bin/bash
# 创建生产环境部署包脚本

echo "📦 正在创建股票分析系统部署包..."
echo "=================================="

# 设置变量
PACKAGE_NAME="gupiao_deployment_$(date +%Y%m%d_%H%M%S)"
TEMP_DIR="/tmp/$PACKAGE_NAME"
PACKAGE_FILE="/tmp/${PACKAGE_NAME}.tar.gz"

# 创建临时目录
mkdir -p $TEMP_DIR

echo "📁 准备部署文件..."

# 核心应用代码
echo "  - 复制核心应用代码..."
cp -r src/ $TEMP_DIR/
cp -r config/ $TEMP_DIR/
cp main.py $TEMP_DIR/
cp simple_app.py $TEMP_DIR/
cp requirements*.txt $TEMP_DIR/

# 部署文档和脚本
echo "  - 复制部署文档..."
cp CENTOS_DEPLOYMENT_GUIDE.md $TEMP_DIR/
cp QUICK_DEPLOY_CHECKLIST.md $TEMP_DIR/
cp README.md $TEMP_DIR/

echo "  - 复制部署脚本..."
cp deploy.sh $TEMP_DIR/
cp manage.sh $TEMP_DIR/
cp check_environment.sh $TEMP_DIR/
cp start_app.sh $TEMP_DIR/
cp nginx_config_template.conf $TEMP_DIR/

# 设置脚本权限
chmod +x $TEMP_DIR/*.sh

# 创建部署说明文件
cat > $TEMP_DIR/DEPLOY_README.md << 'EOF'
# 🚀 股票分析系统部署包

## 📋 包含内容
- 完整应用源代码
- 自动化部署脚本  
- 详细部署文档
- 系统管理工具
- Nginx配置模板

## 🎯 快速部署（CentOS 7.9 + 宝塔）

### 1. 上传解压
```bash
# 上传到服务器并解压
tar -xzf gupiao_deployment_*.tar.gz
cd gupiao_deployment_*
```

### 2. 环境检查
```bash
./check_environment.sh
```

### 3. 一键部署
```bash
sudo ./deploy.sh
```

### 4. 配置API密钥
```bash
vim config/api_keys.py
# 设置: TUSHARE_TOKEN = "your_token_here"
```

### 5. 管理系统
```bash
./manage.sh status    # 查看状态
./manage.sh start     # 启动服务
./manage.sh logs      # 查看日志
```

## 📖 详细文档
- `CENTOS_DEPLOYMENT_GUIDE.md` - 详细部署指南
- `QUICK_DEPLOY_CHECKLIST.md` - 快速部署清单

## 🌐 访问地址
http://your-server-ip:8501

## 🏆 系统特性
- ✅ 5,728只股票全市场覆盖
- ✅ 智能搜索和风险评估
- ✅ Web界面友好易用
- ✅ 自动重启和监控

祝您部署成功！🎉
EOF

# 创建版本信息文件
cat > $TEMP_DIR/VERSION.txt << EOF
股票分析系统部署包
==================
版本: v2.0
构建时间: $(date)
构建者: AI Assistant
目标环境: CentOS 7.9 + 宝塔系统

系统特性:
- 股票数量: 5,728只 (相比原版283只增长1924%)
- 数据源: AkShare + YFinance + Tushare
- Web框架: Streamlit
- 进程管理: Supervisor
- 反向代理: Nginx

文件清单:
$(ls -la $TEMP_DIR/)
EOF

echo "📊 统计部署包信息..."

# 统计文件数量和大小
FILE_COUNT=$(find $TEMP_DIR -type f | wc -l)
DIR_SIZE=$(du -sh $TEMP_DIR | cut -f1)

echo "  - 文件数量: $FILE_COUNT"
echo "  - 目录大小: $DIR_SIZE"

echo "🗜️ 创建压缩包..."

# 创建tar.gz压缩包
cd /tmp
tar -czf $PACKAGE_FILE \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='.gitignore' \
    --exclude='venv' \
    --exclude='.DS_Store' \
    $PACKAGE_NAME/

# 检查压缩包
if [ -f "$PACKAGE_FILE" ]; then
    PACKAGE_SIZE=$(du -sh $PACKAGE_FILE | cut -f1)
    echo "✅ 压缩包创建成功!"
    echo "  - 文件名: $(basename $PACKAGE_FILE)"
    echo "  - 大小: $PACKAGE_SIZE"
    echo "  - 路径: $PACKAGE_FILE"
else
    echo "❌ 压缩包创建失败!"
    exit 1
fi

# 清理临时目录
rm -rf $TEMP_DIR

echo ""
echo "🎯 部署包创建完成!"
echo "=================================="
echo "📦 压缩包: $PACKAGE_FILE"
echo "📊 大小: $PACKAGE_SIZE"
echo "📄 文件数: $FILE_COUNT"
echo ""
echo "📋 下一步操作:"
echo "1. 下载压缩包到本地"
echo "2. 上传到目标服务器"
echo "3. 解压并运行 ./deploy.sh"
echo "4. 配置API密钥"
echo "5. 访问 http://server-ip:8501"
echo ""
echo "🎉 祝您部署成功!"
