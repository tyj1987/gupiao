# 🐳 Docker部署指南 - 股票分析系统

## 📋 系统要求

### 最低配置
- **CPU**: 2核心
- **内存**: 4GB RAM
- **磁盘**: 20GB可用空间
- **操作系统**: Linux (Ubuntu 18.04+, CentOS 7+) / macOS / Windows 10+

### 推荐配置
- **CPU**: 4核心
- **内存**: 8GB RAM
- **磁盘**: 50GB SSD
- **网络**: 稳定的互联网连接

---

## 🚀 快速开始

### 方式一：自动安装（推荐）

```bash
# 1. 下载项目
git clone <your-repo-url>
cd gupiao

# 2. 安装Docker环境（如果未安装）
chmod +x docker-manage.sh
sudo ./docker-manage.sh install

# 3. 配置API密钥
cp config/api_keys.example.py config/api_keys.py
vim config/api_keys.py  # 设置TUSHARE_TOKEN

# 4. 启动服务
./docker-manage.sh up

# 5. 访问系统
# 浏览器打开: http://localhost:8501
```

### 方式二：手动部署

```bash
# 1. 确保Docker和Docker Compose已安装
docker --version
docker-compose --version

# 2. 构建镜像
docker-compose build

# 3. 启动服务
docker-compose up -d

# 4. 查看状态
docker-compose ps
```

---

## 🔧 详细部署步骤

### 第1步：环境准备

#### 安装Docker（CentOS 7）
```bash
# 安装依赖
sudo yum install -y yum-utils

# 添加Docker仓库
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 安装Docker
sudo yum install -y docker-ce docker-ce-cli containerd.io

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 验证安装
docker --version
```

#### 安装Docker Compose
```bash
# 下载Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 设置执行权限
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker-compose --version
```

#### 配置用户权限（可选）
```bash
# 将当前用户添加到docker组
sudo usermod -aG docker $USER

# 重新登录或执行
newgrp docker
```

### 第2步：获取项目代码

```bash
# 方式1: Git克隆
git clone <your-repo-url>
cd gupiao

# 方式2: 上传压缩包
# 上传 gupiao_production_deploy.tar.gz 到服务器
tar -xzf gupiao_production_deploy.tar.gz
cd gupiao_deployment_*
```

### 第3步：配置文件

```bash
# 复制配置文件模板
cp config/api_keys.example.py config/api_keys.py

# 编辑配置文件
vim config/api_keys.py
```

在 `config/api_keys.py` 中设置：
```python
# Tushare Pro API Token
TUSHARE_TOKEN = "your_tushare_token_here"

# 其他配置保持默认
```

### 第4步：构建和启动

```bash
# 构建Docker镜像
docker-compose build

# 启动所有服务
docker-compose up -d

# 查看启动状态
docker-compose ps
```

### 第5步：验证部署

```bash
# 查看容器状态
docker-compose ps

# 查看日志
docker-compose logs gupiao

# 测试访问
curl -I http://localhost:8501
```

---

## 📊 服务架构

### 核心服务

1. **gupiao** - 主应用容器
   - 端口: 8501
   - 功能: Streamlit Web应用
   - 数据: 5,728只股票分析

2. **nginx** - 反向代理（可选）
   - 端口: 80, 443
   - 功能: 负载均衡，SSL终止
   - 配置: nginx.conf

3. **redis** - 缓存服务（可选）
   - 端口: 6379
   - 功能: 高性能数据缓存
   - 存储: 热点股票数据

### 数据持久化

- **gupiao_cache**: 股票数据缓存
- **gupiao_logs**: 应用日志
- **gupiao_redis_data**: Redis数据

---

## 🔧 管理命令

使用 `docker-manage.sh` 脚本进行日常管理：

```bash
# 构建镜像
./docker-manage.sh build

# 启动服务
./docker-manage.sh up

# 停止服务
./docker-manage.sh down

# 重启服务
./docker-manage.sh restart

# 查看状态
./docker-manage.sh status

# 查看日志
./docker-manage.sh logs
./docker-manage.sh logs gupiao  # 查看特定服务

# 进入容器
./docker-manage.sh shell

# 更新服务
./docker-manage.sh update

# 备份数据
./docker-manage.sh backup

# 清理环境
./docker-manage.sh clean
```

---

## 🌐 网络配置

### 端口映射

| 服务 | 容器端口 | 宿主机端口 | 描述 |
|------|---------|-----------|------|
| gupiao | 8501 | 8501 | Streamlit应用 |
| nginx | 80 | 80 | HTTP访问 |
| nginx | 443 | 443 | HTTPS访问 |
| redis | 6379 | 6379 | Redis缓存 |

### 防火墙配置

```bash
# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8501/tcp
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload

# Ubuntu/Debian
sudo ufw allow 8501
sudo ufw allow 80
sudo ufw allow 443
```

---

## 🔒 安全配置

### SSL证书配置

1. 创建SSL目录：
```bash
mkdir -p ssl
```

2. 放置证书文件：
```bash
ssl/
├── cert.pem
└── key.pem
```

3. 修改nginx.conf，取消HTTPS部分注释

### 环境变量安全

