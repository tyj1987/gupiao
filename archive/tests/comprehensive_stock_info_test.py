#!/usr/bin/env python3
"""
全面股票信息可用性测试
确保所有功能都能获取完整的实时股票信息
"""

import sys
import os
sys.path.append('/home/tyj/gupiao')

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def test_data_source_availability():
    """测试数据源可用性"""
    print("🔍 测试数据源可用性")
    print("=" * 60)
    
    try:
        from src.data.data_fetcher import DataFetcher
        from src.data.stock_mapper import stock_mapper
        
        data_fetcher = DataFetcher()
        
        # 测试不同类型的股票
        test_stocks = [
            ("601857.SH", "中国石油", "大盘央企"),
            ("600028.SH", "中国石化", "大盘央企"),
            ("600519.SH", "贵州茅台", "大盘蓝筹"),
            ("000002.SZ", "万科A", "大盘地产"),
            ("300750.SZ", "宁德时代", "创业板科技"),
            ("002594.SZ", "比亚迪", "中小板新能源"),
            ("000063.SZ", "中兴通讯", "深市科技"),
            ("688008.SH", "澜起科技", "科创板"),
            ("002415.SZ", "海康威视", "中小板科技"),
            ("601398.SH", "工商银行", "大盘银行"),
        ]
        
        successful_stocks = []
        failed_stocks = []
        
        for code, name, category in test_stocks:
            print(f"\n测试 {code} ({name} - {category}):")
            
            try:
                # 测试数据获取
                stock_data = data_fetcher.get_stock_data(code, period='6m')
                
                if stock_data is not None and not stock_data.empty:
                    print(f"  ✅ 数据获取成功")
                    print(f"     记录数: {len(stock_data)}")
                    print(f"     日期范围: {stock_data.index.min()} 到 {stock_data.index.max()}")
                    print(f"     价格范围: {stock_data['close'].min():.2f} - {stock_data['close'].max():.2f}")
                    print(f"     包含列: {list(stock_data.columns)}")
                    
                    # 检查关键列
                    required_columns = ['open', 'high', 'low', 'close']
                    
                    # 检查volume列（可能是vol或volume）
                    volume_column = None
                    if 'volume' in stock_data.columns:
                        volume_column = 'volume'
                    elif 'vol' in stock_data.columns:
                        volume_column = 'vol'
                    
                    if volume_column:
                        required_columns.append(volume_column)
                        missing_columns = [col for col in required_columns if col not in stock_data.columns]
                    else:
                        missing_columns = [col for col in required_columns if col not in stock_data.columns]
                        missing_columns.append('volume/vol')
                    
                    if missing_columns:
                        print(f"  ⚠️  缺少关键列: {missing_columns}")
                    else:
                        print(f"  ✅ 所有关键列完整")
                    
                    # 检查数据质量
                    check_columns = [col for col in required_columns if col in stock_data.columns]
                    if check_columns:
                        null_counts = stock_data[check_columns].isnull().sum()
                        if null_counts.sum() > 0:
                            print(f"  ⚠️  存在空值: {null_counts.to_dict()}")
                        else:
                            print(f"  ✅ 数据质量良好")
                    
                    successful_stocks.append((code, name, category))
                    
                else:
                    print(f"  ❌ 数据获取失败或为空")
                    failed_stocks.append((code, name, category))
                    
            except Exception as e:
                print(f"  ❌ 数据获取异常: {e}")
                failed_stocks.append((code, name, category))
        
        print(f"\n📊 数据源测试汇总:")
        print(f"成功获取数据: {len(successful_stocks)}/{len(test_stocks)} 只股票")
        print(f"失败股票: {len(failed_stocks)} 只")
        
        if failed_stocks:
            print(f"\n失败列表:")
            for code, name, category in failed_stocks:
                print(f"  ❌ {code} ({name} - {category})")
        
        return successful_stocks, failed_stocks
        
    except Exception as e:
        print(f"❌ 数据源测试失败: {e}")
        import traceback
        traceback.print_exc()
        return [], []

