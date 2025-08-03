import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from loguru import logger

class YFinanceClient:
    """Yahoo Finance数据客户端"""
    
    def __init__(self):
        """
        初始化Yahoo Finance客户端
        """
        self.enabled = True
        logger.info("YFinance客户端初始化成功")
    
    def get_daily_data(self, 
                      symbol: str, 
                      start_date: Optional[str] = None, 
                      end_date: Optional[str] = None,
                      period: str = "1y") -> pd.DataFrame:
        """
        获取股票日线数据
        
        Args:
            symbol: 股票代码 (如 AAPL, TSLA, SPY等)
            start_date: 开始日期 (YYYY-MM-DD格式)
            end_date: 结束日期 (YYYY-MM-DD格式)
            period: 时间周期 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            包含OHLCV数据的DataFrame
        """
        try:
            # 创建Ticker对象
            ticker = yf.Ticker(symbol)
            
            # 获取历史数据
            if start_date and end_date:
                data = ticker.history(start=start_date, end=end_date)
            else:
                data = ticker.history(period=period)
            
            if data.empty:
                logger.warning(f"没有获取到{symbol}的数据")
                return pd.DataFrame()
            
            # 重命名列以保持一致性
            data = data.rename(columns={
                'Open': 'open',
                'High': 'high', 
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            
            # 添加日期列
            data.reset_index(inplace=True)
            data.rename(columns={'Date': 'date'}, inplace=True)
            
            # 确保日期格式正确
            data['date'] = pd.to_datetime(data['date'])
            
            # 删除不需要的列
            columns_to_keep = ['date', 'open', 'high', 'low', 'close', 'volume']
            data = data[[col for col in columns_to_keep if col in data.columns]]
            
            logger.info(f"获取{symbol}数据成功，共{len(data)}条记录")
            return data
            
        except Exception as e:
            logger.error(f"获取{symbol}日线数据失败: {e}")
            return pd.DataFrame()
    
    def get_intraday_data(self, 
                         symbol: str,
                         interval: str = "1m",
                         period: str = "1d") -> pd.DataFrame:
        """
        获取分钟线数据
        
        Args:
            symbol: 股票代码
            interval: 时间间隔 (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            period: 时间周期 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            包含OHLCV数据的DataFrame
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                logger.warning(f"没有获取到{symbol}的{interval}数据")
                return pd.DataFrame()
            
            # 重命名列
            data = data.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low', 
                'Close': 'close',
                'Volume': 'volume'
            })
            
            # 添加日期列
            data.reset_index(inplace=True)
            data.rename(columns={'Datetime': 'datetime'}, inplace=True)
            
            logger.info(f"获取{symbol} {interval}数据成功，共{len(data)}条记录")
            return data
            
        except Exception as e:
            logger.error(f"获取{symbol} {interval}数据失败: {e}")
            return pd.DataFrame()
    
    def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """
        获取股票基本信息
        
        Args:
            symbol: 股票代码
            
        Returns:
            股票信息字典
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # 提取主要信息
            stock_info = {
                'symbol': symbol,
                'name': info.get('longName', info.get('shortName', symbol)),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 0),
                'enterprise_value': info.get('enterpriseValue', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'forward_pe': info.get('forwardPE', 0),
                'peg_ratio': info.get('pegRatio', 0),
                'price_to_book': info.get('priceToBook', 0),
                'debt_to_equity': info.get('debtToEquity', 0),
                'return_on_equity': info.get('returnOnEquity', 0),
                'return_on_assets': info.get('returnOnAssets', 0),
                'gross_margins': info.get('grossMargins', 0),
                'operating_margins': info.get('operatingMargins', 0),
                'profit_margins': info.get('profitMargins', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'beta': info.get('beta', 0),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
                'recommendation': info.get('recommendationKey', 'hold'),
                'target_price': info.get('targetMeanPrice', 0)
            }
            
            logger.info(f"获取{symbol}基本信息成功")
            return stock_info
            
        except Exception as e:
            logger.error(f"获取{symbol}基本信息失败: {e}")
            return {}
    
    def get_financial_data(self, symbol: str) -> Dict[str, pd.DataFrame]:
        """
        获取财务报表数据
        
        Args:
            symbol: 股票代码
            
        Returns:
            包含各种财务报表的字典
        """
        try:
            ticker = yf.Ticker(symbol)
            
            financial_data = {}
            
            # 获取各种财务数据
            try:
                financial_data['income_statement'] = ticker.financials
                financial_data['balance_sheet'] = ticker.balance_sheet
                financial_data['cash_flow'] = ticker.cashflow
                financial_data['quarterly_income'] = ticker.quarterly_financials
                financial_data['quarterly_balance'] = ticker.quarterly_balance_sheet
                financial_data['quarterly_cashflow'] = ticker.quarterly_cashflow
            except:
                logger.warning(f"部分财务数据获取失败: {symbol}")
            
            logger.info(f"获取{symbol}财务数据成功")
            return financial_data
            
        except Exception as e:
            logger.error(f"获取{symbol}财务数据失败: {e}")
            return {}
    
    def get_dividends(self, symbol: str) -> pd.DataFrame:
        """
        获取股息数据
        
        Args:
            symbol: 股票代码
            
        Returns:
            股息数据DataFrame
        """
        try:
            ticker = yf.Ticker(symbol)
            dividends = ticker.dividends
            
            if dividends.empty:
                logger.warning(f"没有获取到{symbol}的股息数据")
                return pd.DataFrame()
            
            # 转换为DataFrame
            df = dividends.reset_index()
            df.columns = ['date', 'dividend']
            df['date'] = pd.to_datetime(df['date'])
            
            logger.info(f"获取{symbol}股息数据成功，共{len(df)}条记录")
            return df
            
        except Exception as e:
            logger.error(f"获取{symbol}股息数据失败: {e}")
            return pd.DataFrame()
    
    def get_splits(self, symbol: str) -> pd.DataFrame:
        """
        获取股票分割数据
        
        Args:
            symbol: 股票代码
            
        Returns:
            股票分割数据DataFrame
        """
        try:
            ticker = yf.Ticker(symbol)
            splits = ticker.splits
            
            if splits.empty:
                logger.warning(f"没有获取到{symbol}的分割数据")
                return pd.DataFrame()
            
            # 转换为DataFrame
            df = splits.reset_index()
            df.columns = ['date', 'split_ratio']
            df['date'] = pd.to_datetime(df['date'])
            
            logger.info(f"获取{symbol}分割数据成功，共{len(df)}条记录")
            return df
            
        except Exception as e:
            logger.error(f"获取{symbol}分割数据失败: {e}")
            return pd.DataFrame()
    
    def search_symbols(self, query: str) -> List[Dict[str, str]]:
        """
        搜索股票代码
        
        Args:
            query: 搜索关键词
            
        Returns:
            匹配的股票信息列表
        """
        try:
            # yfinance没有直接的搜索功能，这里提供一些常用的股票代码示例
            common_symbols = {
                'apple': ['AAPL', 'Apple Inc.'],
                'microsoft': ['MSFT', 'Microsoft Corporation'],
                'google': ['GOOGL', 'Alphabet Inc.'],
                'amazon': ['AMZN', 'Amazon.com Inc.'],
                'tesla': ['TSLA', 'Tesla Inc.'],
                'meta': ['META', 'Meta Platforms Inc.'],
                'nvidia': ['NVDA', 'NVIDIA Corporation'],
                'spotify': ['SPOT', 'Spotify Technology S.A.'],
                'netflix': ['NFLX', 'Netflix Inc.'],
                'coca': ['KO', 'The Coca-Cola Company'],
                'pepsi': ['PEP', 'PepsiCo Inc.'],
                'walmart': ['WMT', 'Walmart Inc.'],
                'disney': ['DIS', 'The Walt Disney Company'],
                'spx': ['SPY', 'SPDR S&P 500 ETF Trust'],
                'nasdaq': ['QQQ', 'Invesco QQQ Trust'],
                'dow': ['DIA', 'SPDR Dow Jones Industrial Average ETF']
            }
            
            query_lower = query.lower()
            results = []
            
            for key, (symbol, name) in common_symbols.items():
                if query_lower in key or query_lower in name.lower() or query_lower == symbol.lower():
                    results.append({
                        'symbol': symbol,
                        'name': name,
                        'exchange': 'US'
                    })
            
            # 如果没有找到匹配项，尝试直接使用输入作为股票代码
            if not results and len(query) <= 10:
                results.append({
                    'symbol': query.upper(),
                    'name': f'Unknown ({query.upper()})',
                    'exchange': 'US'
                })
            
            logger.info(f"搜索'{query}'找到{len(results)}个结果")
            return results
            
        except Exception as e:
            logger.error(f"搜索股票代码失败: {e}")
            return []
    
    def get_market_summary(self) -> Dict[str, Any]:
        """
        获取市场概况
        
        Returns:
            市场概况数据
        """
        try:
            # 获取主要指数
            indices = ['SPY', 'QQQ', 'DIA', 'VTI']  # S&P500, NASDAQ, DOW, Total Market
            summary = {}
            
            for index in indices:
                try:
                    ticker = yf.Ticker(index)
                    hist = ticker.history(period="2d")
                    if not hist.empty:
                        latest = hist.iloc[-1]
                        prev = hist.iloc[-2] if len(hist) > 1 else latest
                        
                        summary[index] = {
                            'price': float(latest['Close']),
                            'change': float(latest['Close'] - prev['Close']),
                            'change_percent': float((latest['Close'] - prev['Close']) / prev['Close'] * 100),
                            'volume': int(latest['Volume'])
                        }
                except Exception as e:
                    logger.warning(f"获取{index}数据失败: {e}")
            
            logger.info("获取市场概况成功")
            return summary
            
        except Exception as e:
            logger.error(f"获取市场概况失败: {e}")
            return {}
    
    def test_connection(self) -> bool:
        """
        测试连接
        
        Returns:
            连接是否正常
        """
        try:
            # 尝试获取SPY的简单数据来测试连接
            ticker = yf.Ticker("SPY")
            data = ticker.history(period="1d")
            
            if data.empty:
                logger.error("YFinance连接测试失败：无法获取数据")
                return False
            
            logger.info("YFinance连接测试成功")
            return True
            
        except Exception as e:
            logger.error(f"YFinance连接测试失败: {e}")
            return False
