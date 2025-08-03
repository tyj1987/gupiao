#!/usr/bin/env python3
"""
股票精确搜索工具
提供类似界面的精确股票搜索功能
"""

import sys
import os
sys.path.append('/home/tyj/gupiao')

import pandas as pd
import numpy as np
from datetime import datetime

def interactive_stock_search():
    """交互式股票搜索"""
    print("🔍 股票精确搜索工具")
    print("=" * 50)
    print("输入股票名称、代码或关键词进行搜索")
    print("支持搜索: 中文名称、股票代码、简称、关键词")
    print("输入 'quit' 退出")
    print("=" * 50)
    
    try:
        from src.data.stock_mapper import stock_mapper
        from src.data.data_fetcher import DataFetcher
        from src.ai.risk_manager import RiskManager
        
        data_fetcher = DataFetcher()
        risk_manager = RiskManager()
        
        while True:
            # 获取用户输入
            search_term = input("\n请输入搜索关键词: ").strip()
            
            if search_term.lower() in ['quit', 'exit', 'q']:
                print("👋 退出搜索工具")
                break
            
            if not search_term:
                print("❌ 请输入有效的搜索关键词")
                continue
            
            print(f"\n🔍 搜索结果: '{search_term}'")
            print("-" * 40)
            
            # 执行搜索
            try:
                # 基础搜索
                basic_results = stock_mapper.search_stocks(search_term, limit=10)
                
                if not basic_results:
                    print("❌ 未找到匹配的股票")
                    continue
                
                print(f"找到 {len(basic_results)} 个匹配结果:")
                print()
                
                # 显示搜索结果
                for i, result in enumerate(basic_results, 1):
                    symbol = result.get('symbol', 'N/A')
                    name = result.get('name', 'N/A')
                    market = 'A股' if symbol.endswith(('.SH', '.SZ')) else ('港股' if symbol.endswith('.HK') else '美股')
                    
                    print(f"{i:2d}. {symbol:<12} {name:<20} [{market}]")
                    
                    # 获取实时信息
                    try:
                        stock_data = data_fetcher.get_stock_data(symbol, period='5d')
                        if stock_data is not None and not stock_data.empty:
                            latest_price = stock_data['close'].iloc[-1]
                            
                            # 计算涨跌
                            if len(stock_data) >= 2:
                                prev_close = stock_data['close'].iloc[-2]
                                price_change = latest_price - prev_close
                                change_pct = (price_change / prev_close) * 100
                                
                                # 颜色标识
                                if change_pct > 0:
                                    change_indicator = f"📈 +{change_pct:.2f}%"
                                elif change_pct < 0:
                                    change_indicator = f"📉 {change_pct:.2f}%"
                                else:
                                    change_indicator = f"➖ {change_pct:.2f}%"
                            else:
                                change_indicator = "➖ N/A"
                            
                            print(f"     💰 价格: {latest_price:.2f}  {change_indicator}")
                            
                            # 快速风险评估
                            if len(stock_data) >= 20:  # 确保有足够数据进行风险评估
                                risk_result = risk_manager.assess_risk(stock_data)
                                overall_risk = risk_result.get('overall_risk', {})
                                risk_level = overall_risk.get('level', 'N/A')
                                risk_score = overall_risk.get('score', 'N/A')
                                
                                risk_emoji = {
                                    '低风险': '🟢',
                                    '中等风险': '🟡', 
                                    '高风险': '🔴'
                                }.get(risk_level, '⚪')
                                
                                print(f"     {risk_emoji} 风险: {risk_level} (评分: {risk_score})")
                            else:
                                print(f"     ⚪ 风险: 数据不足")
                        else:
                            print(f"     ❌ 无法获取实时数据")
                    except Exception as e:
                        print(f"     ⚠️ 数据获取异常: {str(e)[:30]}...")
                    
                    print()
                
                # 显示搜索建议
                try:
                    suggestions = stock_mapper.get_stock_suggestions(search_term)
                    if suggestions and len(suggestions) > len(basic_results):
                        print("💡 其他相关建议:")
                        for suggestion in suggestions[len(basic_results):len(basic_results)+3]:
                            print(f"     {suggestion}")
                        print()
                except:
                    pass
                
            except Exception as e:
                print(f"❌ 搜索失败: {e}")
                import traceback
                traceback.print_exc()
    
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        print("请确保已正确安装所有依赖")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")

