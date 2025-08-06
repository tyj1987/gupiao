# 股票分析系统 - 项目总结

## 🎯 项目概述

股票分析系统是一个基于AI的智能股票分析工具，专为新手股民设计，提供全面的股票数据分析、技术指标计算和投资建议。

## ✨ 主要特性

### 📊 数据源支持
- **Tushare**: 专业的中国股票数据
- **AKShare**: 开源金融数据接口
- **Yahoo Finance**: 国际市场数据

### 🎨 界面特色
- **中国股市习惯**: 涨红跌绿的颜色显示
- **响应式设计**: 支持多设备访问
- **直观操作**: 简单易用的界面设计

### 🔍 分析功能
- **技术指标**: MA、MACD、RSI、布林带等
- **AI评分**: 智能投资建议和风险评估
- **实时数据**: 股价、成交量实时更新
- **多维分析**: 基本面+技术面综合分析

### 🚀 部署方式
- **传统部署**: 直接运行模式
- **Docker部署**: 容器化部署
- **面板集成**: 支持宝塔、1Panel等

## 📁 项目结构

```
gupiao/
├── src/                    # 源代码目录
│   ├── ui/                # 用户界面
│   │   └── streamlit_app.py
│   ├── data/              # 数据处理
│   │   ├── data_fetcher.py
│   │   ├── data_processor.py
│   │   └── clients/       # 数据源客户端
│   ├── ai/                # AI分析模块
│   │   └── stock_analyzer.py
│   └── trading/           # 交易模块
│       └── auto_trader.py
├── config/                # 配置文件
│   ├── config.py
│   └── api_keys.example.py
├── scripts/               # 部署脚本
│   ├── deploy.sh          # 智能部署脚本
│   ├── manage.sh          # 管理脚本
│   └── cleanup.sh         # 清理脚本
├── archive/               # 归档文件
├── .streamlit/           # Streamlit配置
├── requirements.txt      # Python依赖
├── Dockerfile           # Docker配置
├── docker-compose.yml   # Docker Compose配置
├── nginx.conf          # Nginx配置
└── start.sh           # 快速启动脚本
```

## 🛠️ 安装部署

### 快速启动

```bash
# 1. 克隆项目
git clone <repository-url>
cd gupiao

# 2. 智能部署
./scripts/deploy.sh

# 3. 快速启动
./start.sh
```

### 部署选项

#### 1. 自动部署
```bash
./scripts/deploy.sh                    # 自动选择最佳模式
./scripts/deploy.sh -m docker          # 强制使用Docker模式
./scripts/deploy.sh -m traditional     # 强制使用传统模式
```

#### 2. 管理命令
```bash
./scripts/manage.sh install            # 安装系统
./scripts/manage.sh start              # 启动服务
./scripts/manage.sh stop               # 停止服务
./scripts/manage.sh status             # 查看状态
./scripts/manage.sh logs               # 查看日志
./scripts/manage.sh health             # 健康检查
```

### 系统要求

#### 最低配置
- **CPU**: 1核心
- **内存**: 2GB
- **磁盘**: 5GB可用空间
- **Python**: 3.9+

#### 推荐配置
- **CPU**: 2核心+
- **内存**: 4GB+
- **磁盘**: 10GB+可用空间

### 支持系统

#### Linux发行版
- CentOS 7/8/9
- AlmaLinux 8/9
- Rocky Linux 8/9
- Ubuntu 18.04/20.04/22.04
- Debian 10/11/12

#### 服务器面板
- 宝塔面板 (BT Panel)
- 1Panel
- aaPanel
- 直接系统部署

## 🎨 界面更新

### 中国股市颜色习惯
- ✅ **涨幅显示**: 红色 (#ff4d4d)
- ✅ **跌幅显示**: 绿色 (#00cc00)
- ✅ **K线图**: 涨红跌绿
- ✅ **指标线**: 符合国内习惯

### 视觉改进
- 更直观的价格变化显示
- 清晰的涨跌箭头指示
- 统一的颜色主题风格

## 🧹 项目优化

### 文件清理
- ✅ 删除临时测试文件
- ✅ 清理Zone.Identifier文件
- ✅ 归档过期文档
- ✅ 清理Python缓存
- ✅ 更新.gitignore规则

### 结构优化
- ✅ 整理项目目录结构
- ✅ 分离核心代码和工具脚本
- ✅ 统一配置管理

## 🚀 部署脚本特性

### 智能检测
- ✅ 自动检测系统类型
- ✅ 自动检测服务器面板
- ✅ 智能选择部署模式
- ✅ 检查系统依赖

### 部署模式
- **传统模式**: 虚拟环境 + SystemD服务
- **Docker模式**: 容器化部署 + Nginx代理
- **面板模式**: 集成服务器面板配置

### 管理功能
- 一键安装部署
- 服务启停控制
- 日志查看监控
- 数据备份恢复
- 系统更新升级
- 健康状态检查

## 📊 使用说明

### 1. 首次配置
```bash
# 编辑API配置
cp config/api_keys.example.py config/api_keys.py
nano config/api_keys.py
```

### 2. 访问系统
- **本地访问**: http://localhost:8501
- **服务器访问**: http://your-server-ip:8501

### 3. 功能使用
1. **股票搜索**: 输入股票代码或名称
2. **查看分析**: 获取AI评分和投资建议
3. **技术分析**: 查看K线图和技术指标
4. **风险评估**: 了解投资风险等级

## 🛡️ 安全配置

### 防火墙设置
```bash
# CentOS/RHEL
firewall-cmd --add-port=8501/tcp --permanent
firewall-cmd --reload

# Ubuntu/Debian
ufw allow 8501
```

### 生产环境建议
- 使用Nginx反向代理
- 启用HTTPS证书
- 配置访问限制
- 定期备份数据

## 🔧 故障排除

### 常见问题

#### 1. 端口占用
```bash
# 查看端口使用情况
netstat -tlnp | grep 8501

# 杀死占用进程
pkill -f streamlit
```

#### 2. 依赖问题
```bash
# 重新安装依赖
pip install -r requirements.txt --upgrade

# Docker重建
docker-compose build --no-cache
```

#### 3. 服务无法启动
```bash
# 查看详细日志
./scripts/manage.sh logs

# 健康检查
./scripts/manage.sh health
```

### 日志位置
- **传统模式**: `journalctl -u stock-analysis`
- **Docker模式**: `docker-compose logs`

## 📞 支持联系

如有问题请通过以下方式联系：
- GitHub Issues
- 项目文档
- 技术支持

## 📄 许可证

本项目基于MIT许可证开源。

---

**版本**: 2.1.0  
**更新时间**: 2025年8月7日  
**维护状态**: 积极维护中