def test_stock_search_functionality():
    """测试股票搜索功能"""
    print("\n🔍 测试股票搜索功能")
    print("=" * 60)
    
    try:
        from src.data.stock_mapper import stock_mapper
        
        # 测试各种搜索场景
        search_cases = [
            ("601857", "代码搜索"),
            ("中国石油", "名称搜索"),
            ("中石油", "简称搜索"),
            ("石油", "关键词搜索"),
            ("茅台", "热门股票"),
            ("银行", "行业搜索"),
            ("比亚迪", "新能源"),
            ("宁德时代", "科技股"),
            ("万科", "地产股"),
            ("平安", "金融股"),
        ]
        
        for query, description in search_cases:
            print(f"\n{description} ('{query}'):")
            
            # 使用基础搜索
            basic_results = stock_mapper.search_stocks(query, 5)
            
            # 使用完整搜索
            comprehensive_results = stock_mapper.search_comprehensive(query, 5)
            
            print(f"  基础搜索结果: {len(basic_results)}")
            for result in basic_results[:3]:
                print(f"    📊 {result['symbol']} - {result['name']}")
            
            print(f"  完整搜索结果: {len(comprehensive_results)}")
            for result in comprehensive_results[:3]:
                print(f"    📈 {result['symbol']} - {result['name']}")
        
        # 测试股票池大小
        all_stocks = stock_mapper.get_comprehensive_stocks()
        print(f"\n📊 股票池统计:")
        print(f"总股票数量: {len(all_stocks)}")
        
        # 按市场分类统计
        a_stocks = [s for s in all_stocks.keys() if s.endswith('.SZ') or s.endswith('.SH')]
        us_stocks = [s for s in all_stocks.keys() if not (s.endswith('.SZ') or s.endswith('.SH') or s.endswith('.HK'))]
        hk_stocks = [s for s in all_stocks.keys() if s.endswith('.HK')]
        
        print(f"A股数量: {len(a_stocks)}")
        print(f"美股数量: {len(us_stocks)}")
        print(f"港股数量: {len(hk_stocks)}")
        
        print(f"\n✅ 搜索功能测试完成")
        
    except Exception as e:
        print(f"❌ 搜索功能测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_risk_analysis_integration():
    """测试风险分析系统集成"""
    print("\n🔍 测试风险分析系统集成")
    print("=" * 60)
    
    try:
        from src.ai.risk_manager import RiskManager
        from src.ai.stock_analyzer import StockAnalyzer
        from src.data.data_fetcher import DataFetcher
        from src.data.stock_mapper import stock_mapper
        
        # 初始化组件
        risk_manager = RiskManager()
        analyzer = StockAnalyzer()
        data_fetcher = DataFetcher()
        
        # 测试股票（重点测试中国石油）
        test_stocks = [
            "601857.SH",  # 中国石油
            "600028.SH",  # 中国石化
            "600519.SH",  # 贵州茅台
            "000002.SZ",  # 万科A
            "300750.SZ",  # 宁德时代
        ]
        
        print(f"测试股票池:")
        for stock in test_stocks:
            name = stock_mapper.get_stock_name(stock)
            print(f"  📊 {stock}: {name}")
        
        # 测试风险评估
        print(f"\n--- 风险评估测试 ---")
        risk_results = {}
        
        for stock in test_stocks:
            try:
                print(f"\n分析 {stock}:")
                name = stock_mapper.get_stock_name(stock)
                print(f"股票名称: {name}")
                
                # 获取数据
                stock_data = data_fetcher.get_stock_data(stock, period='6m')
                if stock_data is None or stock_data.empty:
                    print(f"  ❌ 无法获取数据")
                    continue
                
                print(f"  ✅ 数据获取成功: {len(stock_data)} 天")
                
                # 风险评估
                risk_result = risk_manager.assess_risk(stock_data)
                overall_risk = risk_result.get('overall_risk', {})
                
                print(f"  风险评分: {overall_risk.get('score', 'N/A')}")
                print(f"  风险等级: {overall_risk.get('level', 'N/A')}")
                
                risk_results[stock] = {
                    'name': name,
                    'score': overall_risk.get('score', 0),
                    'level': overall_risk.get('level', '未知'),
                    'success': True
                }
                
            except Exception as e:
                print(f"  ❌ 风险评估失败: {e}")
                risk_results[stock] = {
                    'name': stock_mapper.get_stock_name(stock),
                    'score': 0,
                    'level': '错误',
                    'success': False
                }
        
        # 测试智能筛选
        print(f"\n--- 智能筛选测试 ---")
        risk_levels = ["低风险", "中等风险", "高风险"]
        
        for risk_level in risk_levels:
            print(f"\n筛选风险级别: {risk_level}")
            
            try:
                results = analyzer.screen_stocks(
                    stock_list=test_stocks,
                    min_score=0,
                    risk_level=risk_level,
                    market_cap="不限"
                )
                
                print(f"  筛选结果: {len(results)} 只股票")
                for result in results:
                    name = stock_mapper.get_stock_name(result['symbol'])
                    print(f"    📈 {result['symbol']} ({name}): "
                          f"评分={result['score']:.1f}, 风险={result['risk_level']}")
                
            except Exception as e:
                print(f"  ❌ 筛选失败: {e}")
        
        # 汇总结果
        print(f"\n📊 风险分析汇总:")
        successful_analyses = sum(1 for r in risk_results.values() if r['success'])
        print(f"成功分析: {successful_analyses}/{len(test_stocks)} 只股票")
        
        print(f"\n风险分布:")
        for stock, result in risk_results.items():
            if result['success']:
                print(f"  {result['level']}: {stock} ({result['name']}) - {result['score']:.1f}")
        
        print(f"\n✅ 风险分析集成测试完成")
        
    except Exception as e:
        print(f"❌ 风险分析集成测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_ui_integration():
    """测试UI集成"""
    print("\n🔍 测试UI集成")
    print("=" * 60)
    
    try:
        from src.data.stock_mapper import stock_mapper
        
        # 测试股票建议功能
        print("测试股票建议功能:")
        test_inputs = ["中国石油", "石油", "茅台", "银行", "比亚迪"]
        
        for input_text in test_inputs:
            suggestions = stock_mapper.get_stock_suggestions(input_text)
            print(f"  输入 '{input_text}' -> {len(suggestions)} 个建议")
            for suggestion in suggestions[:3]:
                print(f"    💡 {suggestion}")
        
        # 测试行业分类
        print(f"\n测试行业分类:")
        from src.data.comprehensive_stock_pool import comprehensive_stock_pool
        
        industries = comprehensive_stock_pool.get_industry_list()
        print(f"支持的行业数量: {len(industries)}")
        
        for industry in industries[:5]:
            stocks = stock_mapper.get_stocks_by_industry(industry)
            print(f"  {industry}: {len(stocks)} 只股票")
        
        # 测试蓝筹股池
        blue_chips = stock_mapper.get_blue_chip_stocks()
        print(f"\n蓝筹股数量: {len(blue_chips)}")
        
        print(f"\n✅ UI集成测试完成")
        
    except Exception as e:
        print(f"❌ UI集成测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 开始全面股票信息可用性测试")
    print("=" * 80)
    
    # 运行所有测试
    successful_stocks, failed_stocks = test_data_source_availability()
    test_stock_search_functionality()
    test_risk_analysis_integration()
    test_ui_integration()
    
    print("\n🎯 测试总结")
    print("=" * 80)
    print(f"✅ 数据获取成功: {len(successful_stocks)} 只股票")
    print(f"❌ 数据获取失败: {len(failed_stocks)} 只股票")
    
    if len(successful_stocks) > 0:
        print(f"\n✅ 系统功能正常，可以处理以下股票:")
        for code, name, category in successful_stocks[:10]:
            print(f"  📊 {code} ({name})")
    
    if len(failed_stocks) > 0:
        print(f"\n⚠️  以下股票需要检查:")
        for code, name, category in failed_stocks:
            print(f"  ❌ {code} ({name})")
    
    print(f"\n🎉 全面测试完成！")