def batch_search_test():
    """批量搜索测试"""
    print("\n🎯 批量搜索测试")
    print("=" * 50)
    
    try:
        from src.data.stock_mapper import stock_mapper
        
        # 预定义的测试用例
        test_cases = [
            "中国石油",
            "601857",
            "石油",
            "茅台", 
            "600519",
            "银行",
            "比亚迪",
            "002594",
            "腾讯",
            "00700",
            "平安",
            "宁德时代",
            "新能源",
            "科技"
        ]
        
        print(f"测试 {len(test_cases)} 个搜索用例:\n")
        
        for i, search_term in enumerate(test_cases, 1):
            print(f"{i:2d}. 搜索 '{search_term}':")
            
            try:
                results = stock_mapper.search_stocks(search_term, limit=3)
                if results:
                    for j, result in enumerate(results, 1):
                        symbol = result.get('symbol', 'N/A')
                        name = result.get('name', 'N/A')
                        print(f"     {j}. {symbol} - {name}")
                    print(f"     ✅ 找到 {len(results)} 个结果")
                else:
                    print(f"     ❌ 未找到结果")
            except Exception as e:
                print(f"     ❌ 搜索失败: {e}")
            
            print()
        
        print("✅ 批量搜索测试完成")
        
    except Exception as e:
        print(f"❌ 批量搜索测试失败: {e}")

def comprehensive_stock_database_info():
    """显示股票数据库信息"""
    print("\n📊 股票数据库信息")
    print("=" * 50)
    
    try:
        from src.data.stock_mapper import stock_mapper
        from src.data.comprehensive_stock_pool import comprehensive_stock_pool
        
        # 获取所有股票
        all_stocks = stock_mapper.get_comprehensive_stocks()
        print(f"📈 总股票数量: {len(all_stocks)} 只")
        
        # 按市场分类
        markets = {
            'A股(上海)': [s for s in all_stocks.keys() if s.endswith('.SH')],
            'A股(深圳)': [s for s in all_stocks.keys() if s.endswith('.SZ')],
            '港股': [s for s in all_stocks.keys() if s.endswith('.HK')],
            '美股': [s for s in all_stocks.keys() if not any(s.endswith(x) for x in ['.SH', '.SZ', '.HK'])]
        }
        
        print("\n📊 按市场分布:")
        for market, stocks in markets.items():
            print(f"  {market}: {len(stocks)} 只")
            # 显示几个示例
            for stock in stocks[:3]:
                name = all_stocks.get(stock, 'N/A')
                print(f"    - {stock}: {name}")
            if len(stocks) > 3:
                print(f"    ... 还有 {len(stocks)-3} 只")
            print()
        
        # 行业分类信息
        try:
            industries = comprehensive_stock_pool.get_industry_list()
            print(f"🏭 支持行业分类: {len(industries)} 个")
            
            print("\n🏭 行业分布:")
            for industry in industries[:8]:
                stocks = stock_mapper.get_stocks_by_industry(industry)
                print(f"  {industry}: {len(stocks)} 只股票")
            
            if len(industries) > 8:
                print(f"  ... 还有 {len(industries)-8} 个行业")
        except Exception as e:
            print(f"⚠️ 行业信息获取失败: {e}")
        
        # 蓝筹股信息
        try:
            blue_chips = stock_mapper.get_blue_chip_stocks()
            print(f"\n💎 蓝筹股数量: {len(blue_chips)} 只")
            
            print("💎 部分蓝筹股:")
            for i, (code, name) in enumerate(list(blue_chips.items())[:5], 1):
                print(f"  {i}. {code} - {name}")
            
            if len(blue_chips) > 5:
                print(f"  ... 还有 {len(blue_chips)-5} 只蓝筹股")
        except Exception as e:
            print(f"⚠️ 蓝筹股信息获取失败: {e}")
        
    except Exception as e:
        print(f"❌ 数据库信息获取失败: {e}")

if __name__ == "__main__":
    print("🎯 股票精确搜索系统")
    print("支持多种搜索方式，提供实时股票信息")
    
    # 显示数据库信息
    comprehensive_stock_database_info()
    
    # 运行批量测试
    batch_search_test()
    
    # 启动交互式搜索
    interactive_stock_search()
