# 🚀 股票分析系统 - 完整部署指南

## 📋 系统概述

**股票分析与风险评估系统** - 从283只股票扩展到5,728只股票，增长1924%

### 🏆 核心特性
- ✅ **5,728只股票** - 全市场覆盖（A股5,562只 + 港股20只 + 美股146只）
- ✅ **智能搜索** - 支持名称、代码、拼音缩写搜索
- ✅ **实时风险评估** - 多维度风险分析系统
- ✅ **Web界面** - 现代化Streamlit界面
- ✅ **多种部署方式** - Docker/传统/云部署

---

## 🎯 部署方式选择

| 部署方式 | 难度 | 时间 | 适用场景 | 推荐指数 |
|---------|------|------|----------|---------|
| **Docker部署** | 简单 | 5分钟 | 所有环境 | ⭐⭐⭐⭐⭐ |
| **传统部署** | 中等 | 25分钟 | CentOS/Ubuntu | ⭐⭐⭐⭐ |
| **云部署** | 简单 | 10分钟 | 云服务器 | ⭐⭐⭐⭐ |

---

## 🐳 方式一：Docker部署（推荐）

### 🚀 超快速部署（5分钟）

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd gupiao

# 2. 配置API密钥
cp config/api_keys.example.py config/api_keys.py
vim config/api_keys.py  # 设置TUSHARE_TOKEN

# 3. 一键部署
chmod +x docker-quick-deploy.sh
./docker-quick-deploy.sh

# 4. 访问系统
# 浏览器打开: http://localhost:8501
```

### 🔧 完整Docker部署

#### 环境要求
- Docker 20.10+
- Docker Compose 1.29+
- 4GB RAM, 20GB 磁盘空间

#### 部署步骤

```bash
# 1. 检查Docker环境
docker --version
docker-compose --version

# 2. 构建镜像
docker-compose build

# 3. 启动服务
docker-compose up -d

# 4. 查看状态
docker-compose ps
```

#### 管理命令

```bash
# 使用管理脚本
chmod +x docker-manage.sh

./docker-manage.sh status     # 查看状态
./docker-manage.sh logs       # 查看日志
./docker-manage.sh restart    # 重启服务
./docker-manage.sh backup     # 备份数据
./docker-manage.sh clean      # 清理环境
```

#### Docker服务架构

**简化版（开发测试）**
```
┌─────────────────┐
│   股票分析系统    │
│  (Streamlit)    │
│   Port: 8501    │
└─────────────────┘
```

**完整版（生产环境）**
```
┌─────────┐   ┌─────────────┐   ┌─────────┐
│ Nginx   │──▶│ 股票分析系统  │──▶│ Redis   │
│ 80/443  │   │    8501     │   │  6379   │
└─────────┘   └─────────────┘   └─────────┘
```

---

## 🖥️ 方式二：传统部署

### CentOS 7.9 + 宝塔系统

#### 环境要求
- CentOS 7.9.2009 x86_64
- Python 3.7.9
- 宝塔Linux面板
- 4GB RAM, 20GB 磁盘空间

#### 快速部署

```bash
# 1. 环境检查
chmod +x check_environment.sh
./check_environment.sh

# 2. 一键部署
chmod +x deploy.sh
sudo ./deploy.sh

# 3. 配置API密钥
vim /www/wwwroot/gupiao/config/api_keys.py

# 4. 开放端口（宝塔面板）
# 安全 → 端口规则 → 添加8501/TCP

# 5. 访问系统
# http://your-server-ip:8501
```

#### 详细部署步骤

1. **系统准备**
```bash
# 更新系统
sudo yum update -y
sudo yum install -y wget curl git vim python3 python3-pip

# 创建项目目录
sudo mkdir -p /www/wwwroot/gupiao
sudo chown -R www:www /www/wwwroot/gupiao
```

2. **Python环境**
```bash
cd /www/wwwroot/gupiao
python3 -m virtualenv venv
source venv/bin/activate
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

3. **进程管理**
```bash
# 安装Supervisor
pip3 install supervisor

# 配置Supervisor
sudo vim /etc/supervisor/conf.d/gupiao.conf
# [配置内容见详细文档]

# 启动服务
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start gupiao
```

#### 系统管理

```bash
# 使用管理脚本
chmod +x manage.sh

./manage.sh start      # 启动服务
./manage.sh status     # 查看状态
./manage.sh logs       # 查看日志
./manage.sh update     # 更新数据
./manage.sh backup     # 备份系统
```