```bash
# 创建环境变量文件
cat > .env << EOF
TUSHARE_TOKEN=your_token_here
REDIS_PASSWORD=your_redis_password
EOF

# 设置文件权限
chmod 600 .env
```

---

## 📊 监控和日志

### 日志查看

```bash
# 实时日志
docker-compose logs -f gupiao

# 特定时间范围的日志
docker-compose logs --since="2h" gupiao

# 日志文件位置
docker-compose exec gupiao ls /var/log/
```

### 性能监控

```bash
# 容器资源使用
docker stats

# 特定容器统计
docker stats gupiao_app

# 系统资源
docker system df
```

### 健康检查

```bash
# 手动健康检查
curl http://localhost:8501/_stcore/health

# 查看健康状态
docker-compose ps
```

---

## 🔄 数据管理

### 备份数据

```bash
# 自动备份
./docker-manage.sh backup

# 手动备份存储卷
docker run --rm \
  -v gupiao_gupiao_cache:/data \
  -v $(pwd)/backup:/backup \
  alpine tar -czf /backup/cache_backup_$(date +%Y%m%d).tar.gz -C /data .
```

### 恢复数据

```bash
# 恢复存储卷
docker run --rm \
  -v gupiao_gupiao_cache:/data \
  -v $(pwd)/backup:/backup \
  alpine tar -xzf /backup/cache_backup_20250803.tar.gz -C /data
```

### 更新股票数据

```bash
# 进入容器执行更新
docker-compose exec gupiao python -c "
from src.data.universal_stock_fetcher import UniversalStockFetcher
fetcher = UniversalStockFetcher()
fetcher.refresh_all_data()
print('数据更新完成')
"
```

---

## 🚀 扩展配置

### 多实例部署

```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  gupiao:
    # ... 其他配置
    deploy:
      replicas: 3
  
  nginx:
    # 配置负载均衡
    # ... 配置文件
```

启动多实例：
```bash
docker-compose -f docker-compose.yml -f docker-compose.scale.yml up -d --scale gupiao=3
```

### Redis集群

```yaml
# 添加Redis集群配置
redis-cluster:
  image: redis:alpine
  command: redis-server --cluster-enabled yes
  # ... 其他配置
```

---

## 🚨 故障排除

### 常见问题

#### 问题1：容器启动失败
```bash
# 查看详细日志
docker-compose logs gupiao

# 检查配置文件
docker-compose config

# 重新构建镜像
docker-compose build --no-cache gupiao
```

#### 问题2：端口占用
```bash
# 查看端口占用
netstat -tlnp | grep 8501

# 修改端口映射
# 编辑 docker-compose.yml
ports:
  - "8502:8501"  # 改为其他端口
```

#### 问题3：内存不足
```bash
# 查看内存使用
docker stats

# 限制容器内存
docker-compose.yml:
services:
  gupiao:
    mem_limit: 2g
    mem_reservation: 1g
```

#### 问题4：磁盘空间不足
```bash
# 清理Docker资源
docker system prune -a

# 清理悬挂的存储卷
docker volume prune
```

---

## 📈 性能优化

### 镜像优化

```dockerfile
# 多阶段构建
FROM python:3.7-slim as builder
# 编译依赖

FROM python:3.7-slim as runtime
# 运行时环境
COPY --from=builder /app /app
```

### 缓存优化

```yaml
# Redis配置优化
redis:
  image: redis:alpine
  command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
```

### 资源限制

```yaml
services:
  gupiao:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
```

---

## 🎯 生产环境建议

### 1. 资源配置
- CPU: 至少2核心
- 内存: 至少4GB
- 存储: SSD推荐

### 2. 安全设置
- 使用非root用户运行
- 配置SSL证书
- 定期更新镜像

### 3. 监控告警
- 集成Prometheus监控
- 配置日志收集
- 设置健康检查

### 4. 备份策略
- 每日自动备份
- 异地存储备份
- 定期恢复测试

---

## 📞 技术支持

### 🔍 调试信息收集

```bash
# 系统信息
docker version
docker-compose version
uname -a

# 容器信息
docker-compose ps
docker-compose logs gupiao > gupiao.log

# 网络信息
docker network ls
docker network inspect gupiao_gupiao_network
```

### 📂 重要文件位置

- 配置文件: `./config/`
- Docker配置: `./docker-compose.yml`
- Nginx配置: `./nginx.conf`
- 日志文件: Docker存储卷 `gupiao_logs`
- 缓存数据: Docker存储卷 `gupiao_cache`

---

**🎉 恭喜！您现在拥有了一个完全容器化的股票分析系统！**

## 🏆 Docker部署优势

✅ **环境一致性** - 开发、测试、生产环境完全一致  
✅ **快速部署** - 一键启动，5分钟内完成部署  
✅ **易于扩展** - 支持水平扩展和负载均衡  
✅ **资源隔离** - 容器级别的资源管理和隔离  
✅ **版本管理** - 镜像版本化，支持快速回滚  
✅ **云原生** - 支持Kubernetes等容器编排平台  

访问 `http://localhost:8501` 开始使用您的5,728只股票分析系统！🚀
