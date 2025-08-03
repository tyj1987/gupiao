# 股票AI分析助手

一个专为新手股民设计的智能股票分析选择和交易辅助工具，提供实时数据处理和AI驱动的投资建议。

## 功能特性

### 📊 实时数据分析
- 实时股票行情数据获取
- 技术指标计算（MACD、KDJ、RSI等）
- 市场热点板块分析
- 资金流向监控

### 🤖 AI智能分析
- 基于机器学习的股票评分系统
- 智能选股推荐算法
- 风险评估和预警机制
- 个性化投资建议生成

### 📈 可视化界面
- 直观的K线图表展示
- 交互式数据面板
- 新手友好的操作界面
- 移动端适配支持

### 🔔 智能提醒
- 买卖点智能提醒
- 风险预警通知
- 市场异动实时提醒
- 个股关注列表管理

### ⚡ 自动交易
- 模拟交易环境
- 多种交易策略（保守型、平衡型、激进型）
- 风险控制机制
- 实盘交易接口（可扩展）

## 技术架构

### 后端技术栈
- **Python 3.8+**: 主要开发语言
- **FastAPI**: 高性能Web框架
- **Pandas**: 数据处理和分析
- **NumPy**: 数值计算
- **Scikit-learn**: 机器学习算法
- **TA-Lib**: 技术分析指标库
- **SQLite**: 本地数据存储

### 前端技术栈
- **Streamlit**: 快速Web应用开发
- **Plotly**: 交互式图表
- **Bootstrap**: 响应式UI组件

### 数据源
- **Tushare Pro**: 专业金融数据接口
- **AkShare**: 开源财经数据
- **YFinance**: 实时行情数据

## 快速开始

### 环境要求
- Python 3.8+
- pip 包管理器

### 安装步骤

1. **克隆项目**
```bash
git clone <项目地址>
cd gupiao
```

2. **安装依赖**
```bash
# 安装基础依赖
pip install -r requirements_minimal.txt

# 或安装完整依赖
pip install -r requirements.txt
```

3. **配置API密钥**
```bash
# 复制配置文件模板
cp config/api_keys.example.py config/api_keys.py

# 编辑配置文件，填入你的API密钥
nano config/api_keys.py
```

4. **快速体验**
```bash
# 运行简化演示程序
python simple_app.py
```

5. **启动Web界面**
```bash
# 方式1: 使用命令行工具
python main.py web

# 方式2: 直接启动Streamlit
python -m streamlit run src/ui/streamlit_app.py
```

## 使用指南

### 命令行工具

#### 分析单只股票
```bash
python main.py analyze --symbol 000001.SZ --period 1y
```

#### 智能选股
```bash
python main.py screen
```

#### 启动自动交易
```bash
# 模拟交易
python main.py trade --mode simulate --strategy conservative

# 实盘交易（谨慎使用）
python main.py trade --mode live --strategy balanced
```

### Web界面功能

1. **股票分析页面**
   - 输入股票代码进行分析
   - 查看K线图和技术指标
   - 获取AI投资建议

2. **智能选股页面**
   - 设置筛选条件
   - 获取推荐股票列表
   - 查看详细分析报告

3. **自动交易页面**
   - 配置交易策略
   - 监控交易状态
   - 查看收益统计

4. **市场概览页面**
   - 主要指数实时数据
   - 市场热点分析
   - 资金流向监控

5. **投资学堂页面**
   - 基础知识学习
   - 技术分析教程
   - 风险管理指南

## 交易策略说明

### 保守型策略
- **特点**: 风险较低，收益稳定
- **选股标准**: AI评分≥80分，低风险股票
- **止损止盈**: 止损5%，止盈15%
- **适合人群**: 风险厌恶型投资者

### 平衡型策略
- **特点**: 风险适中，收益平衡
- **选股标准**: AI评分≥70分，中低风险股票
- **止损止盈**: 止损10%，止盈20%
- **适合人群**: 普通投资者

### 激进型策略
- **特点**: 高风险高收益
- **选股标准**: AI评分≥65分，追求高成长
- **止损止盈**: 止损15%，止盈30%
- **适合人群**: 风险偏好型投资者

## 风险控制机制

### 仓位管理
- 单只股票最大仓位: 20%
- 最大持仓数量: 5只
- 现金保留比例: 10%

### 风险监控
- 实时监控持仓风险
- 行业集中度预警
- 流动性风险评估
- 市场整体风险分析

