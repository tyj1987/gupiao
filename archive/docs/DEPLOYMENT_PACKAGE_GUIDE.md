# 🚀 股票分析系统生产环境部署包

## 📦 部署包信息

- **文件名**: `gupiao_production_deploy.tar.gz`
- **大小**: 112KB
- **包含文件**: 67个文件
- **目标环境**: CentOS 7.9 + 宝塔系统
- **创建时间**: 2025年8月3日

---

## 📋 包含内容

### 🎯 核心应用代码
- `src/` - 完整的应用源代码
  - `src/ai/` - AI分析模块（风险评估、ML模型等）
  - `src/data/` - 数据处理模块（5728只股票数据）
  - `src/ui/` - Streamlit Web界面
- `config/` - 配置文件目录
- `main.py` - 主程序入口
- `requirements.txt` - Python依赖清单

### 🔧 自动化部署工具
- `deploy.sh` - 一键自动部署脚本
- `manage.sh` - 系统管理脚本
- `check_environment.sh` - 环境检查脚本
- `start_app.sh` - 应用启动脚本

### 📖 部署文档
- `CENTOS_DEPLOYMENT_GUIDE.md` - 详细部署指南
- `QUICK_DEPLOY_CHECKLIST.md` - 快速部署清单
- `DEPLOY_README.md` - 部署包说明
- `README.md` - 项目说明文档

### ⚙️ 配置模板
- `nginx_config_template.conf` - Nginx反向代理配置
- `VERSION.txt` - 版本信息文件

---

## 🚀 快速部署流程

### 第1步：上传到服务器
```bash
# 使用SCP上传（替换your-server-ip）
scp gupiao_production_deploy.tar.gz root@your-server-ip:/root/

# 或使用宝塔面板文件管理上传
```

### 第2步：解压部署包
```bash
# 在服务器上执行
cd /root
tar -xzf gupiao_production_deploy.tar.gz
cd gupiao_deployment_*
```

### 第3步：环境检查
```bash
# 检查系统环境是否满足要求
./check_environment.sh
```

### 第4步：自动部署
```bash
# 一键部署（需要root权限）
sudo ./deploy.sh
```

### 第5步：配置API密钥
```bash
# 编辑配置文件
vim /www/wwwroot/gupiao/config/api_keys.py

# 设置Tushare Token
TUSHARE_TOKEN = "your_tushare_token_here"
```

### 第6步：开放端口（宝塔面板）
1. 登录宝塔面板
2. 安全 → 添加端口规则
3. 端口：8501，协议：TCP，策略：放行

### 第7步：访问系统
浏览器访问：`http://your-server-ip:8501`

---

## 🔧 系统管理命令

```bash
cd /www/wwwroot/gupiao

# 查看系统状态
./manage.sh status

# 启动/停止/重启服务
./manage.sh start
./manage.sh stop  
./manage.sh restart

# 查看实时日志
./manage.sh logs

# 更新股票数据
./manage.sh update

# 系统备份
./manage.sh backup

# 健康检查
./manage.sh health
```

---

## 🏆 系统特性

### 📊 数据覆盖
- **5,728只股票** - 全市场覆盖
- **A股**: 5,562只（上海A股 + 深圳A股）
- **港股**: 20只主要H股
- **美股**: 146只中概股和热门股票

### 🔍 搜索功能
- **智能搜索** - 支持股票名称、代码、拼音缩写
- **跨市场搜索** - 统一搜索A股、港股、美股
- **模糊匹配** - 容错搜索，提供搜索建议

### ⚡ 风险评估
- **多维度分析** - 市场风险、流动性风险、波动性风险等6大维度
- **实时评分** - 42-53分的精确评分系统
- **风险等级** - 低风险、中等风险、高风险分类

### 🌐 Web界面
- **Streamlit框架** - 现代化、响应式Web界面
- **实时数据** - 最新价格和技术指标
- **交互式图表** - 股票走势和分析图表

### 🔄 系统可靠性
- **自动重启** - Supervisor进程管理
- **日志监控** - 完整的日志记录和轮转
- **缓存优化** - 24小时智能缓存机制
- **故障恢复** - 自动故障检测和恢复

---

## 📈 性能指标

- **响应时间** - 搜索响应 < 3秒
- **数据更新** - 24小时自动缓存刷新
- **并发支持** - 支持多用户同时访问
- **内存使用** - 运行时内存 < 1GB
- **磁盘空间** - 系统占用 < 500MB

---

## 🚨 故障排除

### 常见问题

**❌ 无法访问8501端口**
```bash
# 检查防火墙
firewall-cmd --list-ports
firewall-cmd --permanent --add-port=8501/tcp
firewall-cmd --reload
```

**❌ 应用无法启动**
```bash
# 查看日志
tail -f /var/log/gupiao.log

# 重启服务
supervisorctl restart gupiao
```

**❌ 依赖安装失败**
```bash
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

---

## 📞 技术支持

### 🔍 日志位置
- 应用日志：`/var/log/gupiao.log`
- Nginx日志：`/www/wwwlogs/gupiao.access.log`

### 📂 重要目录
- 项目目录：`/www/wwwroot/gupiao`
- 配置目录：`/www/wwwroot/gupiao/config`
- 虚拟环境：`/www/wwwroot/gupiao/venv`

### 🔧 配置文件
- Supervisor：`/etc/supervisor/conf.d/gupiao.conf`
- Nginx：宝塔面板 → 网站 → 配置

---

## 🎯 部署时间预估

- **环境检查**: 3分钟
- **文件上传**: 5分钟  
- **自动部署**: 10分钟
- **配置调试**: 5分钟
- **功能验证**: 2分钟

**总计: 约25分钟完成部署**

---

## ✅ 部署成功标志

当您能够：
1. 访问 `http://your-server-ip:8501`
2. 搜索"中石油"并看到相关结果
3. 查看股票风险评估数据
4. 系统运行稳定无错误

说明部署成功！🎉

---

**🏆 恭喜！您现在拥有了一个功能强大的股票分析系统！**

从原来的283只股票扩展到5,728只股票，增长了1924%，为您提供全市场的投资分析能力！
