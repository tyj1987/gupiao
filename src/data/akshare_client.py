import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Union
from loguru import logger
import time

class AkshareClient:
    """AkShare数据客户端"""
    
    def __init__(self):
        """
        初始化AkShare客户端
        """
        # 请求限制控制
        self.last_request_time = 0
        self.min_interval = 0.5  # 最小请求间隔（秒）
        
        logger.info("AkShare客户端初始化成功")
    
    def _rate_limit(self):
        """请求频率限制"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def get_stock_list(self) -> pd.DataFrame:
        """
        获取股票列表
        
        Returns:
            股票列表DataFrame
        """
        try:
            self._rate_limit()
            
            # 获取A股股票列表
            df = ak.stock_info_a_code_name()
            
            if not df.empty:
                # 统一列名
                df.columns = ['ts_code', 'name']
                # 添加交易所信息
                df['exchange'] = df['ts_code'].apply(
                    lambda x: 'SH' if x.startswith(('60', '68', '90')) else 'SZ'
                )
                # 格式化代码
                df['ts_code'] = df['ts_code'] + '.' + df['exchange']
            
            logger.info(f"获取股票列表成功，共{len(df)}只股票")
            return df
            
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return pd.DataFrame()
    
    def get_daily_data(self, 
                      symbol: str, 
                      start_date: str = None, 
                      end_date: str = None,
                      adjust: str = 'qfq') -> pd.DataFrame:
        """
        获取日线行情数据
        
        Args:
            symbol: 股票代码 (不带后缀)
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            adjust: 复权类型 ('qfq'-前复权, 'hfq'-后复权, ''不复权)
            
        Returns:
            日线数据DataFrame
        """
        try:
            self._rate_limit()
            
            # 默认获取最近一年的数据
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            # 移除后缀
            if '.' in symbol:
                symbol = symbol.split('.')[0]
            
            df = ak.stock_zh_a_hist(symbol=symbol, 
                                   period="daily", 
                                   start_date=start_date.replace('-', ''), 
                                   end_date=end_date.replace('-', ''), 
                                   adjust=adjust)
            
            if not df.empty:
                # 统一列名
                column_mapping = {
                    '日期': 'trade_date',
                    '开盘': 'open',
                    '收盘': 'close', 
                    '最高': 'high',
                    '最低': 'low',
                    '成交量': 'vol',
                    '成交额': 'amount',
                    '振幅': 'pct_chg',
                    '涨跌幅': 'change',
                    '涨跌额': 'change_amount',
                    '换手率': 'turnover_rate'
                }
                
                df = df.rename(columns=column_mapping)
                
                # 确保日期格式
                df['trade_date'] = pd.to_datetime(df['trade_date'])
                
                # 添加股票代码
                df['ts_code'] = symbol
                
                # 按日期排序
                df = df.sort_values('trade_date').reset_index(drop=True)
            
            logger.info(f"获取{symbol}日线数据成功，共{len(df)}条记录")
            return df
            
        except Exception as e:
            logger.error(f"获取{symbol}日线数据失败: {e}")
            return pd.DataFrame()
    
    def get_realtime_data(self, symbols: Union[str, List[str]]) -> pd.DataFrame:
        """
        获取实时行情数据
        
        Args:
            symbols: 股票代码或代码列表
            
        Returns:
            实时数据DataFrame
        """
        try:
            self._rate_limit()
            
            # 获取实时行情
            df = ak.stock_zh_a_spot_em()
            
            if not df.empty and symbols:
                if isinstance(symbols, str):
                    symbols = [symbols]
                
                # 移除后缀并过滤
                clean_symbols = [s.split('.')[0] if '.' in s else s for s in symbols]
                df = df[df['代码'].isin(clean_symbols)]
                
                # 统一列名
                column_mapping = {
                    '代码': 'ts_code',
                    '名称': 'name',
                    '最新价': 'price',
                    '涨跌幅': 'pct_chg',
                    '涨跌额': 'change',
                    '成交量': 'vol',
                    '成交额': 'amount',
                    '振幅': 'amplitude',
                    '最高': 'high',
                    '最低': 'low',
                    '今开': 'open',
                    '昨收': 'pre_close',
                    '量比': 'volume_ratio',
                    '换手率': 'turnover_rate',
                    '市盈率-动态': 'pe_ttm',
                    '市净率': 'pb'
                }
                
                df = df.rename(columns=column_mapping)
                
                # 添加时间戳
                df['update_time'] = datetime.now()
            
            logger.info(f"获取实时数据成功，共{len(df)}只股票")
            return df
            
        except Exception as e:
            logger.error(f"获取实时数据失败: {e}")
            return pd.DataFrame()
    
    def get_index_data(self, 
                      symbol: str, 
                      start_date: str = None, 
                      end_date: str = None) -> pd.DataFrame:
        """
        获取指数数据
        
        Args:
            symbol: 指数代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            指数数据DataFrame
        """
        try:
            self._rate_limit()
            
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
            
            # 指数代码映射
            index_mapping = {
                '000001.SH': 'sh000001',  # 上证指数
                '399001.SZ': 'sz399001',  # 深证成指
                '399006.SZ': 'sz399006',  # 创业板指
                '000300.SH': 'sh000300',  # 沪深300
                '000905.SH': 'sh000905',  # 中证500
            }
            
            ak_symbol = index_mapping.get(symbol, symbol)
            
            df = ak.stock_zh_index_daily(symbol=ak_symbol)
            
            if not df.empty:
                # 过滤日期范围
                df['date'] = pd.to_datetime(df['date'])
                start_dt = pd.to_datetime(start_date)
                end_dt = pd.to_datetime(end_date)
                df = df[(df['date'] >= start_dt) & (df['date'] <= end_dt)]
                
                # 统一列名
                df = df.rename(columns={
                    'date': 'trade_date',
                    'volume': 'vol'
                })
                
                df['ts_code'] = symbol
                df = df.sort_values('trade_date').reset_index(drop=True)
            
            logger.info(f"获取{symbol}指数数据成功，共{len(df)}条记录")
            return df
            
        except Exception as e:
            logger.error(f"获取{symbol}指数数据失败: {e}")
            return pd.DataFrame()
    
    def get_hot_stocks(self, market: str = 'all') -> pd.DataFrame:
        """
        获取热门股票
        
        Args:
            market: 市场类型 ('all', 'sh', 'sz')
            
        Returns:
            热门股票DataFrame
        """
        try:
            self._rate_limit()
            
            # 获取涨幅榜
            df_up = ak.stock_zh_a_spot_em()
            
            if not df_up.empty:
                # 按涨跌幅排序
                df_up = df_up.sort_values('涨跌幅', ascending=False)
                
                # 过滤市场
                if market == 'sh':
                    df_up = df_up[df_up['代码'].str.startswith(('60', '68', '90'))]
                elif market == 'sz':
                    df_up = df_up[df_up['代码'].str.startswith(('00', '30'))]
                
                # 取前50只
                df_up = df_up.head(50)
                
                # 统一列名
                column_mapping = {
                    '代码': 'ts_code',
                    '名称': 'name',
                    '最新价': 'price',
                    '涨跌幅': 'pct_chg',
                    '涨跌额': 'change',
                    '成交量': 'vol',
                    '成交额': 'amount',
                    '换手率': 'turnover_rate'
                }
                
                df_up = df_up.rename(columns=column_mapping)
            
            logger.info(f"获取热门股票成功，共{len(df_up)}只股票")
            return df_up
            
        except Exception as e:
            logger.error(f"获取热门股票失败: {e}")
            return pd.DataFrame()
    
    def get_concept_stocks(self) -> pd.DataFrame:
        """
        获取概念板块数据
        
        Returns:
            概念板块DataFrame
        """
        try:
            self._rate_limit()
            
            df = ak.stock_board_concept_name_em()
            
            if not df.empty:
                # 统一列名
                column_mapping = {
                    '板块名称': 'concept_name',
                    '板块代码': 'concept_code',
                    '最新价': 'price',
                    '涨跌幅': 'pct_chg',
                    '涨跌额': 'change',
                    '总市值': 'market_cap',
                    '换手率': 'turnover_rate',
                    '上涨家数': 'up_count',
                    '下跌家数': 'down_count',
                    '领涨股票': 'leading_stock',
                    '领涨股票涨跌幅': 'leading_pct_chg'
                }
                
                df = df.rename(columns=column_mapping)
            
            logger.info(f"获取概念板块数据成功，共{len(df)}个概念")
            return df
            
        except Exception as e:
            logger.error(f"获取概念板块数据失败: {e}")
            return pd.DataFrame()
    
    def get_industry_stocks(self) -> pd.DataFrame:
        """
        获取行业板块数据
        
        Returns:
            行业板块DataFrame
        """
        try:
            self._rate_limit()
            
            df = ak.stock_board_industry_name_em()
            
            if not df.empty:
                # 统一列名
                column_mapping = {
                    '板块名称': 'industry_name',
                    '板块代码': 'industry_code',
                    '最新价': 'price',
                    '涨跌幅': 'pct_chg',
                    '涨跌额': 'change',
                    '总市值': 'market_cap',
                    '换手率': 'turnover_rate',
                    '上涨家数': 'up_count',
                    '下跌家数': 'down_count',
                    '领涨股票': 'leading_stock',
                    '领涨股票涨跌幅': 'leading_pct_chg'
                }
                
                df = df.rename(columns=column_mapping)
            
            logger.info(f"获取行业板块数据成功，共{len(df)}个行业")
            return df
            
        except Exception as e:
            logger.error(f"获取行业板块数据失败: {e}")
            return pd.DataFrame()
    
    def get_news(self, symbol: str = None, limit: int = 20) -> pd.DataFrame:
        """
        获取股票新闻
        
        Args:
            symbol: 股票代码
            limit: 新闻数量限制
            
        Returns:
            新闻DataFrame
        """
        try:
            self._rate_limit()
            
            if symbol:
                # 移除后缀
                if '.' in symbol:
                    symbol = symbol.split('.')[0]
                
                df = ak.stock_news_em(symbol=symbol)
            else:
                # 获取市场新闻
                df = ak.stock_news_em()
            
            if not df.empty and limit:
                df = df.head(limit)
                
                # 统一列名
                if '新闻标题' in df.columns:
                    df = df.rename(columns={
                        '新闻标题': 'title',
                        '新闻内容': 'content',
                        '发布时间': 'publish_time',
                        '新闻来源': 'source'
                    })
            
            logger.info(f"获取新闻成功，共{len(df)}条")
            return df
            
        except Exception as e:
            logger.error(f"获取新闻失败: {e}")
            return pd.DataFrame()