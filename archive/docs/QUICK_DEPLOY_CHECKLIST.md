# 🚀 CentOS 7.9 + 宝塔系统快速部署清单

## 📋 部署前准备

### ✅ 环境要求检查
- [ ] CentOS 7.9.2009 x86_64
- [ ] Python 3.7.9
- [ ] 宝塔Linux面板已安装
- [ ] 内存 ≥ 2GB
- [ ] 磁盘空间 ≥ 10GB
- [ ] 网络连接正常

### ✅ 文件准备
- [ ] 项目源代码已准备
- [ ] Tushare API Token已获取
- [ ] 服务器SSH访问正常

---

## 🎯 快速部署步骤

### 第1步：环境检查 (3分钟)
```bash
# 上传并运行环境检查脚本
chmod +x check_environment.sh
./check_environment.sh
```

### 第2步：上传项目文件 (5分钟)
**方式A：宝塔面板上传**
1. 登录宝塔面板
2. 文件管理 → `/www/wwwroot/`
3. 创建 `gupiao` 目录
4. 上传项目文件

**方式B：命令行上传**
```bash
# 在本地执行
scp -r /path/to/gupiao/* root@your-server:/www/wwwroot/gupiao/
```

### 第3步：自动部署 (10分钟)
```bash
cd /www/wwwroot/gupiao
chmod +x deploy.sh
./deploy.sh
```

### 第4步：配置API密钥 (2分钟)
```bash
vim /www/wwwroot/gupiao/config/api_keys.py
# 设置 TUSHARE_TOKEN = "your_token_here"
```

### 第5步：宝塔面板配置 (3分钟)
1. 安全 → 添加端口规则 → 8501/TCP
2. 网站 → 添加站点（可选域名配置）
3. SSL证书申请（可选HTTPS）

### 第6步：启动验证 (2分钟)
```bash
# 启动应用
supervisorctl start gupiao

# 检查状态
supervisorctl status gupiao

# 测试访问
curl -I http://localhost:8501
```

---

## 🔧 管理命令

```bash
# 使用管理脚本
chmod +x manage.sh

./manage.sh start     # 启动服务
./manage.sh stop      # 停止服务
./manage.sh restart   # 重启服务
./manage.sh status    # 查看状态
./manage.sh logs      # 查看日志
./manage.sh update    # 更新数据
./manage.sh backup    # 备份系统
./manage.sh health    # 健康检查
```

---

## 🌐 访问地址

- **直接访问**: http://your-server-ip:8501
- **域名访问**: http://your-domain.com (需配置Nginx)
- **HTTPS访问**: https://your-domain.com (需配置SSL)

---

## 🎉 功能验证

### ✅ 基础功能测试
- [ ] 搜索"中石油" - 应返回相关股票
- [ ] 搜索"601857" - 精确代码匹配  
- [ ] 搜索"腾讯" - 港股搜索
- [ ] 搜索"苹果" - 美股搜索

### ✅ 系统功能测试
- [ ] 股票风险评估正常
- [ ] 数据更新功能正常
- [ ] 页面响应速度良好
- [ ] 日志记录正常

---

## 🚨 故障排除

### 常见问题快速解决

**❌ 端口无法访问**
```bash
# 检查防火墙
firewall-cmd --list-ports
firewall-cmd --permanent --add-port=8501/tcp
firewall-cmd --reload
```

**❌ 应用启动失败**
```bash
# 查看日志
tail -f /var/log/gupiao.log

# 检查权限
chown -R www:www /www/wwwroot/gupiao
```

**❌ 依赖安装失败**
```bash
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

**❌ 内存不足**
```bash
# 创建交换文件
sudo dd if=/dev/zero of=/swapfile bs=1024 count=1048576
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 📞 技术支持

### 🔍 日志文件位置
- 应用日志: `/var/log/gupiao.log`
- Nginx日志: `/www/wwwlogs/gupiao.access.log`
- 系统日志: `/var/log/messages`

### 🔧 配置文件位置
- 应用配置: `/www/wwwroot/gupiao/config/`
- Supervisor配置: `/etc/supervisor/conf.d/gupiao.conf`
- Nginx配置: 宝塔面板 → 网站 → 配置

### 📊 监控命令
```bash
# 系统资源监控
top
htop
df -h
free -h

# 应用状态监控
supervisorctl status
netstat -tlnp | grep 8501
```

---

## 🏆 部署成功标志

当您看到以下内容时，说明部署成功：

✅ **5,728只股票数据库** - 相比原来283只增长1924%  
✅ **智能搜索功能** - 支持名称、代码、拼音搜索  
✅ **实时风险评估** - 多维度风险分析系统  
✅ **Web界面正常** - Streamlit界面响应流畅  
✅ **进程管理完善** - Supervisor自动重启  
✅ **监控日志健全** - 完整的运维监控体系  

## 🎯 总部署时间：约25分钟

---

**🎉 恭喜！您现在拥有了一个功能完整、性能强大的股票分析系统！**

立即访问 `http://your-server-ip:8501` 开始体验吧！
