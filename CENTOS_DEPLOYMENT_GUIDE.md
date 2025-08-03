# CentOS 7.9 + 宝塔系统 股票分析系统部署指南

## 📋 系统环境信息
- **操作系统**: CentOS 7.9.2009 x86_64
- **Python版本**: Python 3.7.9
- **面板系统**: 宝塔Linux面板
- **项目类型**: 股票分析与风险评估系统
- **Web框架**: Streamlit
- **数据源**: AkShare + YFinance + Tushare

---

## 🚀 第一步：服务器环境准备

### 1.1 系统更新
```bash
# 更新系统包
sudo yum update -y

# 安装必要的系统工具
sudo yum install -y wget curl git vim
```

### 1.2 宝塔面板相关
确保您的宝塔面板已安装并正常运行：
```bash
# 查看宝塔面板状态
sudo /etc/init.d/bt status

# 如果需要重启宝塔
sudo /etc/init.d/bt restart
```

### 1.3 Python环境验证
```bash
# 检查Python版本
python3 --version
# 应该显示: Python 3.7.9

# 检查pip3
pip3 --version
```

---

## 🐍 第二步：Python环境配置

### 2.1 安装Python依赖管理工具
```bash
# 升级pip
pip3 install --upgrade pip

# 安装虚拟环境工具
pip3 install virtualenv
```

### 2.2 创建项目目录
```bash
# 在合适位置创建项目目录（推荐在/www/wwwroot/下）
sudo mkdir -p /www/wwwroot/gupiao
cd /www/wwwroot/gupiao

# 设置目录权限
sudo chown -R www:www /www/wwwroot/gupiao
```

### 2.3 创建虚拟环境
```bash
# 切换到项目目录
cd /www/wwwroot/gupiao

# 创建虚拟环境
python3 -m virtualenv venv

# 激活虚拟环境
source venv/bin/activate

# 验证虚拟环境
which python
# 应该显示: /www/wwwroot/gupiao/venv/bin/python
```

---

## 📁 第三步：项目代码部署

### 3.1 代码上传方式（三选一）

#### 方式一：直接上传（推荐新手）
1. 打开宝塔面板 → 文件管理
2. 进入 `/www/wwwroot/gupiao` 目录
3. 上传您的项目文件（打包为zip）
4. 解压项目文件

#### 方式二：Git克隆（推荐）
```bash
cd /www/wwwroot/gupiao

# 如果代码在Git仓库中
git clone https://github.com/yourusername/gupiao.git .

# 或者从本地推送到服务器Git仓库
```

#### 方式三：SCP传输
```bash
# 在本地执行（替换为您的服务器IP）
scp -r /path/to/your/gupiao/* root@your-server-ip:/www/wwwroot/gupiao/
```

### 3.2 验证项目结构
```bash
cd /www/wwwroot/gupiao
ls -la

# 应该看到以下结构：
# ├── src/
# │   ├── ai/
# │   ├── data/
# │   └── ui/
# ├── config/
# ├── requirements.txt
# ├── main.py
# └── README.md
```

---

## 🔧 第四步：依赖包安装

### 4.1 激活虚拟环境并安装依赖
```bash
cd /www/wwwroot/gupiao
source venv/bin/activate

# 安装项目依赖
pip install -r requirements.txt

# 如果遇到网络问题，使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 4.2 验证关键依赖
```bash
# 验证主要包是否正确安装
python -c "import streamlit; print('Streamlit:', streamlit.__version__)"
python -c "import akshare; print('AkShare:', akshare.__version__)"
python -c "import yfinance; print('YFinance:', yfinance.__version__)"
python -c "import pandas; print('Pandas:', pandas.__version__)"
python -c "import numpy; print('Numpy:', numpy.__version__)"
```

---

## ⚙️ 第五步：配置文件设置

### 5.1 配置API密钥
```bash
cd /www/wwwroot/gupiao/config