### 止损机制
- 个股止损: 根据策略设定
- 组合止损: 总亏损超过20%
- 时间止损: 持有超过预定期限

## 配置说明

### API配置 (config/api_keys.py)
```python
# Tushare Pro Token (获取地址: https://tushare.pro)
TUSHARE_TOKEN = "your_tushare_token_here"

# 其他API配置
AKSHARE_ENABLED = True
YFINANCE_ENABLED = True
```

### 系统配置 (config/config.py)
- 数据库配置
- 交易参数设置
- AI模型参数
- 风险控制参数

## 数据获取

### 支持的数据源
1. **Tushare Pro** (推荐)
   - 专业金融数据平台
   - 数据质量高，更新及时
   - 需要注册获取Token

2. **AkShare**
   - 开源免费数据
   - 覆盖面广
   - 无需注册

3. **YFinance**
   - 国际市场数据
   - 实时数据获取
   - 免费使用

### 数据类型
- 股票基本信息
- 历史价格数据
- 财务报表数据
- 实时行情数据
- 技术指标数据

## 注意事项

### ⚠️ 重要风险提示
1. **本系统仅供学习和研究使用**
2. **所有投资建议仅供参考，不构成投资建议**
3. **实盘交易请谨慎操作，投资有风险**
4. **建议先使用模拟交易熟悉系统**

### 💡 使用建议
1. **新手用户建议从投资学堂开始学习**
2. **使用模拟交易练习策略**
3. **小额资金开始实盘操作**
4. **定期关注系统更新和改进**

### 🔧 技术支持
- 遇到问题请查看日志文件 (logs/)
- 提交Issue获得技术支持
- 参与社区讨论和改进

## 开发说明

### 项目结构
```
gupiao/
├── config/              # 配置文件
├── src/                 # 源代码
│   ├── ai/             # AI分析模块
│   ├── data/           # 数据处理模块
│   ├── trading/        # 交易模块
│   └── ui/             # 用户界面
├── data/               # 数据存储
├── logs/               # 日志文件
├── main.py             # 主程序入口
├── simple_app.py       # 简化演示程序
└── requirements.txt    # 依赖列表
```

### 扩展开发
- 添加新的数据源
- 实现自定义交易策略
- 集成更多技术指标
- 开发移动端应用

## 更新日志

### v1.0.0 (2024-01-xx)
- 🎉 首次发布
- ✨ 股票分析功能
- ✨ 智能选股功能
- ✨ 自动交易功能
- ✨ Web界面
- ✨ 风险管理系统

## 许可证

本项目采用 MIT 许可证，详情请参见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进项目！

---

**免责声明**: 本软件仅用于教育和研究目的。使用本软件进行的任何投资决策都由用户自行承担风险。开发者不对使用本软件造成的任何损失负责。投资有风险，入市需谨慎！

## 快速开始

### 环境要求
- Python 3.8 或更高版本
- 8GB+ 内存推荐
- 稳定的网络连接

### 安装步骤

1. 克隆项目
```bash
git clone <repository-url>
cd gupiao
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置数据源
```bash
cp config/config.example.py config/config.py
# 编辑config.py，填入API密钥
```

5. 启动应用
```bash
streamlit run app.py
```

## 项目结构

```
gupiao/
├── app.py                 # 主应用入口
├── requirements.txt       # 依赖包列表
├── config/               # 配置文件
│   ├── config.py         # 主配置
│   └── api_keys.py       # API密钥配置
├── src/                  # 源代码
│   ├── data/             # 数据获取模块
│   ├── analysis/         # 分析算法模块
│   ├── ai/               # AI模型模块
│   ├── visualization/    # 可视化模块
│   └── utils/            # 工具函数
├── models/               # 训练好的模型
├── data/                 # 数据存储
└── tests/                # 测试文件
```

## 使用指南

### 新手入门
1. 打开应用后，首先设置关注的股票列表
2. 查看AI推荐的每日精选股票
3. 学习基础的技术指标含义
4. 根据风险偏好调整投资策略

### 高级功能
- 自定义选股策略
- 回测历史表现
- 组合优化建议
- 风险管理工具

## 免责声明

本工具仅供学习和研究使用，不构成投资建议。股市有风险，投资需谨慎。使用本工具进行投资决策的风险由用户自行承担。

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 联系方式

如有问题或建议，请通过Issue联系我们。