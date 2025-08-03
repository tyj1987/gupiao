#!/usr/bin/env python3
"""
全市场股票获取器
动态获取所有A股、港股、美股股票信息
"""

import akshare as ak
import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional, Tuple
from loguru import logger
import time
import requests
from datetime import datetime, timedelta
import json
import os

class UniversalStockFetcher:
    """全市场股票获取器"""
    
    def __init__(self):
        self.cache_dir = "/tmp/stock_cache"
        self.cache_file = os.path.join(self.cache_dir, "all_stocks_cache.json")
        self.last_update_file = os.path.join(self.cache_dir, "last_update.txt")
        
        # 创建缓存目录
        os.makedirs(self.cache_dir, exist_ok=True)
        
        self.a_stock_cache = None
        self.us_stock_cache = None
        self.hk_stock_cache = None
        self.last_update = None
        
    def _is_cache_valid(self, hours: int = 24) -> bool:
        """检查缓存是否有效（默认24小时过期）"""
        try:
            if os.path.exists(self.last_update_file):
                with open(self.last_update_file, 'r') as f:
                    last_update_str = f.read().strip()
                    last_update = datetime.fromisoformat(last_update_str)
                    return datetime.now() - last_update < timedelta(hours=hours)
        except Exception as e:
            logger.warning(f"检查缓存有效性失败: {e}")
        return False
    
    def _save_cache(self, all_stocks: Dict[str, str]):
        """保存股票缓存"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(all_stocks, f, ensure_ascii=False, indent=2)
            
            with open(self.last_update_file, 'w') as f:
                f.write(datetime.now().isoformat())
                
            logger.info(f"股票缓存已保存: {len(all_stocks)} 只股票")
        except Exception as e:
            logger.error(f"保存缓存失败: {e}")
    
    def _load_cache(self) -> Optional[Dict[str, str]]:
        """加载股票缓存"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    all_stocks = json.load(f)
                logger.info(f"从缓存加载 {len(all_stocks)} 只股票")
                return all_stocks
        except Exception as e:
            logger.error(f"加载缓存失败: {e}")
        return None
    
    def get_all_a_stocks(self, force_refresh: bool = False) -> Dict[str, str]:
        """获取所有A股股票列表"""
        if self.a_stock_cache is None or force_refresh:
            try:
                logger.info("正在获取A股股票列表...")
                
                a_stocks = {}
                
                # 方法1: 使用akshare获取实时A股列表
                try:
                    stock_list = ak.stock_zh_a_spot_em()
                    logger.info(f"从东方财富获取到 {len(stock_list)} 只A股")
                    
                    for _, row in stock_list.iterrows():
                        code = str(row['代码'])
                        name = str(row['名称'])
                        
                        # 确定交易所后缀
                        if code.startswith(('000', '001', '002', '003', '300')):
                            full_code = f"{code}.SZ"
                        elif code.startswith(('600', '601', '603', '605', '688', '689')):
                            full_code = f"{code}.SH"
                        elif code.startswith(('400', '420', '430', '831', '832', '833', '834', '835', '836', '837', '838', '839')):
                            # 新三板暂时跳过
                            continue
                        else:
                            # 其他代码也加入，使用原代码
                            full_code = code
                            
                        a_stocks[full_code] = name
                
                except Exception as e:
                    logger.warning(f"使用东方财富接口获取A股数据失败: {e}")
                
                # 方法2: 使用备用接口
                if len(a_stocks) < 1000:  # 如果获取的股票太少，尝试备用方法
                    try:
                        # 获取沪深股票基本信息
                        stock_info_sh = ak.stock_info_sh_name_code()  # 上海
                        stock_info_sz = ak.stock_info_sz_name_code()  # 深圳
                        
                        # 处理上海股票
                        for _, row in stock_info_sh.iterrows():
                            code = f"{row['证券代码']}.SH"
                            name = row['证券简称']
                            a_stocks[code] = name
                        
                        # 处理深圳股票
                        for _, row in stock_info_sz.iterrows():
                            code = f"{row['证券代码']}.SZ"
                            name = row['证券简称']
                            a_stocks[code] = name
                            
                        logger.info(f"使用备用接口获取到额外 {len(stock_info_sh) + len(stock_info_sz)} 只股票")
                    
                    except Exception as e:
                        logger.warning(f"使用备用接口获取A股数据失败: {e}")
                
                # 方法3: 获取各个板块的股票
                try:
                    # 获取沪深300成分股
                    hs300 = ak.index_stock_cons(symbol="000300")
                    for _, row in hs300.iterrows():
                        code = f"{row['品种代码']}.{'SH' if row['品种代码'].startswith(('600', '601', '603', '605', '688')) else 'SZ'}"
                        name = row['品种名称']
                        a_stocks[code] = name
                    
                    # 获取中证500成分股
                    zz500 = ak.index_stock_cons(symbol="000905")
                    for _, row in zz500.iterrows():
                        code = f"{row['品种代码']}.{'SH' if row['品种代码'].startswith(('600', '601', '603', '605', '688')) else 'SZ'}"
                        name = row['品种名称']
                        a_stocks[code] = name
                        
                    logger.info("成功获取指数成分股")
                        
                except Exception as e:
                    logger.warning(f"获取指数成分股失败: {e}")
                
                self.a_stock_cache = a_stocks
                logger.info(f"成功获取 {len(a_stocks)} 只A股股票")
                
            except Exception as e:
                logger.error(f"获取A股股票列表失败: {e}")
                return {}
                
        return self.a_stock_cache or {}
    
    def get_all_hk_stocks(self, force_refresh: bool = False) -> Dict[str, str]:
        """获取港股股票列表"""
        if self.hk_stock_cache is None or force_refresh:
            try:
                logger.info("正在获取港股股票列表...")
                
                hk_stocks = {}
                
                # 获取港股主要股票
                try:
                    # 获取恒生指数成分股
                    hsi_stocks = ak.index_stock_cons_hk(symbol="HSI")
                    for _, row in hsi_stocks.iterrows():
                        code = f"{row['成分券代码'].zfill(5)}.HK"
                        name = row['成分券名称']
                        hk_stocks[code] = name
                    
                    logger.info(f"获取恒生指数成分股 {len(hsi_stocks)} 只")
                    
                except Exception as e:
                    logger.warning(f"获取恒生指数成分股失败: {e}")
                
                # 添加一些知名港股
                famous_hk_stocks = {
                    "00700.HK": "腾讯控股",
                    "09988.HK": "阿里巴巴-SW",
                    "03690.HK": "美团-W",
                    "01024.HK": "快手-W",
                    "00175.HK": "吉利汽车",
                    "02318.HK": "中国平安",
                    "01398.HK": "工商银行",
                    "03968.HK": "招商银行",
                    "01299.HK": "友邦保险",
                    "00386.HK": "中国石油化工股份",
                    "00857.HK": "中国石油股份",
                    "01093.HK": "石药集团",
                    "00992.HK": "联想集团",
                    "01810.HK": "小米集团-W",
                    "02269.HK": "药明生物",
                    "06098.HK": "碧桂园服务",
                    "01997.HK": "九龙仓置业",
                    "00388.HK": "香港交易所",
                    "00005.HK": "汇丰控股",
                    "00941.HK": "中国移动"
                }
                
                hk_stocks.update(famous_hk_stocks)
                
                self.hk_stock_cache = hk_stocks
                logger.info(f"成功获取 {len(hk_stocks)} 只港股股票")
                
            except Exception as e:
                logger.error(f"获取港股股票列表失败: {e}")
                return {}
                
        return self.hk_stock_cache or {}
    
    def get_all_us_stocks(self, force_refresh: bool = False) -> Dict[str, str]:
        """获取主要美股股票列表"""
        if self.us_stock_cache is None or force_refresh:
            try:
                logger.info("正在获取美股股票列表...")
                
                us_stocks = {}
                
                # 主要美股股票列表
                major_us_stocks = {
                    # 科技股
                    'AAPL': 'Apple Inc.',
                    'MSFT': 'Microsoft Corporation', 
                    'GOOGL': 'Alphabet Inc.',
                    'GOOG': 'Alphabet Inc. Class A',
                    'AMZN': 'Amazon.com Inc.',
                    'TSLA': 'Tesla Inc.',
                    'META': 'Meta Platforms Inc.',
                    'NVDA': 'NVIDIA Corporation',
                    'NFLX': 'Netflix Inc.',
                    'ADBE': 'Adobe Inc.',
                    'CRM': 'Salesforce Inc.',
                    'ORCL': 'Oracle Corporation',
                    'INTC': 'Intel Corporation',
                    'AMD': 'Advanced Micro Devices Inc.',
                    'IBM': 'International Business Machines Corp.',
                    'CSCO': 'Cisco Systems Inc.',
                    'UBER': 'Uber Technologies Inc.',
                    'LYFT': 'Lyft Inc.',
                    'SNOW': 'Snowflake Inc.',
                    'ZM': 'Zoom Video Communications Inc.',
                    'TWTR': 'Twitter Inc.',
                    'SNAP': 'Snap Inc.',
                    'SQ': 'Square Inc.',
                    'PYPL': 'PayPal Holdings Inc.',
                    'SHOP': 'Shopify Inc.',
                    
                    # 金融股
                    'JPM': 'JPMorgan Chase & Co.',
                    'BAC': 'Bank of America Corp.',
                    'WFC': 'Wells Fargo & Co.',
                    'GS': 'Goldman Sachs Group Inc.',
                    'MS': 'Morgan Stanley',
                    'C': 'Citigroup Inc.',
                    'AXP': 'American Express Co.',
                    'V': 'Visa Inc.',
                    'MA': 'Mastercard Inc.',
                    'BRK.A': 'Berkshire Hathaway Inc.',
                    'BRK.B': 'Berkshire Hathaway Inc.',
                    
                    # 医药生物
                    'JNJ': 'Johnson & Johnson',
                    'PFE': 'Pfizer Inc.',
                    'UNH': 'UnitedHealth Group Inc.',
                    'MRK': 'Merck & Co. Inc.',
                    'ABT': 'Abbott Laboratories',
                    'TMO': 'Thermo Fisher Scientific Inc.',
                    'DHR': 'Danaher Corporation',
                    'BMY': 'Bristol-Myers Squibb Co.',
                    'AMGN': 'Amgen Inc.',
                    'GILD': 'Gilead Sciences Inc.',
                    'MRNA': 'Moderna Inc.',
                    'BNTX': 'BioNTech SE',
                    'REGN': 'Regeneron Pharmaceuticals Inc.',
                    'VRTX': 'Vertex Pharmaceuticals Inc.',
                    'BIIB': 'Biogen Inc.',
                    
                    # 消费股
                    'AMZN': 'Amazon.com Inc.',
                    'WMT': 'Walmart Inc.',
                    'HD': 'Home Depot Inc.',
                    'PG': 'Procter & Gamble Co.',
                    'KO': 'Coca-Cola Co.',
                    'PEP': 'PepsiCo Inc.',
                    'MCD': 'McDonald\'s Corp.',
                    'SBUX': 'Starbucks Corporation',
                    'NKE': 'Nike Inc.',
                    'DIS': 'Walt Disney Co.',
                    'COST': 'Costco Wholesale Corp.',
                    'TGT': 'Target Corporation',
                    'LOW': 'Lowe\'s Companies Inc.',
                    
                    # 工业股
                    'BA': 'Boeing Co.',
                    'CAT': 'Caterpillar Inc.',
                    'GE': 'General Electric Co.',
                    'MMM': '3M Co.',
                    'HON': 'Honeywell International Inc.',
                    'UPS': 'United Parcel Service Inc.',
                    'FDX': 'FedEx Corporation',
                    'LMT': 'Lockheed Martin Corp.',
                    'RTX': 'Raytheon Technologies Corp.',
                    'NOC': 'Northrop Grumman Corp.',
                    
                    # 能源股
                    'XOM': 'Exxon Mobil Corporation',
                    'CVX': 'Chevron Corporation',
                    'COP': 'ConocoPhillips',
                    'SLB': 'Schlumberger NV',
                    'EOG': 'EOG Resources Inc.',
                    'KMI': 'Kinder Morgan Inc.',
                    'OXY': 'Occidental Petroleum Corp.',
                    'MPC': 'Marathon Petroleum Corp.',
                    'PSX': 'Phillips 66',
                    'VLO': 'Valero Energy Corp.',
                    
                    # 电动车
                    'TSLA': 'Tesla Inc.',
                    'NIO': 'NIO Inc.',
                    'XPEV': 'XPeng Inc.',
                    'LI': 'Li Auto Inc.',
                    'RIVN': 'Rivian Automotive Inc.',
                    'LCID': 'Lucid Group Inc.',
                    'F': 'Ford Motor Co.',
                    'GM': 'General Motors Co.',
                    
                    # 中概股
                    'BABA': 'Alibaba Group Holding Ltd.',
                    'JD': 'JD.com Inc.',
                    'PDD': 'PDD Holdings Inc.',
                    'BIDU': 'Baidu Inc.',
                    'NTES': 'NetEase Inc.',
                    'TCEHY': 'Tencent Holdings Ltd.',
                    'TME': 'Tencent Music Entertainment Group',
                    'IQ': 'iQIYI Inc.',
                    'BILI': 'Bilibili Inc.',
                    'DIDI': 'DiDi Global Inc.',
                    'EDU': 'New Oriental Education & Technology Group Inc.',
                    'TAL': 'TAL Education Group',
                    'YMM': 'Full Truck Alliance Co. Ltd.',
                    'DOYU': 'DouYu International Holdings Ltd.',
                    'HUYA': 'HUYA Inc.',
                    'WB': 'Weibo Corporation',
                    'SINA': 'SINA Corporation',
                    'SOHU': 'Sohu.com Inc.',
                    'VIPS': 'Vipshop Holdings Ltd.',
                    'ATHM': 'Autohome Inc.',
                    'BZUN': 'Baozun Inc.',
                    'KC': 'Kingsoft Cloud Holdings Ltd.',
                    'TIGR': 'UP Fintech Holding Ltd.',
                    'FUTU': 'Futu Holdings Ltd.',
                    'GOTU': 'Gaotu Techedu Inc.',
                    'RLX': 'RLX Technology Inc.',
                    'DADA': 'Dada Nexus Ltd.',
                    'TUYA': 'Tuya Inc.',
                    'NIU': 'Niu Technologies',
                    'LX': 'LexinFintech Holdings Ltd.',
                    'FINV': 'FinVolution Group',
                    'QTT': 'Qutoutiao Inc.',
                    'MOMO': 'Hello Group Inc.',
                    'YY': 'JOYY Inc.',
                    'LIVE': 'Live Ventures Inc.',
                    'GDS': 'GDS Holdings Ltd.',
                    'VNET': '21Vianet Group Inc.',
                    'CAAS': 'China Automotive Systems Inc.',
                    'CBAT': 'CBAK Energy Technology Inc.',
                    'CAN': 'Canaan Inc.',
                    'DQ': 'Daqo New Energy Corp.',
                    'GOTU': 'Gaotu Techedu Inc.',
                    'HTHT': 'H World Group Ltd.',
                    'JOBS': '51job Inc.',
                    'KNTK': 'Kiniksa Pharmaceuticals Ltd.',
                    'LABU': 'Direxion Daily S&P Biotech Bull 3X Shares',
                    'MNSO': 'MINISO Group Holding Ltd.',
                    'ONEW': 'OneWater Marine Inc.',
                    'PAGS': 'PagSeguro Digital Ltd.',
                    'QS': 'QuantumScape Corp.',
                    'RUN': 'Sunrun Inc.',
                    'SPCE': 'Virgin Galactic Holdings Inc.',
                    'TKAT': 'Takung Art Co. Ltd.',
                    'WDH': 'Waterdrop Inc.',
                    'XNET': 'Xunlei Ltd.',
                    'YI': '111 Inc.',
                    'ZKIN': 'ZK International Group Co. Ltd.'
                }
                
                us_stocks.update(major_us_stocks)
                
                self.us_stock_cache = us_stocks
                logger.info(f"成功获取 {len(us_stocks)} 只美股股票")
                
            except Exception as e:
                logger.error(f"获取美股股票列表失败: {e}")
                return {}
                
        return self.us_stock_cache or {}
    
    def get_all_stocks(self, force_refresh: bool = False) -> Dict[str, str]:
        """获取所有市场的股票"""
        # 检查缓存
        if not force_refresh and self._is_cache_valid():
            cached_stocks = self._load_cache()
            if cached_stocks:
                return cached_stocks
        
        logger.info("开始获取全市场股票信息...")
        
        all_stocks = {}
        
        # 获取A股
        a_stocks = self.get_all_a_stocks(force_refresh)
        all_stocks.update(a_stocks)
        logger.info(f"已添加 {len(a_stocks)} 只A股")
        
        # 获取港股
        hk_stocks = self.get_all_hk_stocks(force_refresh)
        all_stocks.update(hk_stocks)
        logger.info(f"已添加 {len(hk_stocks)} 只港股")
        
        # 获取美股
        us_stocks = self.get_all_us_stocks(force_refresh)
        all_stocks.update(us_stocks)
        logger.info(f"已添加 {len(us_stocks)} 只美股")
        
        logger.info(f"总计获取 {len(all_stocks)} 只股票")
        
        # 保存缓存
        self._save_cache(all_stocks)
        
        return all_stocks
    
    def search_stocks(self, query: str, limit: int = 20) -> List[Dict[str, str]]:
        """在全市场股票中搜索"""
        all_stocks = self.get_all_stocks()
        
        query_original = query.strip()
        query = query.upper().strip()
        results = []
        
        if not query:
            return results
        
        # 搜索别名映射
        search_aliases = {
            '中石油': '中国石油',
            '中石化': '中国石化',
            '工行': '工商银行',
            '建行': '建设银行',
            '招行': '招商银行',
            '中行': '中国银行',
            '茅台': '贵州茅台',
            '五粮': '五粮液',
            '腾讯': '腾讯控股',
            '阿里': '阿里巴巴',
            '苹果': 'Apple',
            '微软': 'Microsoft',
            '谷歌': 'Google',
            '特斯拉': 'Tesla',
            '英伟达': 'NVIDIA'
        }
        
        # 检查别名
        search_term = query_original
        for alias, full_name in search_aliases.items():
            if alias in query_original:
                search_term = full_name
                break
        
        for symbol, name in all_stocks.items():
            match_score = 0
            match_type = 'none'
            
            # 1. 精确代码匹配
            if query == symbol.upper():
                match_score = 100
                match_type = 'exact_code'
            # 2. 代码部分匹配
            elif query in symbol.upper():
                match_score = 90
                match_type = 'code'
            # 3. 精确名称匹配
            elif search_term == name:
                match_score = 85
                match_type = 'exact_name'
            # 4. 名称部分匹配
            elif search_term in name or query in name:
                match_score = 80
                match_type = 'name'
            # 5. 模糊匹配
            elif any(word in name for word in search_term.split() if len(word) > 1):
                match_score = 70
                match_type = 'fuzzy'
            
            if match_score > 0:
                # 确定市场类型
                if symbol.endswith('.SH') or symbol.endswith('.SZ'):
                    market = '上海A股' if symbol.endswith('.SH') else '深圳A股'
                elif symbol.endswith('.HK'):
                    market = '香港H股'
                else:
                    market = '美股'
                
                results.append({
                    'symbol': symbol,
                    'name': name,
                    'match_type': match_type,
                    'market': market,
                    'score': match_score
                })
        
        # 按匹配分数排序
        results.sort(key=lambda x: (-x['score'], x['symbol']))
        
        # 返回结果时移除score字段
        final_results = []
        for r in results[:limit]:
            final_results.append({
                'symbol': r['symbol'],
                'name': r['name'],
                'match_type': r['match_type'],
                'market': r['market']
            })
        
        return final_results
    
    def get_market_statistics(self) -> Dict[str, int]:
        """获取各市场股票数量统计"""
        all_stocks = self.get_all_stocks()
        
        stats = {
            'total': len(all_stocks),
            'a_stock_sh': 0,
            'a_stock_sz': 0, 
            'hk_stock': 0,
            'us_stock': 0
        }
        
        for symbol in all_stocks.keys():
            if symbol.endswith('.SH'):
                stats['a_stock_sh'] += 1
            elif symbol.endswith('.SZ'):
                stats['a_stock_sz'] += 1
            elif symbol.endswith('.HK'):
                stats['hk_stock'] += 1
            else:
                stats['us_stock'] += 1
        
        stats['a_stock_total'] = stats['a_stock_sh'] + stats['a_stock_sz']
        
        return stats

# 创建全局实例
universal_stock_fetcher = UniversalStockFetcher()

if __name__ == "__main__":
    # 测试全市场股票获取
    fetcher = UniversalStockFetcher()
    
    print("🌍 开始获取全市场股票信息...")
    all_stocks = fetcher.get_all_stocks()
    
    print(f"\n📊 股票数量统计:")
    stats = fetcher.get_market_statistics()
    print(f"  总计: {stats['total']:,} 只股票")
    print(f"  A股: {stats['a_stock_total']:,} 只 (上海: {stats['a_stock_sh']:,}, 深圳: {stats['a_stock_sz']:,})")
    print(f"  港股: {stats['hk_stock']:,} 只")
    print(f"  美股: {stats['us_stock']:,} 只")
    
    print(f"\n🔍 搜索测试:")
    test_queries = ["中石油", "腾讯", "苹果", "AAPL", "茅台"]
    
    for query in test_queries:
        results = fetcher.search_stocks(query, limit=3)
        print(f"\n搜索 '{query}':")
        for result in results:
            print(f"  {result['symbol']} - {result['name']} ({result['market']})")