# 复制配置文件模板
cp api_keys.example.py api_keys.py

# 编辑配置文件
vim api_keys.py
```

在 `api_keys.py` 中配置：
```python
# Tushare Pro API Token
TUSHARE_TOKEN = "your_tushare_token_here"

# 其他配置保持默认即可
```

### 5.2 设置文件权限
```bash
# 设置配置文件权限（安全考虑）
chmod 600 /www/wwwroot/gupiao/config/api_keys.py

# 设置项目目录权限
chown -R www:www /www/wwwroot/gupiao
```

---

## 🌐 第六步：Web服务配置

### 6.1 创建启动脚本
```bash
cd /www/wwwroot/gupiao

# 创建启动脚本
cat > start_app.sh << 'EOF'
#!/bin/bash
cd /www/wwwroot/gupiao
source venv/bin/activate
streamlit run src/ui/streamlit_app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
EOF

# 设置执行权限
chmod +x start_app.sh
```

### 6.2 测试应用启动
```bash
# 激活虚拟环境
source venv/bin/activate

# 测试启动（前台运行，用于调试）
streamlit run src/ui/streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

如果看到以下输出说明成功：
```
You can now view your Streamlit app in your browser.
URL: http://your-server-ip:8501
```

按 `Ctrl+C` 停止测试。

---

## 🔒 第七步：防火墙和端口配置

### 7.1 开放端口（在宝塔面板中）
1. 登录宝塔面板
2. 进入 "安全" 选项
3. 添加端口规则：
   - **端口**: 8501
   - **协议**: TCP
   - **策略**: 放行
   - **备注**: 股票分析系统

### 7.2 系统防火墙配置
```bash
# CentOS 7 使用firewalld
sudo firewall-cmd --permanent --add-port=8501/tcp
sudo firewall-cmd --reload

# 验证端口开放
sudo firewall-cmd --list-ports
```

---

## 🚀 第八步：进程管理（使用Supervisor）

### 8.1 安装Supervisor
```bash
# 通过宝塔面板安装，或手动安装
pip3 install supervisor

# 创建配置目录
sudo mkdir -p /etc/supervisor/conf.d
```

### 8.2 创建Supervisor配置
```bash
sudo vim /etc/supervisor/conf.d/gupiao.conf
```

配置内容：
```ini
[program:gupiao]
command=/www/wwwroot/gupiao/venv/bin/streamlit run src/ui/streamlit_app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
directory=/www/wwwroot/gupiao
user=www
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/gupiao.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=3
environment=PATH="/www/wwwroot/gupiao/venv/bin"
```

### 8.3 启动Supervisor服务
```bash
# 重新加载配置
sudo supervisorctl reread
sudo supervisorctl update

# 启动应用
sudo supervisorctl start gupiao

# 查看状态
sudo supervisorctl status
```

---

## 🌍 第九步：Nginx反向代理配置（可选）

### 9.1 在宝塔面板配置域名
1. 进入宝塔面板 → 网站
2. 添加站点：
   - **域名**: your-domain.com（或使用IP）
   - **根目录**: /www/wwwroot/gupiao
   - **PHP版本**: 纯静态

### 9.2 配置Nginx反向代理
在宝塔面板中，编辑该站点的Nginx配置：
```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为您的域名
    
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Streamlit特殊配置
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
```

### 9.3 SSL证书配置（可选）
在宝塔面板中为域名申请和配置SSL证书，实现HTTPS访问。

---

## 📊 第十步：系统验证和测试

### 10.1 功能验证
```bash
# 检查进程状态
sudo supervisorctl status gupiao

# 检查日志
tail -f /var/log/gupiao.log

# 测试网络连接
curl -I http://localhost:8501
```

### 10.2 股票数据测试
访问: `http://your-server-ip:8501`（或配置的域名）

