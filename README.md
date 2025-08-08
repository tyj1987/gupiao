# 📈 股票AI分析系统

基于AI驱动的智能股票分析平台，提供实时数据分析、技术指标计算、风险评估和自动交易策略。

## ✨ 主要特性

- 🔍 **智能股票搜索**: 支持股票代码、名称、简称的模糊搜索
- 📊 **AI综合评分**: 多维度智能评估股票投资价值
- 🎯 **智能选股**: AI驱动的股票筛选和推荐系统
- ⚡ **自动交易**: 支持保守型、平衡型、激进型三种策略
- 📈 **技术分析**: MA、RSI、MACD等技术指标分析
- 🛡️ **风险控制**: 智能止损止盈和仓位管理
- 📱 **响应式设计**: 支持移动端和桌面端访问

## 🚀 快速开始

### 1. 环境要求

- Python 3.9+
- Docker (可选)

### 2. 安装部署

#### 方式一: 直接运行
```bash
# 克隆项目
git clone https://github.com/tyj1987/gupiao.git
cd gupiao

# 安装依赖
pip install -r requirements_minimal_fixed.txt

# 配置API密钥
cp config/api_keys.example.py config/api_keys.py
# 编辑 config/api_keys.py 添加您的API密钥

# 启动应用
streamlit run src/ui/streamlit_app.py
```

#### 方式二: Docker部署
```bash
# 拉取镜像
docker pull tuoyongjun1987/gupiao-stock-analysis:latest

# 运行容器
docker run -d \
  --name gupiao-app \
  --restart unless-stopped \
  -p 8501:8501 \
  tuoyongjun1987/gupiao-stock-analysis:latest
```

### 3. 访问应用

- 本地访问: http://localhost:8501
- 测试环境: http://ddns.52trz.com:8501
- 生产环境: http://47.94.225.76:8501

## 📁 项目结构

```
gupiao/
├── src/                    # 源代码
│   ├── ui/                # 用户界面
│   │   ├── streamlit_app.py      # 主应用
│   │   └── smart_stock_input.py  # 智能搜索组件
│   ├── data/              # 数据处理
│   │   ├── data_fetcher.py       # 数据获取
│   │   ├── stock_mapper.py       # 股票映射
│   │   └── clients/              # 数据源客户端
│   ├── ai/                # AI分析模块
│   │   └── stock_analyzer.py     # 智能分析器
│   └── trading/           # 交易模块
│       ├── auto_trader.py        # 自动交易
│       └── watchlist_manager.py  # 自选股管理
├── config/                # 配置文件
│   ├── config.py          # 主配置
│   └── api_keys.example.py      # API密钥示例
├── .streamlit/            # Streamlit配置
├── scripts/               # 工具脚本
│   └── clean-project.sh   # 项目清理脚本
├── requirements_minimal_fixed.txt  # 精简依赖
├── Dockerfile             # Docker配置
└── README.md              # 项目说明
```

## 🎯 核心功能

### 📊 股票分析
- 实时股价数据获取
- 技术指标计算和可视化
- 基本面数据分析
- AI评分和投资建议

### 🔍 智能搜索
- 支持股票代码搜索 (如: 000001, 600519.SH)
- 支持公司名称搜索 (如: 平安银行, 贵州茅台)
- 支持简称模糊搜索 (如: 中行, 工行, 茅台)
- 热门股票快速选择

### ⚡ 自动交易
- **保守型策略**: 低风险稳健收益 (止损5-8%, 止盈10-15%)
- **平衡型策略**: 风险收益平衡 (止损8-12%, 止盈15-25%)
- **激进型策略**: 高风险高收益 (止损10-15%, 止盈20-30%)

### 🛡️ 风险管理
- 智能止损止盈
- 仓位控制和分散投资
- 实时风险监控
- 最大回撤控制

## 🔧 配置说明

### API配置
在 `config/api_keys.py` 中配置数据源API密钥:

```python
# Tushare API
TUSHARE_TOKEN = "your_tushare_token"

# Alpha Vantage API
ALPHA_VANTAGE_API_KEY = "your_alpha_vantage_key"

# 其他API配置...
```

### 环境变量
```bash
# 应用端口
STREAMLIT_SERVER_PORT=8501

# 数据源配置
TUSHARE_TOKEN=your_token
ALPHA_VANTAGE_API_KEY=your_key
```

## 📊 数据源

- **Tushare**: 中国A股专业数据
- **Yahoo Finance**: 全球股票数据
- **AKShare**: 开源金融数据

## 🌟 Docker镜像优化

本项目采用多阶段构建和精简依赖，镜像大小控制在合理范围内:

- 基础镜像: `python:3.9-slim`
- 只安装必要的系统依赖
- 使用 `.dockerignore` 排除不必要文件
- 清理构建缓存和临时文件

## 🔄 CI/CD流程

项目采用GitHub Actions实现自动化部署:

1. **代码检查**: 依赖检查、语法检查
2. **项目清理**: 自动清理临时文件和缓存
3. **镜像构建**: 自动构建和推送Docker镜像
4. **自动部署**: 部署到测试和生产环境
5. **健康检查**: 自动验证部署状态

## ⚠️ 免责声明

本系统仅供学习和研究使用，不构成投资建议。股市有风险，投资需谨慎。使用自动交易功能请务必先进行充分的模拟测试。

## 📝 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎提交Issue和Pull Request来帮助改进项目。

## 📞 联系方式

- 作者: tyj1987
- 邮箱: tuoyongjun1987@qq.com
- GitHub: https://github.com/tyj1987/gupiao