### Ubuntu 20.04+ 部署

```bash
# 1. 安装依赖
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git curl

# 2. 创建项目
git clone <your-repo-url>
cd gupiao
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. 配置服务
sudo cp systemd/gupiao.service /etc/systemd/system/
sudo systemctl enable gupiao
sudo systemctl start gupiao

# 4. 配置Nginx
sudo cp nginx/gupiao.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/gupiao /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

---

## ☁️ 方式三：云部署

### 阿里云ECS部署

```bash
# 1. 购买ECS实例
# 配置: 2核4GB, CentOS 7.9, 40GB SSD

# 2. 安全组配置
# 开放端口: 22(SSH), 80(HTTP), 443(HTTPS), 8501(应用)

# 3. 安装宝塔面板
yum install -y wget && wget -O install.sh http://download.bt.cn/install/install_6.0.sh && sh install.sh

# 4. 部署应用
# 按照传统部署方式进行
```

### 腾讯云CVM部署

```bash
# 1. 购买CVM实例
# 配置: 标准型S5.MEDIUM4, Ubuntu 20.04

# 2. 防火墙配置
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8501

# 3. Docker部署
sudo apt update
sudo apt install -y docker.io docker-compose
# 按照Docker部署方式进行
```

### AWS EC2部署

```bash
# 1. 启动EC2实例
# AMI: Amazon Linux 2, 实例类型: t3.medium

# 2. 安装Docker
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# 3. 部署应用
# 按照Docker部署方式进行
```

---

## ⚙️ 配置文件说明

### API密钥配置

```python
# config/api_keys.py
TUSHARE_TOKEN = "your_tushare_token_here"  # 必需
```

获取Tushare Token：
1. 访问 https://tushare.pro/register
2. 注册账号并获取token
3. 将token填入配置文件

### 环境变量配置

```bash
# .env文件（可选）
TUSHARE_TOKEN=your_token_here
STREAMLIT_SERVER_PORT=8501
CACHE_EXPIRE_HOURS=24
```

### Nginx配置（生产环境）

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # Streamlit特殊配置
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
```

---

## 🔧 系统管理

### 日常维护

```bash
# 查看系统状态
./manage.sh status          # 传统部署
./docker-manage.sh status   # Docker部署

# 更新股票数据
./manage.sh update          # 传统部署  
./docker-manage.sh update   # Docker部署

# 查看日志
./manage.sh logs            # 传统部署
./docker-manage.sh logs     # Docker部署

# 备份数据
./manage.sh backup          # 传统部署
./docker-manage.sh backup   # Docker部署
```

### 性能监控

```bash
# 系统资源
top
htop
df -h
free -h

# 应用监控
curl -I http://localhost:8501/_stcore/health

# Docker监控
docker stats
docker-compose logs -f
```

### 数据管理

```bash
# 手动刷新股票数据
python -c "
from src.data.universal_stock_fetcher import UniversalStockFetcher
fetcher = UniversalStockFetcher()
fetcher.refresh_all_data()
print('数据更新完成')
"

# 清理缓存
rm -rf /tmp/stock_cache/*

# 查看统计信息
python -c "
from src.data.universal_stock_fetcher import UniversalStockFetcher
fetcher = UniversalStockFetcher()
stats = fetcher.get_market_statistics()
print(f'总计: {stats[\"total\"]} 只股票')
"
```

---

## 🚨 故障排除

### 常见问题

#### 1. 端口访问失败
```bash
# 检查端口占用
netstat -tlnp | grep 8501

# 检查防火墙
sudo firewall-cmd --list-ports              # CentOS
sudo ufw status                             # Ubuntu
```

#### 2. 依赖安装失败
```bash
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 升级pip
pip install --upgrade pip
```

#### 3. 内存不足
```bash
# 查看内存使用
free -h

# 创建交换文件
sudo dd if=/dev/zero of=/swapfile bs=1024 count=2097152
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### 4. 股票数据获取失败
```bash
# 检查网络连接
ping tushare.pro
ping finance.yahoo.com

# 检查API密钥
python -c "
import tushare as ts
ts.set_token('your_token_here')
print('API连接正常')
"
```

### 日志分析

```bash
# 应用日志
tail -f /var/log/gupiao.log                 # 传统部署
docker-compose logs -f gupiao               # Docker部署

# 系统日志
tail -f /var/log/messages                   # CentOS
tail -f /var/log/syslog                     # Ubuntu

