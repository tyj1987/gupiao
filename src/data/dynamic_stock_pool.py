#!/usr/bin/env python3
"""
动态股票池管理器
"""

import random
from typing import List, Dict
from loguru import logger
from .stock_mapper import stock_mapper

class DynamicStockPool:
    """动态股票池管理器"""
    
    def __init__(self):
        # 使用股票映射器获取完整股票池
        all_stocks = stock_mapper.get_all_stocks()
        
        self.stock_pools = {
            "中国A股": {},
            "美股": {}
        }
        
        # 自动分类股票到不同行业
        self._categorize_stocks(all_stocks)
        
        self.market_cap_mapping = {
            "大盘股": ["银行", "白酒", "科技"],
            "中盘股": ["医药", "新能源", "消费"],
            "小盘股": ["地产", "科技", "消费"]
        }
    
    def _categorize_stocks(self, all_stocks: Dict[str, str]):
        """根据股票名称和代码自动分类到行业"""
        
        # 行业关键词映射
        industry_keywords = {
            "银行": ["银行", "农商", "信贷", "金融"],
            "白酒": ["茅台", "五粮液", "洋河", "古井", "口子", "酒鬼", "水井坊", "泸州", "金徽", "舍得"],
            "地产": ["万科", "招商蛇口", "保利", "华侨城", "华夏幸福", "金地", "建发", "城建", "地产", "陆家嘴"],
            "科技": ["中兴", "海康", "东方财富", "沃森", "科大讯飞", "京东方", "歌尔", "宁德", "澜起", "晶晨", "苹果", "微软", "谷歌", "Meta", "英伟达", "亚马逊", "奈飞", "奥多比", "Salesforce"],
            "医药": ["长春高新", "恒瑞", "爱尔", "东阿阿胶", "药明", "泰格", "迈瑞", "华海", "凯莱英", "康泰", "辉瑞", "强生", "Moderna", "BioNTech", "吉利德", "安进", "Biogen", "再生元", "Vertex", "Illumina"],
            "新能源": ["宁德时代", "牧原", "阳光电源", "晶澳", "锦浪", "中环", "隆基", "亿纬锂能", "天齐"],
            "消费": ["双汇", "苏泊尔", "伊利", "百润", "海天", "美的", "格力", "安琪", "可口可乐", "百事", "沃尔玛", "家得宝", "麦当劳", "星巴克", "耐克", "迪士尼", "好市多", "塔吉特"],
            "电动车": ["特斯拉", "Rivian", "Lucid", "蔚来", "小鹏", "理想", "福特", "通用"],
            "金融": ["摩根大通", "美国银行", "高盛", "摩根士丹利", "花旗", "富国银行", "美国运通", "Visa", "万事达", "伯克希尔"]
        }
        
        # 初始化行业分类
        for market in self.stock_pools:
            for industry in industry_keywords:
                self.stock_pools[market][industry] = []
        
        # 自动分类股票
        for symbol, name in all_stocks.items():
            # 判断市场
            if symbol.endswith('.SZ') or symbol.endswith('.SH'):
                market = "中国A股"
            else:
                market = "美股"
            
            # 根据关键词分类到行业
            classified = False
            for industry, keywords in industry_keywords.items():
                for keyword in keywords:
                    if keyword in name:
                        self.stock_pools[market][industry].append(symbol)
                        classified = True
                        break
                if classified:
                    break
            
            # 如果没有分类成功，放入默认的"其他"分类
            if not classified:
                if "其他" not in self.stock_pools[market]:
                    self.stock_pools[market]["其他"] = []
                self.stock_pools[market]["其他"].append(symbol)
    
    def get_stock_pool(self, 
                      market: str = "混合", 
                      sector: str = "全部", 
                      market_cap: str = "不限",
                      pool_size: int = 200) -> List[str]:
        """
        获取动态股票池
        
        Args:
            market: 市场类型 ("中国A股", "美股", "混合")
            sector: 行业类型 ("全部", "银行", "科技", 等)
            market_cap: 市值偏好 ("不限", "大盘股", "中盘股", "小盘股")
            pool_size: 股票池大小
            
        Returns:
            股票代码列表
        """
        try:
            stocks = []
            
            # 根据市场选择股票池
            if market == "中国A股":
                source_pools = [self.stock_pools["中国A股"]]
            elif market == "美股":
                source_pools = [self.stock_pools["美股"]]
            else:  # 混合
                source_pools = [self.stock_pools["中国A股"], self.stock_pools["美股"]]
            
            # 根据行业筛选
            for pool in source_pools:
                if sector == "全部":
                    # 所有行业
                    for sector_stocks in pool.values():
                        stocks.extend(sector_stocks)
                elif sector in pool:
                    # 特定行业
                    stocks.extend(pool[sector])
                else:
                    # 如果指定行业不存在，添加所有股票
                    for sector_stocks in pool.values():
                        stocks.extend(sector_stocks)
            
            # 根据市值偏好筛选
            if market_cap != "不限" and market_cap in self.market_cap_mapping:
                preferred_sectors = self.market_cap_mapping[market_cap]
                filtered_stocks = []
                
                for pool in source_pools:
                    for sector_name, sector_stocks in pool.items():
                        if sector_name in preferred_sectors:
                            filtered_stocks.extend(sector_stocks)
                
                if filtered_stocks:
                    stocks = filtered_stocks
            
            # 去重
            unique_stocks = list(set(stocks))
            
            # 如果池子大小小于等于请求大小，返回全部
            if len(unique_stocks) <= pool_size:
                return unique_stocks
            else:
                # 随机选择指定数量
                return random.sample(unique_stocks, pool_size)
                
        except Exception as e:
            logger.error(f"生成股票池失败: {e}")
            # 返回所有可用股票作为备选
            return list(stock_mapper.get_all_stocks().keys())
    
    def get_all_stocks(self) -> List[str]:
        """获取所有可用股票代码"""
        return list(stock_mapper.get_all_stocks().keys())
    
    def get_sector_stocks(self, sector: str, market: str = "混合") -> List[str]:
        """获取特定行业的股票"""
        stocks = []
        
        if market in ["中国A股", "混合"] and sector in self.stock_pools["中国A股"]:
            stocks.extend(self.stock_pools["中国A股"][sector])
        
        if market in ["美股", "混合"] and sector in self.stock_pools["美股"]:
            stocks.extend(self.stock_pools["美股"][sector])
        
        return stocks
    
    def get_available_sectors(self, market: str = "混合") -> List[str]:
        """获取可用的行业列表"""
        sectors = set(["全部"])
        
        if market in ["中国A股", "混合"]:
            sectors.update(self.stock_pools["中国A股"].keys())
        
        if market in ["美股", "混合"]:
            sectors.update(self.stock_pools["美股"].keys())
        
        return sorted(list(sectors))
    
    def get_random_stocks(self, count: int = 10) -> List[str]:
        """获取随机股票组合"""
        all_stocks = self.get_all_stocks()
        return random.sample(all_stocks, min(count, len(all_stocks)))
    
    def get_pool_statistics(self) -> Dict:
        """获取股票池统计信息"""
        stats = {
            "总股票数": len(self.get_all_stocks()),
            "中国A股": {
                "总数": sum(len(stocks) for stocks in self.stock_pools["中国A股"].values()),
                "行业分布": {k: len(v) for k, v in self.stock_pools["中国A股"].items()}
            },
            "美股": {
                "总数": sum(len(stocks) for stocks in self.stock_pools["美股"].values()),
                "行业分布": {k: len(v) for k, v in self.stock_pools["美股"].items()}
            }
        }
        return stats
