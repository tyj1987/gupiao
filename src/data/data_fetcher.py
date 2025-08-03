import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from loguru import logger
import asyncio
import concurrent.futures
from functools import lru_cache

from .tushare_client import TushareClient
from .akshare_client import AkshareClient
from .data_processor import DataProcessor
from config.config import config

try:
    from .yfinance_client import YFinanceClient
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    logger.warning("YFinance不可用，国际股票数据功能将被禁用")

class DataFetcher:
    """统一数据获取器"""
    
    def __init__(self, use_cache: bool = True):
        """
        初始化数据获取器
        
        Args:
            use_cache: 是否使用缓存
        """
        self.use_cache = use_cache
        self.processor = DataProcessor()
        
        # 初始化数据源客户端
        self.tushare_client = None
        self.akshare_client = None
        self.yfinance_client = None
        
        try:
            if config.api.tushare_token:
                self.tushare_client = TushareClient(config.api.tushare_token)
                logger.info("Tushare客户端初始化成功")
        except Exception as e:
            logger.warning(f"Tushare客户端初始化失败: {e}")
        
        try:
            if config.api.akshare_enabled:
                self.akshare_client = AkshareClient()
                logger.info("AkShare客户端初始化成功")
        except Exception as e:
            logger.warning(f"AkShare客户端初始化失败: {e}")
        
        try:
            if YFINANCE_AVAILABLE:
                self.yfinance_client = YFinanceClient()
                logger.info("YFinance客户端初始化成功")
        except Exception as e:
            logger.warning(f"YFinance客户端初始化失败: {e}")
        
        if not self.tushare_client and not self.akshare_client and not self.yfinance_client:
            raise RuntimeError("没有可用的数据源")
        
        logger.info("数据获取器初始化完成")
    
    def _detect_market(self, symbol: str) -> str:
        """
        检测股票代码属于哪个市场
        
        Args:
            symbol: 股票代码
            
        Returns:
            市场类型: 'CN' (中国), 'US' (美国), 'UNKNOWN'
        """
        symbol = symbol.upper().strip()
        
        # 中国股票代码特征
        if '.' in symbol:
            if symbol.endswith('.SH') or symbol.endswith('.SZ'):
                return 'CN'
        else:
            # 纯数字代码，通常是中国股票
            if symbol.isdigit() and len(symbol) == 6:
                return 'CN'
        
        # 美国股票代码特征 (字母代码)
        if symbol.isalpha() and 1 <= len(symbol) <= 5:
            return 'US'
        
        # 其他常见模式
        if symbol in ['SPY', 'QQQ', 'DIA', 'VTI', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']:
            return 'US'
        
        return 'UNKNOWN'
    
    def get_stock_list(self, exchange: str = None) -> pd.DataFrame:
        """
        获取股票列表
        
        Args:
            exchange: 交易所代码
            
        Returns:
            股票列表DataFrame
        """
        try:
            # 优先使用Tushare
            if self.tushare_client:
                df = self.tushare_client.get_stock_list(exchange)
                if not df.empty:
                    return self.processor.clean_data(df)
            
            # 备用AkShare
            if self.akshare_client:
                df = self.akshare_client.get_stock_list()
                if not df.empty:
                    if exchange:
                        df = df[df['exchange'] == exchange.upper()]
                    return self.processor.clean_data(df)
            
            logger.error("所有数据源获取股票列表失败")
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return pd.DataFrame()
    
    def get_stock_data(self, 
                      symbol: str,
                      period: str = "1y",
                      adj: str = 'qfq',
                      with_indicators: bool = True) -> pd.DataFrame:
        """
        获取股票数据的统一接口
        
        Args:
            symbol: 股票代码 (支持中国和美国股票)
            period: 数据周期 (1d, 5d, 1m, 3m, 6m, 1y, 2y, 5y, 10y, ytd, max)
            adj: 复权类型 (qfq前复权, hfq后复权, None不复权)
            with_indicators: 是否计算技术指标
            
        Returns:
            股票数据DataFrame
        """
        try:
            # 检测市场类型
            market = self._detect_market(symbol)
            
            if market == 'US' and self.yfinance_client:
                # 美国股票使用yfinance
                logger.info(f"使用YFinance获取美国股票{symbol}数据")
                return self._get_us_stock_data(symbol, period, with_indicators)
            
            elif market == 'CN':
                # 中国股票使用现有逻辑
                logger.info(f"使用中国数据源获取股票{symbol}数据")
                return self._get_cn_stock_data(symbol, period, adj, with_indicators)
            
            else:
                logger.warning(f"无法识别股票{symbol}的市场类型，尝试使用所有可用数据源")
                
                # 先尝试中国数据源
                if market != 'US':
                    data = self._get_cn_stock_data(symbol, period, adj, with_indicators)
                    if not data.empty:
                        return data
                
                # 再尝试美国数据源
                if self.yfinance_client:
                    data = self._get_us_stock_data(symbol, period, with_indicators)
                    if not data.empty:
                        return data
                
                logger.error(f"无法获取股票{symbol}的数据")
                return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"获取股票{symbol}数据失败: {e}")
            return pd.DataFrame()
    
    def _get_us_stock_data(self, 
                          symbol: str, 
                          period: str = "1y",
                          with_indicators: bool = True) -> pd.DataFrame:
        """
        获取美国股票数据
        
        Args:
            symbol: 美国股票代码
            period: 时间周期
            with_indicators: 是否计算技术指标
            
        Returns:
            股票数据DataFrame
        """
        try:
            if not self.yfinance_client:
                logger.error("YFinance客户端不可用")
                return pd.DataFrame()
            
            # 获取数据
            df = self.yfinance_client.get_daily_data(symbol=symbol, period=period)
            
            if df.empty:
                logger.warning(f"没有获取到{symbol}的数据")
                return pd.DataFrame()
            
            # 数据清洗和处理
            df = self.processor.clean_data(df)
            
            # 计算技术指标
            if with_indicators and not df.empty:
                df = self.processor.calculate_technical_indicators(df)
            
            return df
            
        except Exception as e:
            logger.error(f"获取美国股票{symbol}数据失败: {e}")
            return pd.DataFrame()
    
    def _get_cn_stock_data(self, 
                          symbol: str,
                          period: str = "1y", 
                          adj: str = 'qfq',
                          with_indicators: bool = True) -> pd.DataFrame:
        """
        获取中国股票数据 (原有逻辑)
        
        Args:
            symbol: 中国股票代码
            period: 数据周期
            adj: 复权类型
            with_indicators: 是否计算技术指标
            
        Returns:
            股票数据DataFrame
        """
        try:
            # 转换period为日期范围
            end_date = datetime.now().strftime('%Y-%m-%d')
            
            period_mapping = {
                '1d': 1,
                '5d': 5, 
                '1m': 30,
                '3m': 90,
                '6m': 180,
                '1y': 365,
                '2y': 730,
                '5y': 1825,
                '10y': 3650,
                'ytd': None,  # 年初至今
                'max': None   # 所有数据
            }
            
            if period == 'ytd':
                start_date = datetime.now().replace(month=1, day=1).strftime('%Y-%m-%d')
            elif period == 'max':
                start_date = '1990-01-01'  # 足够早的日期
            else:
                days = period_mapping.get(period, 365)
                start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            # 处理股票代码格式
            ts_code = symbol
            if '.' not in symbol:
                # 简单的代码格式转换逻辑
                if symbol.startswith('00') or symbol.startswith('30'):
                    ts_code = f"{symbol}.SZ"  # 深圳
                elif symbol.startswith('60'):
                    ts_code = f"{symbol}.SH"  # 上海
                else:
                    # 尝试自动检测，默认添加.SH
                    ts_code = f"{symbol}.SH"
            
            logger.info(f"获取股票{ts_code}数据，周期：{period}({start_date} 到 {end_date})")
            
            # 调用已有的get_daily_data方法
            return self.get_daily_data(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                adj=adj,
                with_indicators=with_indicators
            )
            
        except Exception as e:
            logger.error(f"获取股票{symbol}数据失败: {e}")
            return pd.DataFrame()
    
    def get_daily_data(self, 
                      ts_code: str, 
                      start_date: str = None, 
                      end_date: str = None,
                      adj: str = 'qfq',
                      with_indicators: bool = True) -> pd.DataFrame:
        """
        获取日线数据
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            adj: 复权类型
            with_indicators: 是否计算技术指标
            
        Returns:
            日线数据DataFrame
        """
        try:
            df = pd.DataFrame()
            
            # 优先使用Tushare
            if self.tushare_client:
                df = self.tushare_client.get_daily_data(ts_code, start_date, end_date, adj)
            
            # 如果Tushare失败，使用AkShare
            if df.empty and self.akshare_client:
                # 转换日期格式
                ak_start = start_date.replace('-', '') if start_date else None
                ak_end = end_date.replace('-', '') if end_date else None
                
                # 转换复权类型
                ak_adj = adj if adj in ['qfq', 'hfq'] else ''
                
                df = self.akshare_client.get_daily_data(
                    ts_code.split('.')[0], 
                    ak_start, 
                    ak_end, 
                    ak_adj
                )
            
            if not df.empty:
                # 数据清洗
                df = self.processor.clean_data(df)
                
                # 计算技术指标
                if with_indicators:
                    df = self.processor.calculate_technical_indicators(df)
                    df = self.processor.create_features(df)
                    df = self.processor.detect_patterns(df)
            
            return df
            
        except Exception as e:
            logger.error(f"获取{ts_code}日线数据失败: {e}")
            return pd.DataFrame()
    
    def get_realtime_data(self, ts_codes: Union[str, List[str]]) -> pd.DataFrame:
        """
        获取实时数据
        
        Args:
            ts_codes: 股票代码或代码列表
            
        Returns:
            实时数据DataFrame
        """
        try:
            df = pd.DataFrame()
            
            # 优先使用Tushare
            if self.tushare_client:
                df = self.tushare_client.get_realtime_data(ts_codes)
            
            # 如果Tushare失败，使用AkShare
            if df.empty and self.akshare_client:
                df = self.akshare_client.get_realtime_data(ts_codes)
            
            if not df.empty:
                df = self.processor.clean_data(df)
            
            return df
            
        except Exception as e:
            logger.error(f"获取实时数据失败: {e}")
            return pd.DataFrame()
    
    def get_index_data(self, 
                      ts_code: str, 
                      start_date: str = None, 
                      end_date: str = None) -> pd.DataFrame:
        """
        获取指数数据
        
        Args:
            ts_code: 指数代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            指数数据DataFrame
        """
        try:
            df = pd.DataFrame()
            
            # 优先使用Tushare
            if self.tushare_client:
                df = self.tushare_client.get_index_data(ts_code, start_date, end_date)
            
            # 如果Tushare失败，使用AkShare
            if df.empty and self.akshare_client:
                df = self.akshare_client.get_index_data(ts_code, start_date, end_date)
            
            if not df.empty:
                df = self.processor.clean_data(df)
                df = self.processor.calculate_technical_indicators(df)
            
            return df
            
        except Exception as e:
            logger.error(f"获取{ts_code}指数数据失败: {e}")
            return pd.DataFrame()
    
    def get_financial_data(self, ts_code: str) -> Dict[str, pd.DataFrame]:
        """
        获取财务数据
        
        Args:
            ts_code: 股票代码
            
        Returns:
            财务数据字典
        """
        try:
            if self.tushare_client:
                return self.tushare_client.get_financial_data(ts_code)
            else:
                logger.warning("财务数据需要Tushare Pro支持")
                return {}
                
        except Exception as e:
            logger.error(f"获取{ts_code}财务数据失败: {e}")
            return {}
    
    def get_market_overview(self) -> Dict[str, pd.DataFrame]:
        """
        获取市场概览数据
        
        Returns:
            市场概览数据字典
        """
        try:
            overview = {}
            
            # 获取主要指数数据
            for name, code in config.market_indices.items():
                index_data = self.get_index_data(code)
                if not index_data.empty:
                    overview[name] = index_data.tail(1)
            
            # 获取热门股票
            if self.akshare_client:
                hot_stocks = self.akshare_client.get_hot_stocks()
                if not hot_stocks.empty:
                    overview['热门股票'] = hot_stocks
            
            # 获取概念板块
            if self.akshare_client:
                concepts = self.akshare_client.get_concept_stocks()
                if not concepts.empty:
                    overview['概念板块'] = concepts.head(20)
            
            # 获取行业板块
            if self.akshare_client:
                industries = self.akshare_client.get_industry_stocks()
                if not industries.empty:
                    overview['行业板块'] = industries.head(20)
            
            return overview
            
        except Exception as e:
            logger.error(f"获取市场概览失败: {e}")
            return {}
    
    def get_stock_analysis(self, ts_code: str) -> Dict[str, any]:
        """
        获取股票综合分析数据
        
        Args:
            ts_code: 股票代码
            
        Returns:
            综合分析数据字典
        """
        try:
            analysis = {
                'basic_info': {},
                'price_data': pd.DataFrame(),
                'financial_data': {},
                'technical_analysis': {},
                'news': pd.DataFrame()
            }
            
            # 获取基本信息
            stock_list = self.get_stock_list()
            if not stock_list.empty:
                stock_info = stock_list[stock_list['ts_code'] == ts_code]
                if not stock_info.empty:
                    analysis['basic_info'] = stock_info.iloc[0].to_dict()
            
            # 获取价格数据（最近一年）
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            price_data = self.get_daily_data(ts_code, start_date=start_date)
            analysis['price_data'] = price_data
            
            # 获取财务数据
            financial_data = self.get_financial_data(ts_code)
            analysis['financial_data'] = financial_data
            
            # 技术分析
            if not price_data.empty:
                latest_data = price_data.iloc[-1]
                
                # 支撑阻力位
                support_resistance = self.processor.calculate_support_resistance(price_data)
                
                analysis['technical_analysis'] = {
                    'latest_price': latest_data.get('close', 0),
                    'ma5': latest_data.get('ma5', 0),
                    'ma20': latest_data.get('ma20', 0),
                    'rsi': latest_data.get('rsi6', 0),
                    'macd': latest_data.get('macd', 0),
                    'support': support_resistance.get('support'),
                    'resistance': support_resistance.get('resistance'),
                    'trend': '上涨' if latest_data.get('ma5', 0) > latest_data.get('ma20', 0) else '下跌'
                }
            
            # 获取新闻（如果支持）
            if self.akshare_client:
                try:
                    news = self.akshare_client.get_news(ts_code, limit=10)
                    analysis['news'] = news
                except:
                    pass
            
            return analysis
            
        except Exception as e:
            logger.error(f"获取{ts_code}综合分析失败: {e}")
            return {}
    
    def get_batch_data(self, 
                      ts_codes: List[str], 
                      data_type: str = 'realtime',
                      max_workers: int = 5) -> Dict[str, pd.DataFrame]:
        """
        批量获取数据
        
        Args:
            ts_codes: 股票代码列表
            data_type: 数据类型 ('realtime', 'daily', 'analysis')
            max_workers: 最大并发数
            
        Returns:
            批量数据字典
        """
        try:
            results = {}
            
            if data_type == 'realtime':
                # 实时数据可以批量获取
                df = self.get_realtime_data(ts_codes)
                for code in ts_codes:
                    stock_data = df[df['ts_code'] == code.split('.')[0]] if not df.empty else pd.DataFrame()
                    results[code] = stock_data
            
            else:
                # 其他数据类型使用并发获取
                with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                    if data_type == 'daily':
                        future_to_code = {
                            executor.submit(self.get_daily_data, code): code 
                            for code in ts_codes
                        }
                    elif data_type == 'analysis':
                        future_to_code = {
                            executor.submit(self.get_stock_analysis, code): code 
                            for code in ts_codes
                        }
                    
                    for future in concurrent.futures.as_completed(future_to_code):
                        code = future_to_code[future]
                        try:
                            results[code] = future.result()
                        except Exception as e:
                            logger.error(f"获取{code}数据失败: {e}")
                            results[code] = pd.DataFrame() if data_type == 'daily' else {}
            
            return results
            
        except Exception as e:
            logger.error(f"批量获取数据失败: {e}")
            return {}
    
    @lru_cache(maxsize=100)
    def is_trading_day(self, date: str = None) -> bool:
        """
        判断是否为交易日（带缓存）
        
        Args:
            date: 日期字符串
            
        Returns:
            是否为交易日
        """
        try:
            if self.tushare_client:
                return self.tushare_client.is_trading_day(date)
            else:
                # 简单判断：周一到周五
                if not date:
                    check_date = datetime.now()
                else:
                    check_date = datetime.strptime(date, '%Y%m%d')
                
                return check_date.weekday() < 5
                
        except Exception as e:
            logger.error(f"判断交易日失败: {e}")
            return False
    
    def get_market_status(self) -> Dict[str, any]:
        """
        获取市场状态
        
        Returns:
            市场状态字典
        """
        try:
            now = datetime.now()
            today = now.strftime('%Y%m%d')
            
            status = {
                'is_trading_day': self.is_trading_day(today),
                'current_time': now.strftime('%H:%M:%S'),
                'market_status': 'closed'
            }
            
            # 判断市场开盘状态
            if status['is_trading_day']:
                current_time = now.time()
                market_open = datetime.strptime(config.trading.market_open, '%H:%M').time()
                lunch_start = datetime.strptime(config.trading.lunch_start, '%H:%M').time()
                lunch_end = datetime.strptime(config.trading.lunch_end, '%H:%M').time()
                market_close = datetime.strptime(config.trading.market_close, '%H:%M').time()
                
                if market_open <= current_time < lunch_start:
                    status['market_status'] = 'morning_trading'
                elif lunch_start <= current_time < lunch_end:
                    status['market_status'] = 'lunch_break'
                elif lunch_end <= current_time < market_close:
                    status['market_status'] = 'afternoon_trading'
                else:
                    status['market_status'] = 'closed'
            
            return status
            
        except Exception as e:
            logger.error(f"获取市场状态失败: {e}")
            return {'market_status': 'unknown'}
    
    def get_international_stock_info(self, symbol: str) -> Dict:
        """
        获取国际股票基本信息
        
        Args:
            symbol: 股票代码
            
        Returns:
            股票基本信息字典
        """
        try:
            if not self.yfinance_client:
                logger.error("YFinance客户端不可用")
                return {}
            
            info = self.yfinance_client.get_stock_info(symbol)
            logger.info(f"获取{symbol}基本信息成功")
            return info
            
        except Exception as e:
            logger.error(f"获取{symbol}基本信息失败: {e}")
            return {}
    
    def search_international_stocks(self, query: str) -> List[Dict]:
        """
        搜索国际股票
        
        Args:
            query: 搜索关键词
            
        Returns:
            匹配的股票列表
        """
        try:
            if not self.yfinance_client:
                logger.error("YFinance客户端不可用")
                return []
            
            results = self.yfinance_client.search_symbols(query)
            logger.info(f"搜索'{query}'找到{len(results)}个国际股票")
            return results
            
        except Exception as e:
            logger.error(f"搜索国际股票失败: {e}")
            return []
    
    def get_market_summary(self) -> Dict:
        """
        获取市场概况 (包括国际市场)
        
        Returns:
            市场概况数据
        """
        try:
            summary = {}
            
            # 获取中国市场概况
            if self.akshare_client:
                try:
                    # 这里可以添加中国市场指数数据
                    pass
                except Exception as e:
                    logger.warning(f"获取中国市场概况失败: {e}")
            
            # 获取美国市场概况
            if self.yfinance_client:
                try:
                    us_summary = self.yfinance_client.get_market_summary()
                    summary.update(us_summary)
                except Exception as e:
                    logger.warning(f"获取美国市场概况失败: {e}")
            
            logger.info("获取市场概况成功")
            return summary
            
        except Exception as e:
            logger.error(f"获取市场概况失败: {e}")
            return {}
    
    def test_data_sources(self) -> Dict[str, bool]:
        """
        测试所有数据源连接
        
        Returns:
            各数据源的连接状态
        """
        status = {}
        
        # 测试Tushare
        if self.tushare_client:
            try:
                status['tushare'] = self.tushare_client.test_connection()
            except:
                status['tushare'] = False
        else:
            status['tushare'] = False
        
        # 测试AkShare
        if self.akshare_client:
            try:
                status['akshare'] = self.akshare_client.test_connection()
            except:
                status['akshare'] = False
        else:
            status['akshare'] = False
        
        # 测试YFinance
        if self.yfinance_client:
            try:
                status['yfinance'] = self.yfinance_client.test_connection()
            except:
                status['yfinance'] = False
        else:
            status['yfinance'] = False
        
        logger.info(f"数据源连接测试结果: {status}")
        return status