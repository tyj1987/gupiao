import os
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    """数据库配置"""
    sqlite_path: str = "data/stock_data.db"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = None

@dataclass
class APIConfig:
    """API配置"""
    # Tushare Pro配置
    tushare_token: str = os.getenv("TUSHARE_TOKEN", "")
    
    # 其他数据源配置
    akshare_enabled: bool = True
    yfinance_enabled: bool = True
    
    # API请求限制
    request_timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0

@dataclass
class AIConfig:
    """AI模型配置"""
    # 模型文件路径
    model_path: str = "models/"
    
    # 特征工程参数
    feature_window: int = 20  # 技术指标计算窗口
    prediction_days: int = 5   # 预测天数
    
    # 模型参数
    train_test_split: float = 0.8
    random_state: int = 42
    
    # 评分权重 (确保总和为1.0)
    technical_weight: float = 0.35
    fundamental_weight: float = 0.25
    sentiment_weight: float = 0.20
    ml_weight: float = 0.20  # 机器学习权重

@dataclass
class TradingConfig:
    """交易配置"""
    # 风险控制
    max_position_size: float = 0.1  # 单只股票最大仓位
    stop_loss_pct: float = 0.08     # 止损百分比
    take_profit_pct: float = 0.15   # 止盈百分比
    
    # 选股参数
    min_market_cap: float = 50e8    # 最小市值（元）
    max_pe_ratio: float = 50        # 最大市盈率
    min_volume_ratio: float = 1.2   # 最小量比
    
    # 交易时间
    market_open: str = "09:30"
    market_close: str = "15:00"
    lunch_start: str = "11:30"
    lunch_end: str = "13:00"

@dataclass
class UIConfig:
    """界面配置"""
    # Streamlit配置
    page_title: str = "股票AI分析助手"
    page_icon: str = "📈"
    layout: str = "wide"
    
    # 主题配置
    primary_color: str = "#FF6B6B"
    background_color: str = "#FFFFFF"
    secondary_background_color: str = "#F0F2F6"
    text_color: str = "#262730"
    
    # 图表配置
    chart_height: int = 500
    chart_width: int = 800
    
    # 刷新间隔（秒）
    auto_refresh_interval: int = 60

@dataclass
class LogConfig:
    """日志配置"""
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    log_rotation: str = "1 day"
    log_retention: str = "30 days"
    log_format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"

class Config:
    """主配置类"""
    
    def __init__(self):
        self.database = DatabaseConfig()
        self.api = APIConfig()
        self.ai = AIConfig()
        self.trading = TradingConfig()
        self.ui = UIConfig()
        self.log = LogConfig()
        
        # 创建必要的目录
        self._create_directories()
    
    def _create_directories(self):
        """创建必要的目录"""
        directories = [
            "data",
            "logs",
            "models",
            "cache",
            "exports"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @property
    def stock_codes(self) -> List[str]:
        """默认关注的股票代码"""
        return [
            "000001.SZ",  # 平安银行
            "000002.SZ",  # 万科A
            "600000.SH",  # 浦发银行
            "600036.SH",  # 招商银行
            "600519.SH",  # 贵州茅台
            "000858.SZ",  # 五粮液
            "002415.SZ",  # 海康威视
            "300059.SZ",  # 东方财富
        ]
    
    @property
    def technical_indicators(self) -> List[str]:
        """技术指标列表"""
        return [
            "SMA",    # 简单移动平均
            "EMA",    # 指数移动平均
            "MACD",   # MACD指标
            "RSI",    # 相对强弱指标
            "KDJ",    # 随机指标
            "BOLL",   # 布林带
            "CCI",    # 顺势指标
            "WR",     # 威廉指标
            "BIAS",   # 乖离率
            "ROC",    # 变动率指标
        ]
    
    @property
    def market_indices(self) -> Dict[str, str]:
        """市场指数代码"""
        return {
            "上证指数": "000001.SH",
            "深证成指": "399001.SZ",
            "创业板指": "399006.SZ",
            "科创50": "000688.SH",
            "沪深300": "000300.SH",
            "中证500": "000905.SH",
        }

# 全局配置实例
config = Config()

# 环境变量检查
def check_environment():
    """检查环境配置"""
    issues = []
    
    if not config.api.tushare_token:
        issues.append("未设置TUSHARE_TOKEN环境变量")
    
    return issues

if __name__ == "__main__":
    # 配置检查
    issues = check_environment()
    if issues:
        print("配置问题:")
        for issue in issues:
            print(f"- {issue}")
    else:
        print("配置检查通过")