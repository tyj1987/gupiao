import tushare as ts
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Union
from loguru import logger
import time
import os

class TushareClient:
    """Tushare数据客户端"""
    
    def __init__(self, token: str = None):
        """
        初始化Tushare客户端
        
        Args:
            token: Tushare Pro API token
        """
        self.token = token or os.getenv('TUSHARE_TOKEN')
        if not self.token:
            raise ValueError("请设置Tushare token")
        
        # 设置token
        ts.set_token(self.token)
        self.pro = ts.pro_api()
        
        # 请求限制控制
        self.last_request_time = 0
        self.min_interval = 0.2  # 最小请求间隔（秒）
        
        logger.info("Tushare客户端初始化成功")
    
    def _rate_limit(self):
        """请求频率限制"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def get_stock_list(self, exchange: str = None) -> pd.DataFrame:
        """
        获取股票列表
        
        Args:
            exchange: 交易所代码 ('SSE', 'SZSE')
            
        Returns:
            股票列表DataFrame
        """
        try:
            self._rate_limit()
            
            if exchange:
                df = self.pro.stock_basic(exchange=exchange, list_status='L')
            else:
                df = self.pro.stock_basic(list_status='L')
            
            logger.info(f"获取股票列表成功，共{len(df)}只股票")
            return df
            
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return pd.DataFrame()
    
    def get_daily_data(self, 
                      ts_code: str, 
                      start_date: str = None, 
                      end_date: str = None,
                      adj: str = 'qfq') -> pd.DataFrame:
        """
        获取日线行情数据
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            adj: 复权类型 ('qfq'-前复权, 'hfq'-后复权, None-不复权)
            
        Returns:
            日线数据DataFrame
        """
        try:
            self._rate_limit()
            
            # 默认获取最近一年的数据
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
            
            df = self.pro.daily(ts_code=ts_code, 
                               start_date=start_date, 
                               end_date=end_date)
            
            if adj and not df.empty:
                # 获取复权数据
                adj_df = self.pro.adj_factor(ts_code=ts_code, 
                                           start_date=start_date, 
                                           end_date=end_date)
                
                if not adj_df.empty:
                    df = df.merge(adj_df[['trade_date', 'adj_factor']], 
                                 on='trade_date', how='left')
                    
                    if adj == 'qfq':  # 前复权
                        latest_factor = df['adj_factor'].iloc[0]
                        df['adj_factor'] = df['adj_factor'] / latest_factor
                    
                    # 应用复权因子
                    for col in ['open', 'high', 'low', 'close', 'pre_close']:
                        if col in df.columns:
                            df[col] = df[col] * df['adj_factor']
            
            # 按日期排序
            if not df.empty:
                df = df.sort_values('trade_date').reset_index(drop=True)
                df['trade_date'] = pd.to_datetime(df['trade_date'])
            
            logger.info(f"获取{ts_code}日线数据成功，共{len(df)}条记录")
            return df
            
        except Exception as e:
            logger.error(f"获取{ts_code}日线数据失败: {e}")
            return pd.DataFrame()
    
    def get_realtime_data(self, ts_codes: Union[str, List[str]]) -> pd.DataFrame:
        """
        获取实时行情数据
        
        Args:
            ts_codes: 股票代码或代码列表
            
        Returns:
            实时数据DataFrame
        """
        try:
            self._rate_limit()
            
            if isinstance(ts_codes, str):
                ts_codes = [ts_codes]
            
            # 分批获取，避免请求过大
            batch_size = 50
            all_data = []
            
            for i in range(0, len(ts_codes), batch_size):
                batch_codes = ts_codes[i:i + batch_size]
                codes_str = ','.join(batch_codes)
                
                df = self.pro.realtime_quote(ts_code=codes_str)
                if not df.empty:
                    all_data.append(df)
                
                if i + batch_size < len(ts_codes):
                    time.sleep(0.1)  # 批次间延迟
            
            if all_data:
                result = pd.concat(all_data, ignore_index=True)
                logger.info(f"获取实时数据成功，共{len(result)}只股票")
                return result
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"获取实时数据失败: {e}")
            return pd.DataFrame()
    
    def get_financial_data(self, 
                          ts_code: str, 
                          period: str = None,
                          report_type: str = '1') -> Dict[str, pd.DataFrame]:
        """
        获取财务数据
        
        Args:
            ts_code: 股票代码
            period: 报告期 (YYYYMMDD)
            report_type: 报告类型 ('1'-合并报表, '2'-单季合并, '3'-调整单季合并表)
            
        Returns:
            包含利润表、资产负债表、现金流量表的字典
        """
        try:
            financial_data = {}
            
            # 利润表
            self._rate_limit()
            income = self.pro.income(ts_code=ts_code, period=period, report_type=report_type)
            financial_data['income'] = income
            
            # 资产负债表
            self._rate_limit()
            balancesheet = self.pro.balancesheet(ts_code=ts_code, period=period, report_type=report_type)
            financial_data['balancesheet'] = balancesheet
            
            # 现金流量表
            self._rate_limit()
            cashflow = self.pro.cashflow(ts_code=ts_code, period=period, report_type=report_type)
            financial_data['cashflow'] = cashflow
            
            # 财务指标
            self._rate_limit()
            fina_indicator = self.pro.fina_indicator(ts_code=ts_code, period=period)
            financial_data['indicators'] = fina_indicator
            
            logger.info(f"获取{ts_code}财务数据成功")
            return financial_data
            
        except Exception as e:
            logger.error(f"获取{ts_code}财务数据失败: {e}")
            return {}
    
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
            self._rate_limit()
            
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
            
            df = self.pro.index_daily(ts_code=ts_code, 
                                     start_date=start_date, 
                                     end_date=end_date)
            
            if not df.empty:
                df = df.sort_values('trade_date').reset_index(drop=True)
                df['trade_date'] = pd.to_datetime(df['trade_date'])
            
            logger.info(f"获取{ts_code}指数数据成功，共{len(df)}条记录")
            return df
            
        except Exception as e:
            logger.error(f"获取{ts_code}指数数据失败: {e}")
            return pd.DataFrame()
    
    def get_trade_calendar(self, 
                          start_date: str = None, 
                          end_date: str = None) -> pd.DataFrame:
        """
        获取交易日历
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            交易日历DataFrame
        """
        try:
            self._rate_limit()
            
            if not start_date:
                start_date = datetime.now().strftime('%Y%m%d')
            if not end_date:
                end_date = (datetime.now() + timedelta(days=30)).strftime('%Y%m%d')
            
            df = self.pro.trade_cal(start_date=start_date, end_date=end_date)
            
            logger.info(f"获取交易日历成功，共{len(df)}条记录")
            return df
            
        except Exception as e:
            logger.error(f"获取交易日历失败: {e}")
            return pd.DataFrame()
    
    def get_concept_stocks(self, concept_name: str = None) -> pd.DataFrame:
        """
        获取概念股数据
        
        Args:
            concept_name: 概念名称
            
        Returns:
            概念股DataFrame
        """
        try:
            self._rate_limit()
            
            if concept_name:
                # 先获取概念分类
                concepts = self.pro.concept()
                concept_code = None
                
                for _, row in concepts.iterrows():
                    if concept_name in row['name']:
                        concept_code = row['code']
                        break
                
                if concept_code:
                    df = self.pro.concept_detail(id=concept_code)
                else:
                    df = pd.DataFrame()
            else:
                df = self.pro.concept()
            
            logger.info(f"获取概念股数据成功，共{len(df)}条记录")
            return df
            
        except Exception as e:
            logger.error(f"获取概念股数据失败: {e}")
            return pd.DataFrame()
    
    def is_trading_day(self, date: str = None) -> bool:
        """
        判断是否为交易日
        
        Args:
            date: 日期字符串 (YYYYMMDD)
            
        Returns:
            是否为交易日
        """
        try:
            if not date:
                date = datetime.now().strftime('%Y%m%d')
            
            calendar = self.get_trade_calendar(start_date=date, end_date=date)
            
            if not calendar.empty:
                return calendar.iloc[0]['is_open'] == 1
            
            return False
            
        except Exception as e:
            logger.error(f"判断交易日失败: {e}")
            return False