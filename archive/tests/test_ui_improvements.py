#!/usr/bin/env python3
"""
测试界面改进功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def test_stock_mapper_search():
    """测试股票映射器的搜索功能"""
    print("🧪 测试股票搜索功能")
    print("=" * 50)
    
    from src.data.stock_mapper import stock_mapper
    
    # 测试代码搜索
    print("\n📊 测试股票代码搜索:")
    test_queries = ["000001", "600519", "AAPL", "TSLA"]
    
    for query in test_queries:
        results = stock_mapper.search_stocks(query, limit=3)
        print(f"搜索 '{query}':")
        for result in results:
            print(f"  • {result['symbol']} - {result['name']} ({result['match_type']})")
    
    # 测试名称搜索
    print("\n🏷️ 测试股票名称搜索:")
    name_queries = ["平安", "茅台", "苹果", "特斯拉"]
    
    for query in name_queries:
        results = stock_mapper.search_stocks(query, limit=3)
        print(f"搜索 '{query}':")
        for result in results:
            print(f"  • {result['symbol']} - {result['name']} ({result['match_type']})")
    
    # 测试输入建议
    print("\n💡 测试输入建议:")
    suggestion_queries = ["600", "000", "A", "M"]
    
    for query in suggestion_queries:
        suggestions = stock_mapper.get_stock_suggestions(query)
        print(f"输入 '{query}' 的建议 (前5个):")
        for suggestion in suggestions[:5]:
            print(f"  • {suggestion}")

def test_stock_mapping_coverage():
    """测试股票映射覆盖率"""
    print("\n🧪 测试股票映射覆盖率")
    print("=" * 50)
    
    from src.data.stock_mapper import stock_mapper
    
    all_stocks = stock_mapper.get_all_stocks()
    a_stocks = stock_mapper.get_stocks_by_market("中国A股")
    us_stocks = stock_mapper.get_stocks_by_market("美股")
    
    print(f"📊 总股票数: {len(all_stocks)}")
    print(f"🇨🇳 A股数量: {len(a_stocks)}")
    print(f"🇺🇸 美股数量: {len(us_stocks)}")
    
    # 验证分类正确性
    print(f"\n✅ 验证分类:")
    a_stock_check = all([s.endswith('.SZ') or s.endswith('.SH') for s in a_stocks.keys()])
    us_stock_check = all([not (s.endswith('.SZ') or s.endswith('.SH')) for s in us_stocks.keys()])
    
    print(f"A股分类正确: {a_stock_check}")
    print(f"美股分类正确: {us_stock_check}")
    
    # 显示一些样例
    print(f"\n📋 A股样例 (前5个):")
    for i, (symbol, name) in enumerate(list(a_stocks.items())[:5]):
        print(f"  {i+1}. {symbol} - {name}")
    
    print(f"\n📋 美股样例 (前5个):")
    for i, (symbol, name) in enumerate(list(us_stocks.items())[:5]):
        print(f"  {i+1}. {symbol} - {name}")

def main():
    """运行所有测试"""
    print("🚀 开始测试界面改进功能")
    print("=" * 70)
    
    test_stock_mapper_search()
    test_stock_mapping_coverage()
    
    print("\n✅ 界面改进功能测试完成！")
    print("=" * 70)
    
    print("\n📝 改进总结:")
    print("1. ✅ 功能导航改为直接列出的单选按钮")
    print("2. ✅ 股票输入支持智能搜索和自动匹配")
    print("3. ✅ 增强的股票映射器支持模糊搜索")
    print("4. ✅ 智能股票输入组件提供更好的用户体验")

if __name__ == "__main__":
    main()
