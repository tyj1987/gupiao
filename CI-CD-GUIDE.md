# CI/CD 部署指南

## 🔧 配置说明

###### Docker Hub配置
- 用户名: tuoyongjun1987
- 镜像名: tuoyongjun1987/gupiao-stock-analysis
- 访问令牌: [您的Docker Hub访问令牌]GitHub Secrets配置
运行以下脚本自动配置所需的Secrets：
```bash
./setup-github-secrets.sh
```

手动配置的Secrets:
- `DOCKER_HUB_TOKEN`: [您的Docker Hub访问令牌]
- `TEST_SERVER_PASSWORD`: [测试服务器密码]  
- `PROD_SERVER_PASSWORD`: [生产服务器密码]

### 2. 服务器配置

#### 生产服务器 (47.94.225.76)
- 用户名: root
- SSH密码: [您的生产服务器密码]
- 端口: 22
- 访问地址: http://47.94.225.76:8501

#### 测试服务器 (192.168.2.8)  
- 用户名: root
- SSH密码: [您的测试服务器密码]
- 端口: 22
- 访问地址: http://192.168.2.8:8501

### 3. Docker Hub配置
- 用户名: tuoyongjun1987
- 镜像名: tuoyongjun1987/gupiao-stock-analysis
- 访问令牌: [您的Docker Hub访问令牌]

## 🚀 部署流程

### 自动部署
1. 推送代码到 `main` 分支
2. GitHub Actions自动运行CI/CD流程
3. 依次部署到测试服务器和生产服务器

### 手动部署
1. 在服务器上运行初始化脚本:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/tyj1987/gupiao/main/server-init.sh | bash
   ```

2. 登录Docker Hub:
   ```bash
   docker login -u tuoyongjun1987
   # 输入令牌: [您的Docker Hub访问令牌]
   ```

3. 启动应用:
   ```bash
   docker run -d \
     --name gupiao-app \
     --restart unless-stopped \
     -p 8501:8501 \
     tuoyongjun1987/gupiao-stock-analysis:latest
   ```

## 📋 CI/CD工作流

### 流程步骤
1. **测试阶段**: 运行Python环境测试，验证依赖和应用文件
2. **构建阶段**: 构建Docker镜像并推送到Docker Hub
3. **测试部署**: 自动部署到测试服务器进行验证
4. **生产部署**: 验证通过后部署到生产服务器
5. **通知阶段**: 发送部署结果通知

### 触发条件
- 推送到 `main` 或 `develop` 分支
- 创建针对 `main` 分支的Pull Request

### 环境变量
- `ENVIRONMENT`: production/test
- `STREAMLIT_SERVER_PORT`: 8501
- `STREAMLIT_SERVER_ADDRESS`: 0.0.0.0
- `STREAMLIT_SERVER_HEADLESS`: true

## 🔍 监控和维护

### 健康检查
应用提供健康检查端点: `/healthz`

### 日志查看
```bash
# 查看容器日志
docker logs gupiao-app

# 查看应用日志
docker exec gupiao-app tail -f /app/logs/app.log
```

### 更新部署
```bash
# 停止当前容器
docker stop gupiao-app && docker rm gupiao-app

# 拉取最新镜像
docker pull tuoyongjun1987/gupiao-stock-analysis:latest

# 重新启动
docker run -d --name gupiao-app --restart unless-stopped -p 8501:8501 tuoyongjun1987/gupiao-stock-analysis:latest
```

## 🔐 安全配置

### 防火墙设置
```bash
ufw enable
ufw allow ssh
ufw allow 8501/tcp
ufw allow 80/tcp
ufw allow 443/tcp
```

### SSL配置 (可选)
使用nginx反向代理配置HTTPS:
```bash
docker-compose -f docker-compose.production.yml up -d
```

## 📞 联系信息
- GitHub用户: tyj1987
- 邮箱: tuoyongjun1987@qq.com
- 仓库: https://github.com/tyj1987/gupiao
