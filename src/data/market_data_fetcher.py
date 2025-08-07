#!/usr/bin/env python3
"""
市场数据获取模块
"""

import requests
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from loguru import logger
import akshare as ak
import yfinance as yf

class MarketDataFetcher:
    """市场数据获取器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_market_indices(self) -> Dict[str, Dict]:
        """获取主要市场指数实时数据"""
        indices_data = {}
        
        try:
            # 获取A股指数
            a_share_indices = {
                '上证指数': '000001',
                '深证成指': '399001', 
                '创业板指': '399006',
                '科创50': '000688'
            }
            
            for name, code in a_share_indices.items():
                try:
                    # 使用akshare获取指数数据
                    df = ak.stock_zh_index_spot_em()
                    matching_rows = df[df['代码'] == code]
                    
                    if not matching_rows.empty:
                        row = matching_rows.iloc[0]
                        indices_data[name] = {
                            'current': float(row['最新价']),
                            'change': float(row['涨跌额']),
                            'change_pct': float(row['涨跌幅']),
                            'volume': float(row['成交量']) if row['成交量'] != '-' else 0,
                            'amount': float(row['成交额']) if row['成交额'] != '-' else 0
                        }
                    else:
                        # 模拟数据作为备选
                        indices_data[name] = self._generate_mock_index_data(name)
                        
                except Exception as e:
                    logger.warning(f"获取{name}数据失败: {e}")
                    indices_data[name] = self._generate_mock_index_data(name)
            
            # 获取美股指数 (通过yfinance)
            us_indices = {
                '纳斯达克': '^IXIC',
                '标普500': '^GSPC',
                '道琼斯': '^DJI'
            }
            
            for name, symbol in us_indices.items():
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="2d")
                    if not hist.empty:
                        current = hist['Close'].iloc[-1]
                        prev = hist['Close'].iloc[-2] if len(hist) > 1 else current
                        change = current - prev
                        change_pct = (change / prev * 100) if prev != 0 else 0
                        
                        indices_data[name] = {
                            'current': round(current, 2),
                            'change': round(change, 2),
                            'change_pct': round(change_pct, 2),
                            'volume': int(hist['Volume'].iloc[-1]) if 'Volume' in hist else 0,
                            'amount': 0
                        }
                    else:
                        indices_data[name] = self._generate_mock_index_data(name, is_us=True)
                        
                except Exception as e:
                    logger.warning(f"获取{name}数据失败: {e}")
                    indices_data[name] = self._generate_mock_index_data(name, is_us=True)
                    
        except Exception as e:
            logger.error(f"获取市场指数数据失败: {e}")
            # 返回模拟数据
            indices_data = {
                '上证指数': self._generate_mock_index_data('上证指数'),
                '深证成指': self._generate_mock_index_data('深证成指'),
                '创业板指': self._generate_mock_index_data('创业板指'),
                '科创50': self._generate_mock_index_data('科创50'),
                '纳斯达克': self._generate_mock_index_data('纳斯达克', is_us=True),
                '标普500': self._generate_mock_index_data('标普500', is_us=True),
                '道琼斯': self._generate_mock_index_data('道琼斯', is_us=True)
            }
        
        return indices_data
    
    def _generate_mock_index_data(self, name: str, is_us: bool = False) -> Dict:
        """生成模拟指数数据"""
        np.random.seed(hash(name) % 1000)  # 基于名称生成固定随机数
        
        if is_us:
            base_values = {
                '纳斯达克': 15000,
                '标普500': 4500,
                '道琼斯': 35000
            }
            base = base_values.get(name, 10000)
        else:
            base_values = {
                '上证指数': 3200,
                '深证成指': 12000,
                '创业板指': 2800,
                '科创50': 1200
            }
            base = base_values.get(name, 3000)
        
        change_pct = np.random.uniform(-2, 2)
        current = base * (1 + change_pct / 100)
        change = current - base
        
        return {
            'current': round(current, 2),
            'change': round(change, 2),
            'change_pct': round(change_pct, 2),
            'volume': np.random.randint(100000000, 500000000),
            'amount': np.random.randint(100000000000, 500000000000)
        }
    
    def get_hot_sectors(self) -> List[Dict]:
        """获取热门板块数据"""
        try:
            # 尝试获取板块数据
            df = ak.stock_board_industry_name_em()
            
            # 选取前几个活跃板块，转换为UI需要的格式
            hot_sectors = []
            for i in range(min(8, len(df))):
                row = df.iloc[i]
                
                # 解析涨跌幅数值
                change_pct = 0.0
                if pd.notna(row['涨跌幅']):
                    change_pct = float(row['涨跌幅'])
                
                # 解析成交额为亿元单位
                volume = 0.0
                if pd.notna(row['总市值']):
                    volume = float(row['总市值']) / 100000000  # 转换为亿元
                
                hot_sectors.append({
                    'name': row['板块名称'] if pd.notna(row['板块名称']) else "未知板块",
                    'change_pct': change_pct,
                    'volume': volume,
                    'leading_stock': row['领涨股票'] if pd.notna(row['领涨股票']) else "暂无数据"
                })
                
            return hot_sectors
            
        except Exception as e:
            logger.warning(f"获取热门板块数据失败: {e}")
            # 返回模拟数据，格式与UI匹配
            return [
                {"name": "人工智能", "change_pct": 3.45, "volume": 15.6, "leading_stock": "科大讯飞"},
                {"name": "新能源汽车", "change_pct": 2.18, "volume": 12.3, "leading_stock": "宁德时代"},
                {"name": "半导体", "change_pct": 1.89, "volume": 8.9, "leading_stock": "中芯国际"},
                {"name": "医药生物", "change_pct": -0.56, "volume": 5.2, "leading_stock": "恒瑞医药"},
                {"name": "白酒", "change_pct": 0.78, "volume": 7.1, "leading_stock": "贵州茅台"},
                {"name": "银行", "change_pct": 0.32, "volume": 4.8, "leading_stock": "招商银行"},
                {"name": "房地产", "change_pct": -1.23, "volume": 3.9, "leading_stock": "万科A"},
                {"name": "5G通信", "change_pct": 2.67, "volume": 6.4, "leading_stock": "中兴通讯"}
            ]
    
    def get_market_overview(self) -> Dict:
        """获取完整的市场概览数据"""
        return {
            'indices': self.get_market_indices(),
            'hot_sectors': self.get_hot_sectors(),
            'update_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

# 全局实例
market_data_fetcher = MarketDataFetcher()