# Nginx日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

---

## 🔒 安全配置

### 基础安全

```bash
# 防火墙配置
sudo firewall-cmd --permanent --add-port=8501/tcp
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload

# 文件权限
chmod 600 config/api_keys.py
chown -R www:www /www/wwwroot/gupiao
```

### HTTPS配置

```bash
# 使用Let's Encrypt
sudo yum install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com

# 手动证书
mkdir -p ssl/
# 将证书文件放入ssl目录
# 配置nginx.conf启用HTTPS
```

### 访问控制

```bash
# IP白名单（nginx）
location / {
    allow 192.168.1.0/24;
    allow 10.0.0.0/8;
    deny all;
    
    proxy_pass http://127.0.0.1:8501;
}

# 基础认证
sudo htpasswd -c /etc/nginx/.htpasswd admin
# nginx配置中添加auth_basic指令
```

---

## 📈 性能优化

### 应用优化

```bash
# 启动时环境变量
export STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200
export STREAMLIT_SERVER_MAX_MESSAGE_SIZE=200
export STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false
```

### 缓存优化

```python
# config/config.py
CACHE_ENABLED = True
CACHE_EXPIRE_HOURS = 24
CACHE_DIR = "/tmp/stock_cache"
```

### 数据库优化

```bash
# 使用Redis缓存
sudo yum install -y redis
sudo systemctl start redis
sudo systemctl enable redis

# 配置应用使用Redis
```

---

## 📊 监控告警

### Prometheus监控

```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
```

### 日志收集

```bash
# ELK Stack
docker-compose -f docker-compose.elk.yml up -d

# 访问Kibana: http://localhost:5601
```

---

## 🎯 生产环境建议

### 1. 硬件配置
- **CPU**: 4核心以上
- **内存**: 8GB以上  
- **磁盘**: SSD 100GB以上
- **网络**: 10Mbps以上带宽

### 2. 高可用配置
```bash
# 负载均衡
upstream gupiao_backend {
    server 127.0.0.1:8501;
    server 127.0.0.1:8502;
    server 127.0.0.1:8503;
}

# 数据库集群
# Redis Cluster / MySQL Master-Slave
```

### 3. 备份策略
```bash
# 数据备份
0 2 * * * /path/to/backup.sh

# 代码备份
0 3 * * 0 tar -czf /backup/code_$(date +\%Y\%m\%d).tar.gz /www/wwwroot/gupiao
```

### 4. 监控告警
```bash
# CPU使用率 > 80%
# 内存使用率 > 80%  
# 磁盘使用率 > 85%
# 服务响应时间 > 5s
```

---

## 📞 技术支持

### 🔍 问题诊断

```bash
# 系统信息收集
uname -a
python3 --version
docker --version
free -h
df -h

# 应用状态检查
curl -I http://localhost:8501
./manage.sh health
./docker-manage.sh status
```

### 📂 重要目录

| 目录 | 用途 | 路径 |
|------|------|------|
| 项目目录 | 应用代码 | `/www/wwwroot/gupiao` |
| 配置目录 | 配置文件 | `config/` |
| 日志目录 | 运行日志 | `/var/log/` |
| 缓存目录 | 数据缓存 | `/tmp/stock_cache/` |
| 备份目录 | 数据备份 | `/var/backup/gupiao/` |

### 📧 获取帮助

如果遇到问题：

1. 查看日志文件获取错误信息
2. 检查配置文件是否正确
3. 验证网络连接和API密钥
4. 查看系统资源使用情况
5. 参考故障排除章节

---

## 🏆 部署成功验证

### 功能测试清单

- [ ] 访问 `http://your-server:8501` 正常
- [ ] 搜索"中石油"返回相关结果
- [ ] 搜索"601857"精确匹配
- [ ] 搜索"腾讯"找到港股  
- [ ] 搜索"苹果"找到美股
- [ ] 风险评估功能正常
- [ ] 股票筛选功能正常
- [ ] 系统运行稳定无错误

### 性能指标

- ✅ **搜索响应时间** < 3秒
- ✅ **页面加载时间** < 5秒  
- ✅ **内存使用** < 2GB
- ✅ **CPU使用率** < 50%
- ✅ **股票数据库** 5,728只股票

---

**🎉 恭喜！您现在拥有了功能强大的股票分析系统！**

从原来的283只股票扩展到5,728只股票，增长了1924%，为您提供全市场的投资分析能力！

选择适合您的部署方式开始使用吧！🚀
