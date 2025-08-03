#!/usr/bin/env python3
"""
测试扩展的股票池功能
验证中国石油等重要股票是否已正确映射
"""

import sys
import os
sys.path.append('/home/tyj/gupiao')

def test_comprehensive_stock_pool():
    """测试完整股票池"""
    print("🎯 测试完整股票池")
    print("=" * 60)
    
    try:
        from src.data.stock_mapper import stock_mapper
        from src.data.comprehensive_stock_pool import comprehensive_stock_pool
        
        print("1. 测试股票池规模")
        all_stocks = stock_mapper.get_comprehensive_stocks()
        print(f"总股票数量: {len(all_stocks)}")
        
        print("\n2. 测试重要股票映射")
        important_stocks = [
            '601857.SH',  # 中国石油
            '600028.SH',  # 中国石化  
            '601398.SH',  # 工商银行
            '600519.SH',  # 贵州茅台
            '000002.SZ',  # 万科A
            '300750.SZ',  # 宁德时代
            '002594.SZ',  # 比亚迪
            '000063.SZ',  # 中兴通讯
            '002415.SZ',  # 海康威视
            '000661.SZ',  # 长春高新
        ]
        
        for code in important_stocks:
            name = stock_mapper.get_stock_name(code)
            status = "✅" if name != code else "❌"
            print(f"  {status} {code}: {name}")
        
        print("\n3. 测试搜索功能")
        search_terms = ['中国石油', '中石油', '茅台', '万科', '宁德', '比亚迪']
        
        for term in search_terms:
            results = stock_mapper.search_comprehensive(term, 3)
            print(f"\n搜索 '{term}':")
            for result in results:
                print(f"  📊 {result['symbol']} - {result['name']}")
        
        print("\n4. 测试行业分类")
        industries = comprehensive_stock_pool.get_industry_list()
        print(f"支持的行业数量: {len(industries)}")
        
        for industry in industries[:5]:  # 显示前5个行业
            stocks = stock_mapper.get_stocks_by_industry(industry)
            print(f"  📈 {industry}: {len(stocks)}只股票")
            if stocks:
                # 显示前3只股票
                for stock in stocks[:3]:
                    name = stock_mapper.get_stock_name(stock)
                    print(f"     - {stock}: {name}")
        
        print("\n5. 测试蓝筹股列表")
        blue_chips = stock_mapper.get_blue_chip_stocks()
        print(f"蓝筹股数量: {len(blue_chips)}")
        print("主要蓝筹股:")
        for stock in blue_chips[:10]:
            name = stock_mapper.get_stock_name(stock)
            print(f"  💎 {stock}: {name}")
        
        print("\n6. 测试随机股票样本")
        random_stocks = stock_mapper.get_random_sample(8)
        print("随机股票样本:")
        for stock in random_stocks:
            name = stock_mapper.get_stock_name(stock)
            print(f"  🎲 {stock}: {name}")
        
        print("\n✅ 股票池测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_risk_analysis_with_expanded_pool():
    """测试扩展股票池的风险分析"""
    print("\n🎯 测试扩展股票池的风险分析")
    print("=" * 60)
    
    try:
        from src.ai.stock_analyzer import StockAnalyzer
        from src.data.stock_mapper import stock_mapper
        
        analyzer = StockAnalyzer()
        
        # 使用包含中国石油等股票的测试池
        test_stocks = [
            '601857.SH',  # 中国石油
            '600028.SH',  # 中国石化
            '600519.SH',  # 贵州茅台
            '000002.SZ',  # 万科A
            '300750.SZ',  # 宁德时代
            '002594.SZ',  # 比亚迪
            '601398.SH',  # 工商银行
            '600036.SH',  # 招商银行
        ]
        
        print("测试股票池:")
        for stock in test_stocks:
            name = stock_mapper.get_stock_name(stock)
            print(f"  📊 {stock}: {name}")
        
        print("\n执行风险分析和筛选...")
        
        # 测试不同风险偏好的筛选
        risk_levels = ["低风险", "中等风险", "高风险"]
        
        for risk_level in risk_levels:
            print(f"\n--- 风险偏好: {risk_level} ---")
            
            results = analyzer.screen_stocks(
                stock_list=test_stocks,
                min_score=0,  # 降低评分要求
                risk_level=risk_level,
                market_cap="不限"
            )
            
            print(f"筛选结果: {len(results)}只股票")
            for result in results:
                name = stock_mapper.get_stock_name(result['symbol'])
                print(f"  📈 {result['symbol']} - {name}: "
                      f"评分={result['score']:.1f}, 风险={result['risk_level']}")
        
        print("\n✅ 风险分析测试完成")
        
    except Exception as e:
        print(f"❌ 风险分析测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_specific_stock_search():
    """测试特定股票搜索"""
    print("\n🎯 测试特定股票搜索")
    print("=" * 60)
    
    try:
        from src.data.stock_mapper import stock_mapper
        
        # 测试各种搜索方式
        search_cases = [
            ('601857', '按代码搜索中国石油'),
            ('中国石油', '按名称搜索中国石油'),
            ('中石油', '按简称搜索中国石油'),
            ('石油', '模糊搜索石油相关'),
            ('银行', '搜索银行股'),
            ('白酒', '搜索白酒股'),
            ('新能源', '搜索新能源股'),
            ('茅台', '搜索茅台'),
            ('比亚迪', '搜索比亚迪'),
            ('平安', '搜索平安相关'),
        ]
        
        for query, description in search_cases:
            print(f"\n{description} ('{query}'):")
            results = stock_mapper.search_comprehensive(query, 5)
            
            if results:
                for result in results:
                    print(f"  ✅ {result['symbol']} - {result['name']} [{result['match_type']}]")
            else:
                print("  ❌ 未找到匹配结果")
        
        print("\n✅ 搜索测试完成")
        
    except Exception as e:
        print(f"❌ 搜索测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 开始测试扩展股票池")
    print("=" * 80)
    
    # 运行所有测试
    test_comprehensive_stock_pool()
    test_specific_stock_search()
    test_risk_analysis_with_expanded_pool()
    
    print("\n🎉 所有测试完成")
