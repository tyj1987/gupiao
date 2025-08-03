#!/usr/bin/env python3
"""
股票代码与名称映射模块
"""

import pandas as pd
from typing import Dict, Optional, List
from loguru import logger

class StockMapper:
    """股票代码与名称映射器"""
    
    def __init__(self):
        # 延迟导入避免循环依赖
        try:
            from .universal_stock_fetcher import universal_stock_fetcher
            self.universal_fetcher = universal_stock_fetcher
            self.stock_mapping = self.universal_fetcher.get_all_stocks()
        except Exception as e:
            logger.warning(f"无法加载全市场股票获取器，使用回退映射: {e}")
            self.universal_fetcher = None
            self.stock_mapping = self._get_fallback_mapping()
            
        self.market_indices = self._init_market_indices()
        
    def _get_fallback_mapping(self) -> Dict[str, str]:
        """获取回退映射（基础股票列表）"""
        return {
            # 银行股
            '000001.SZ': '平安银行',
            '600000.SH': '浦发银行',
            '600036.SH': '招商银行',
            '601328.SH': '交通银行',
            '601398.SH': '工商银行',
            '601988.SH': '中国银行',
            '601939.SH': '建设银行',
            '600015.SH': '华夏银行',
            '601169.SH': '北京银行',
            '002142.SZ': '宁波银行',
            '600016.SH': '民生银行',
            '601009.SH': '南京银行',
            '600919.SH': '江苏银行',
            '002839.SZ': '张家港行',
            '601229.SH': '上海银行',
            
            # 白酒股
            '600519.SH': '贵州茅台',
            '000858.SZ': '五粮液',
            '002304.SZ': '洋河股份',
            '000596.SZ': '古井贡酒',
            '603589.SH': '口子窖',
            '000799.SZ': '酒鬼酒',
            '600779.SH': '水井坊',
            '000568.SZ': '泸州老窖',
            
            # 石油石化
            '601857.SH': '中国石油',
            '600028.SH': '中国石化',
            '600688.SH': '上海石化',
            '002493.SZ': '荣盛石化',
            '000703.SZ': '恒逸石化',
            '601808.SH': '中海油服',
            '600938.SH': '中国海油',
            
            # 科技股
            '000063.SZ': '中兴通讯',
            '002415.SZ': '海康威视',
            '000725.SZ': '京东方A',
            '002050.SZ': '三花智控',
            '300750.SZ': '宁德时代',
            '002594.SZ': '比亚迪',
            
            # 主要美股
            'AAPL': '苹果公司',
            'MSFT': '微软公司',
            'GOOGL': '谷歌公司',
            'META': 'Meta公司',
            'NVDA': '英伟达公司',
            'AMZN': '亚马逊公司',
            'TSLA': '特斯拉公司',
            
            # 主要港股
            "00700.HK": "腾讯控股",
            "09988.HK": "阿里巴巴-SW",
            "03690.HK": "美团-W",
            "01024.HK": "快手-W",
            "00175.HK": "吉利汽车"
        }
    
    def _init_market_indices(self) -> Dict[str, str]:
        """初始化市场指数映射"""
        return {
            '000001.SH': '上证指数',
            '399001.SZ': '深证成指',
            '399006.SZ': '创业板指',
            '000688.SH': '科创50',
            '000300.SH': '沪深300',
            '000905.SH': '中证500',
            '^GSPC': '标普500',
            '^DJI': '道琼斯指数',
            '^IXIC': '纳斯达克指数'
        }
    
    def get_stock_name(self, symbol: str) -> str:
        """根据股票代码获取股票名称"""
        return self.stock_mapping.get(symbol.upper(), symbol)
    
    def get_stock_symbol(self, name: str) -> Optional[str]:
        """根据股票名称获取股票代码"""
        for symbol, stock_name in self.stock_mapping.items():
            if stock_name == name:
                return symbol
        return None
    
    def search_stocks(self, query: str, limit: int = 10) -> List[Dict[str, str]]:
        """搜索股票（支持代码和名称模糊搜索）"""
        if self.universal_fetcher:
            try:
                # 使用全市场搜索
                return self.universal_fetcher.search_stocks(query, limit)
            except Exception as e:
                logger.error(f"全市场搜索失败: {e}")
        
        # 回退到本地搜索
        return self._local_search(query, limit)
    
    def _local_search(self, query: str, limit: int = 10) -> List[Dict[str, str]]:
        """本地搜索（回退方法）"""
        query_original = query.strip()
        query = query.upper().strip()
        results = []
        
        if not query:
            return results
        
        # 特殊搜索映射
        search_aliases = {
            '中行': '中国银行',
            '工行': '工商银行', 
            '建行': '建设银行',
            '招行': '招商银行',
            '茅台': '贵州茅台',
            '五粮': '五粮液'
        }
        
        # 检查是否有别名匹配
        search_term = query_original
        for alias, full_name in search_aliases.items():
            if alias in query_original:
                search_term = full_name
                break
        
        for symbol, name in self.stock_mapping.items():
            match_score = 0
            match_type = 'none'
            
            # 1. 精确代码匹配（最高优先级）
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
            # 5. 模糊匹配（去掉股票后缀等）
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
        
        # 按匹配分数排序，分数越高越靠前
        results.sort(key=lambda x: (-x['score'], x['symbol']))
        
        # 返回结果时移除score字段
        final_results = []
        for r in results[:limit]:
            final_results.append({
                'symbol': r['symbol'],
                'name': r['name'],
                'match_type': r['match_type'],
                'market': r.get('market', '未知市场')
            })
        
        return final_results
    
    def get_stock_suggestions(self, partial_input: str) -> List[str]:
        """获取股票输入建议"""
        suggestions = []
        query = partial_input.strip()
        
        if len(query) < 1:
            return suggestions
        
        # 使用改进的搜索功能获取建议
        search_results = self.search_stocks(query, limit=10)
        
        for result in search_results:
            suggestion = f"{result['symbol']} - {result['name']}"
            suggestions.append(suggestion)
        
        return suggestions
    
    def add_names_to_data(self, data_list) -> list:
        """为股票数据列表添加名称字段"""
        enhanced_data = []
        
        for item in data_list:
            if isinstance(item, dict):
                symbol = item.get('symbol', '')
                name = self.get_stock_name(symbol)
                item['name'] = name
                enhanced_data.append(item)
            else:
                enhanced_data.append(item)
        
        return enhanced_data
    
    def get_all_stocks(self) -> Dict[str, str]:
        """获取所有股票的代码与名称映射"""
        return self.stock_mapping.copy()
    
    def get_market_name(self, index_code: str) -> str:
        """获取市场指数名称"""
        return self.market_indices.get(index_code, index_code)
    
    def get_stocks_by_market(self, market: str = "all") -> Dict[str, str]:
        """根据市场获取股票列表"""
        if market == "A股" or market == "中国A股":
            return {k: v for k, v in self.stock_mapping.items() 
                   if k.endswith('.SZ') or k.endswith('.SH')}
        elif market == "美股":
            return {k: v for k, v in self.stock_mapping.items() 
                   if not (k.endswith('.SZ') or k.endswith('.SH') or k.endswith('.HK'))}
        elif market == "港股":
            return {k: v for k, v in self.stock_mapping.items() 
                   if k.endswith('.HK')}
        else:
            return self.stock_mapping.copy()
    
    def expand_stock_pool(self, base_pool: list) -> list:
        """扩展股票池，返回所有可用股票"""
        return list(self.stock_mapping.keys())
    
    def get_comprehensive_stocks(self) -> Dict[str, str]:
        """获取完整股票池（全市场）"""
        if self.universal_fetcher:
            try:
                return self.universal_fetcher.get_all_stocks()
            except Exception as e:
                logger.error(f"获取全市场股票失败: {e}")
        return self.stock_mapping.copy()
    
    def get_market_statistics(self) -> Dict[str, int]:
        """获取市场统计信息"""
        if self.universal_fetcher:
            try:
                return self.universal_fetcher.get_market_statistics()
            except Exception as e:
                logger.error(f"获取市场统计失败: {e}")
        
        # 返回基础统计
        total = len(self.stock_mapping)
        a_stocks = sum(1 for k in self.stock_mapping.keys() if k.endswith(('.SH', '.SZ')))
        hk_stocks = sum(1 for k in self.stock_mapping.keys() if k.endswith('.HK'))
        us_stocks = total - a_stocks - hk_stocks
        
        return {
            'total': total, 
            'a_stock_total': a_stocks, 
            'hk_stock': hk_stocks, 
            'us_stock': us_stocks
        }
    
    def refresh_stock_data(self, force: bool = False):
        """刷新股票数据"""
        if self.universal_fetcher:
            try:
                logger.info("开始刷新股票数据...")
                new_mapping = self.universal_fetcher.get_all_stocks(force_refresh=force)
                self.stock_mapping = new_mapping
                logger.info(f"股票数据刷新完成，总计 {len(new_mapping)} 只股票")
            except Exception as e:
                logger.error(f"刷新股票数据失败: {e}")
        else:
            logger.warning("无全市场获取器，无法刷新股票数据")
    
    def search_comprehensive(self, query: str, limit: int = 20) -> List[Dict[str, str]]:
        """在完整股票池中搜索"""
        return self.search_stocks(query, limit)
    
    def get_stocks_by_industry(self, industry: str) -> Dict[str, str]:
        """根据行业获取股票列表"""
        # 简化版本，返回所有股票
        return self.stock_mapping.copy()
    
    def get_blue_chip_stocks(self) -> Dict[str, str]:
        """获取蓝筹股列表"""
        # 简化版本，返回一些知名蓝筹股
        blue_chips = {}
        for symbol, name in self.stock_mapping.items():
            if any(keyword in name for keyword in ['银行', '石油', '茅台', '平安', '工商', '建设', '中国']):
                blue_chips[symbol] = name
        return blue_chips
    
    def get_random_sample(self, count: int = 50) -> List[str]:
        """获取随机股票样本"""
        import random
        stocks = list(self.stock_mapping.keys())
        return random.sample(stocks, min(count, len(stocks)))

# 全局实例
stock_mapper = StockMapper()
