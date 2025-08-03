#!/usr/bin/env python3
"""
股票搜索增强模块
提供更全面的股票信息检索和分析功能
"""

import pandas as pd
import re
from typing import Dict, List, Optional, Tuple, Any
from loguru import logger
from datetime import datetime, timedelta

class StockSearchEnhancer:
    """股票搜索增强器"""
    
    def __init__(self):
        self.alternative_mappings = self._init_alternative_mappings()
        self.fuzzy_search_patterns = self._init_fuzzy_patterns()
        self.market_prefixes = self._init_market_prefixes()
        self.company_aliases = self._init_company_aliases()
    
    def _init_alternative_mappings(self) -> Dict[str, List[str]]:
        """初始化备选映射表"""
        return {
            # 同一公司的不同上市地
            '中国石油': [
                '601857.SH',  # A股
                '00857.HK',   # H股
                'PTR',        # 美股ADR
            ],
            '中国石化': [
                '600028.SH',  # A股
                '00386.HK',   # H股
                'SNP',        # 美股ADR
            ],
            '中国平安': [
                '601318.SH',  # A股
                '02318.HK',   # H股
            ],
            '中国人寿': [
                '601628.SH',  # A股
                '02628.HK',   # H股
                'LFC',        # 美股ADR
            ],
            '中国移动': [
                '600941.SH',  # A股
                '00941.HK',   # H股
                'CHL',        # 美股ADR
            ],
            '中国电信': [
                '601728.SH',  # A股
                '00728.HK',   # H股
                'CHA',        # 美股ADR
            ],
            '中国联通': [
                '600050.SH',  # A股
                '00762.HK',   # H股
                'CHU',        # 美股ADR
            ],
            '腾讯控股': [
                '00700.HK',   # 港股
                'TCEHY',      # 美股ADR
            ],
            '阿里巴巴': [
                '09988.HK',   # 港股
                'BABA',       # 美股
            ],
            '贵州茅台': [
                '600519.SH',  # A股
            ],
            '五粮液': [
                '000858.SZ',  # A股
            ],
            '比亚迪': [
                '002594.SZ',  # A股
                '01211.HK',   # H股
                'BYDDY',      # 美股ADR
            ],
            '宁德时代': [
                '300750.SZ',  # A股
            ],
        }
    
    def _init_fuzzy_patterns(self) -> Dict[str, List[str]]:
        """初始化模糊搜索模式"""
        return {
            # 拼音首字母缩写
            'ZGSYC': ['中国石油'],
            'ZGSH': ['中国石化'],
            'ZGPA': ['中国平安'],
            'GZMT': ['贵州茅台'],
            'WLY': ['五粮液'],
            'BYD': ['比亚迪'],
            'NDSJ': ['宁德时代'],
            
            # 常见简称
            '石油': ['中国石油', '中国石化'],
            '银行': ['工商银行', '建设银行', '中国银行', '农业银行', '招商银行', '平安银行'],
            '保险': ['中国平安', '中国人寿', '中国太保', '新华保险'],
            '白酒': ['贵州茅台', '五粮液', '剑南春', '洋河股份'],
            '新能源': ['比亚迪', '宁德时代', '隆基绿能', '阳光电源'],
            '科技': ['中兴通讯', '海康威视', '科大讯飞', '立讯精密'],
            
            # 行业关键词
            '汽车': ['比亚迪', '长城汽车', '长安汽车', '上汽集团'],
            '医药': ['恒瑞医药', '药明康德', '迈瑞医疗', '爱尔眼科'],
            '地产': ['万科A', '保利地产', '招商蛇口', '华夏幸福'],
            '食品': ['伊利股份', '双汇发展', '海天味业', '中炬高新'],
        }
    
    def _init_market_prefixes(self) -> Dict[str, str]:
        """初始化市场前缀"""
        return {
            'SH': '上海证券交易所',
            'SZ': '深圳证券交易所',
            'HK': '香港证券交易所',
            'US': '美国证券交易所',
            'NASDAQ': '纳斯达克',
            'NYSE': '纽约证券交易所',
        }
    
    def _init_company_aliases(self) -> Dict[str, str]:
        """初始化公司别名"""
        return {
            # 银行
            '工行': '工商银行',
            '建行': '建设银行',
            '中行': '中国银行',
            '农行': '农业银行',
            '招行': '招商银行',
            '浦发': '浦发银行',
            '民生': '民生银行',
            '光大': '光大银行',
            '华夏': '华夏银行',
            '交行': '交通银行',
            
            # 保险
            '平安': '中国平安',
            '人寿': '中国人寿',
            '太保': '中国太保',
            '新华': '新华保险',
            
            # 石油化工
            '中石油': '中国石油',
            '中石化': '中国石化',
            '中海油': '中国海洋石油',
            
            # 电信
            '移动': '中国移动',
            '联通': '中国联通',
            '电信': '中国电信',
            
            # 科技
            '华为': '华为技术',  # 注意：华为未上市
            '腾讯': '腾讯控股',
            '阿里': '阿里巴巴',
            '百度': '百度',
            '京东': '京东',
            '美团': '美团',
            '滴滴': '滴滴出行',
            
            # 白酒
            '茅台': '贵州茅台',
            '五粮': '五粮液',
            '剑南春': '剑南春',
            '洋河': '洋河股份',
            '泸州': '泸州老窖',
            '古井': '古井贡酒',
            
            # 新能源汽车
            '比亚迪': '比亚迪',
            '理想': '理想汽车',
            '蔚来': '蔚来汽车',
            '小鹏': '小鹏汽车',
            '特斯拉': 'Tesla',
            
            # 新能源电池/材料
            '宁德': '宁德时代',
            '国轩': '国轩高科',
            '亿纬': '亿纬锂能',
            
            # 地产
            '万科': '万科A',
            '恒大': '中国恒大',
            '碧桂园': '碧桂园',
            '保利': '保利地产',
            
            # 医药
            '恒瑞': '恒瑞医药',
            '康美': '康美药业',
            '云南白药': '云南白药',
            '片仔癀': '片仔癀',
            
            # 食品饮料
            '伊利': '伊利股份',
            '蒙牛': '蒙牛乳业',
            '双汇': '双汇发展',
            '海天': '海天味业',
        }
    
    def enhanced_search(self, query: str, stock_mapper, data_fetcher=None) -> List[Dict[str, Any]]:
        """增强搜索功能"""
        results = []
        original_query = query.strip()
        
        logger.info(f"开始增强搜索: '{original_query}'")
        
        # 1. 基础搜索
        basic_results = self._basic_search(original_query, stock_mapper)
        results.extend(basic_results)
        
        # 2. 别名搜索
        alias_results = self._alias_search(original_query, stock_mapper)
        results.extend(alias_results)
        
        # 3. 模糊搜索
        fuzzy_results = self._fuzzy_search(original_query, stock_mapper)
        results.extend(fuzzy_results)
        
        # 4. 跨市场搜索
        cross_market_results = self._cross_market_search(original_query, stock_mapper)
        results.extend(cross_market_results)
        
        # 5. 去重和排序
        unique_results = self._deduplicate_and_rank(results)
        
        # 6. 添加数据状态检查
        if data_fetcher:
            enhanced_results = self._check_data_availability(unique_results, data_fetcher)
        else:
            enhanced_results = unique_results
        
        logger.info(f"搜索完成，共找到 {len(enhanced_results)} 个结果")
        return enhanced_results
    
    def _basic_search(self, query: str, stock_mapper) -> List[Dict[str, Any]]:
        """基础搜索"""
        try:
            results = stock_mapper.search_stocks(query, limit=20)
            return [self._format_result(r, 'basic', 100) for r in results]
        except Exception as e:
            logger.warning(f"基础搜索失败: {e}")
            return []
    
    def _alias_search(self, query: str, stock_mapper) -> List[Dict[str, Any]]:
        """别名搜索"""
        results = []
        query_lower = query.lower()
        
        # 检查公司别名
        for alias, full_name in self.company_aliases.items():
            if alias.lower() in query_lower or query_lower in alias.lower():
                try:
                    alias_results = stock_mapper.search_stocks(full_name, limit=5)
                    for r in alias_results:
                        formatted = self._format_result(r, 'alias', 80)
                        formatted['matched_alias'] = alias
                        results.append(formatted)
                except Exception as e:
                    logger.warning(f"别名搜索失败 ({alias}): {e}")
        
        return results
    
    def _fuzzy_search(self, query: str, stock_mapper) -> List[Dict[str, Any]]:
        """模糊搜索"""
        results = []
        query_upper = query.upper()
        
        # 检查模糊匹配模式
        for pattern, companies in self.fuzzy_search_patterns.items():
            if pattern.upper() in query_upper or query_upper in pattern.upper():
                for company in companies:
                    try:
                        fuzzy_results = stock_mapper.search_stocks(company, limit=3)
                        for r in fuzzy_results:
                            formatted = self._format_result(r, 'fuzzy', 60)
                            formatted['matched_pattern'] = pattern
                            results.append(formatted)
                    except Exception as e:
                        logger.warning(f"模糊搜索失败 ({company}): {e}")
        
        return results
    
    def _cross_market_search(self, query: str, stock_mapper) -> List[Dict[str, Any]]:
        """跨市场搜索"""
        results = []
        
        # 检查是否有跨市场上市的股票
        for company, symbols in self.alternative_mappings.items():
            if (query.lower() in company.lower() or 
                company.lower() in query.lower() or
                any(query.upper() in symbol for symbol in symbols)):
                
                for symbol in symbols:
                    try:
                        # 尝试在股票映射中查找
                        name = stock_mapper.get_stock_name(symbol)
                        result = {
                            'symbol': symbol,
                            'name': name if name != symbol else company,
                            'match_type': 'cross_market'
                        }
                        formatted = self._format_result(result, 'cross_market', 70)
                        formatted['original_company'] = company
                        results.append(formatted)
                    except Exception as e:
                        logger.warning(f"跨市场搜索失败 ({symbol}): {e}")
        
        return results
    
    def _format_result(self, result: Dict, search_type: str, base_score: int) -> Dict[str, Any]:
        """格式化搜索结果"""
        return {
            'symbol': result.get('symbol', ''),
            'name': result.get('name', ''),
            'search_type': search_type,
            'score': base_score,
            'market': self._get_market_type(result.get('symbol', '')),
            'data_available': None,  # 将在后续检查中填充
        }
    
    def _get_market_type(self, symbol: str) -> str:
        """获取市场类型"""
        if symbol.endswith('.SH'):
            return '上海A股'
        elif symbol.endswith('.SZ'):
            return '深圳A股'
        elif symbol.endswith('.HK'):
            return '香港H股'
        elif symbol.endswith('.BJ'):
            return '北京新三板'
        elif len(symbol) <= 4 and symbol.isalpha():
            return '美股'
        else:
            return '未知市场'
    
    def _deduplicate_and_rank(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重和排序"""
        # 按symbol去重
        seen_symbols = set()
        unique_results = []
        
        # 按score降序排序
        sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)
        
        for result in sorted_results:
            symbol = result['symbol']
            if symbol not in seen_symbols and symbol:
                seen_symbols.add(symbol)
                unique_results.append(result)
        
        return unique_results
    
    def _check_data_availability(self, results: List[Dict[str, Any]], data_fetcher) -> List[Dict[str, Any]]:
        """检查数据可用性"""
        enhanced_results = []
        
        for result in results:
            symbol = result['symbol']
            try:
                # 快速检查数据可用性（获取少量数据）
                test_data = data_fetcher.get_stock_data(symbol, period='5d')
                result['data_available'] = test_data is not None and not test_data.empty
                
                if result['data_available']:
                    # 添加一些基本信息
                    latest_price = test_data['close'].iloc[-1] if not test_data.empty else None
                    result['latest_price'] = latest_price
                    result['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                else:
                    result['latest_price'] = None
                    result['last_update'] = None
                    
            except Exception as e:
                result['data_available'] = False
                result['latest_price'] = None
                result['last_update'] = None
                result['error'] = str(e)
                logger.warning(f"数据可用性检查失败 ({symbol}): {e}")
            
            enhanced_results.append(result)
        
        return enhanced_results
    
    def suggest_alternatives(self, query: str, stock_mapper) -> List[str]:
        """建议替代搜索词"""
        suggestions = []
        query_lower = query.lower()
        
        # 基于别名建议
        for alias, full_name in self.company_aliases.items():
            if query_lower in alias.lower():
                suggestions.append(f"尝试搜索: {full_name}")
            elif query_lower in full_name.lower():
                suggestions.append(f"简称搜索: {alias}")
        
        # 基于模糊模式建议
        for pattern, companies in self.fuzzy_search_patterns.items():
            if query_lower in pattern.lower():
                suggestions.extend([f"相关公司: {comp}" for comp in companies[:3]])
        
        return list(set(suggestions))[:10]  # 去重并限制数量
    
    def get_search_statistics(self, query: str, stock_mapper, data_fetcher=None) -> Dict[str, Any]:
        """获取搜索统计信息"""
        results = self.enhanced_search(query, stock_mapper, data_fetcher)
        
        stats = {
            'total_results': len(results),
            'by_search_type': {},
            'by_market': {},
            'data_available_count': 0,
            'data_unavailable_count': 0,
        }
        
        for result in results:
            # 按搜索类型统计
            search_type = result['search_type']
            stats['by_search_type'][search_type] = stats['by_search_type'].get(search_type, 0) + 1
            
            # 按市场统计
            market = result['market']
            stats['by_market'][market] = stats['by_market'].get(market, 0) + 1
            
            # 数据可用性统计
            if result.get('data_available'):
                stats['data_available_count'] += 1
            else:
                stats['data_unavailable_count'] += 1
        
        return stats

# 全局实例
stock_search_enhancer = StockSearchEnhancer()