测试功能：
1. ✅ 搜索"中石油" - 应该返回相关股票
2. ✅ 搜索"601857" - 精确代码匹配
3. ✅ 查看股票风险评估
4. ✅ 验证5000+股票数据库

---

## 🔧 第十一步：系统维护

### 11.1 日常监控
```bash
# 查看应用状态
sudo supervisorctl status gupiao

# 查看系统资源使用
top
htop  # 如果已安装

# 查看磁盘使用
df -h
```

### 11.2 日志管理
```bash
# 查看应用日志
tail -f /var/log/gupiao.log

# 清理旧日志（可设置定时任务）
sudo logrotate -f /etc/logrotate.conf
```

### 11.3 数据更新
```bash
# 进入项目目录
cd /www/wwwroot/gupiao
source venv/bin/activate

# 手动刷新股票数据
python -c "
from src.data.universal_stock_fetcher import UniversalStockFetcher
fetcher = UniversalStockFetcher()
fetcher.refresh_all_data()
print('数据更新完成')
"
```

---

## 🚨 故障排除

### 常见问题解决

#### 问题1：端口访问失败
```bash
# 检查端口占用
netstat -tlnp | grep 8501

# 检查防火墙
sudo firewall-cmd --list-ports
```

#### 问题2：依赖包安装失败
```bash
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 单独安装问题包
pip install problematic-package -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

#### 问题3：内存不足
```bash
# 查看内存使用
free -h

# 创建交换文件（如果需要）
sudo dd if=/dev/zero of=/swapfile bs=1024 count=1048576
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### 问题4：权限问题
```bash
# 重新设置权限
sudo chown -R www:www /www/wwwroot/gupiao
sudo chmod -R 755 /www/wwwroot/gupiao
```

---

## 🎯 性能优化建议

### 缓存优化
```bash
# 在config/config.py中设置
CACHE_ENABLED = True
CACHE_EXPIRE_HOURS = 24
```

### 内存优化
```python
# 在应用启动时设置环境变量
export STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200
export STREAMLIT_SERVER_MAX_MESSAGE_SIZE=200
```

### 数据库优化
- 考虑使用Redis缓存热点数据
- 定期清理过期缓存文件

---

## 📝 部署检查清单

- [ ] CentOS 7.9系统已更新
- [ ] Python 3.7.9环境正常
- [ ] 宝塔面板运行正常
- [ ] 项目代码已上传
- [ ] 虚拟环境已创建并激活
- [ ] 依赖包安装完成
- [ ] API密钥配置正确
- [ ] 防火墙端口已开放
- [ ] Supervisor进程管理配置
- [ ] Nginx反向代理配置（可选）
- [ ] SSL证书配置（可选）
- [ ] 功能测试通过
- [ ] 监控和日志配置

---

## 🔗 重要链接

- **项目访问**: http://your-server-ip:8501
- **宝塔面板**: http://your-server-ip:8888
- **日志文件**: /var/log/gupiao.log
- **项目目录**: /www/wwwroot/gupiao

---

## 📞 技术支持

如果在部署过程中遇到问题：

1. 检查日志文件：`tail -f /var/log/gupiao.log`
2. 验证配置文件：检查API密钥和权限
3. 重启服务：`sudo supervisorctl restart gupiao`
4. 查看系统资源：`top` 和 `df -h`

---

**部署完成后，您将拥有一个功能完整的股票分析系统，包含5,728只股票的实时数据分析能力！** 🎉

## 🏆 系统特性总结

- ✅ **5,728只股票** - 全市场覆盖（相比原来283只增长1924%）
- ✅ **智能搜索** - 支持名称、代码、拼音搜索
- ✅ **实时风险评估** - 多维度风险分析
- ✅ **Web界面** - 友好的Streamlit界面
- ✅ **高可用性** - Supervisor进程管理
- ✅ **安全部署** - 防火墙和权限配置
- ✅ **生产就绪** - 完整的监控和日志系统
