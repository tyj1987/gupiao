#!/usr/bin/env python3
"""
全市场股票系统测试脚本
"""

import sys
import os
sys.path.append('/home/tyj/gupiao')

from src.data.universal_stock_fetcher import universal_stock_fetcher
from src.data.stock_mapper import StockMapper

def test_universal_stock_system():
    """测试全市场股票系统"""
    print("🌍 全市场股票系统测试")
    print("=" * 60)
    
    # 测试全市场股票获取器
    print("1. 测试全市场股票获取器")
    print("-" * 30)
    
    try:
        # 获取所有股票
        all_stocks = universal_stock_fetcher.get_all_stocks()
        
        # 获取统计信息
        stats = universal_stock_fetcher.get_market_statistics()
        
        print(f"📊 股票数量统计:")
        print(f"  总计: {stats['total']:,} 只股票")
        print(f"  A股: {stats['a_stock_total']:,} 只")
        print(f"    - 上海A股: {stats['a_stock_sh']:,} 只")
        print(f"    - 深圳A股: {stats['a_stock_sz']:,} 只")
        print(f"  港股: {stats['hk_stock']:,} 只")
        print(f"  美股: {stats['us_stock']:,} 只")
        
        print(f"\n✅ 相比之前的283只股票，现在有 {stats['total']:,} 只股票！")
        print(f"   增长了 {stats['total'] - 283:,} 只股票 ({((stats['total'] - 283) / 283 * 100):.1f}% 增长)")
        
    except Exception as e:
        print(f"❌ 获取全市场股票失败: {e}")
        return
    
    print("\n" + "=" * 60)
    print("2. 测试股票搜索功能")
    print("-" * 30)
    
    # 测试搜索功能
    test_queries = [
        "中石油",     # A股简称
        "601857",     # A股代码
        "腾讯",       # 港股
        "00700",      # 港股代码
        "苹果",       # 美股中文名
        "AAPL",       # 美股代码
        "Tesla",      # 美股英文名
        "茅台",       # A股简称
        "阿里",       # 中概股
        "美团"        # 港股
    ]
    
    for query in test_queries:
        print(f"\n🔍 搜索: '{query}'")
        try:
            results = universal_stock_fetcher.search_stocks(query, limit=5)
            if results:
                for i, result in enumerate(results, 1):
                    print(f"  {i}. {result['symbol']} - {result['name']} ({result['market']})")
            else:
                print("  无搜索结果")
        except Exception as e:
            print(f"  搜索失败: {e}")
    
    print("\n" + "=" * 60)
    print("3. 测试更新后的股票映射器")
    print("-" * 30)
    
    try:
        stock_mapper = StockMapper()
        
        # 获取全部股票
        all_mapped_stocks = stock_mapper.get_comprehensive_stocks()
        print(f"📈 股票映射器中的股票数量: {len(all_mapped_stocks):,} 只")
        
        # 获取市场统计
        mapper_stats = stock_mapper.get_market_statistics()
        print(f"📊 映射器统计:")
        print(f"  总计: {mapper_stats['total']:,} 只")
        
        # 测试搜索
        print(f"\n🔍 映射器搜索测试:")
        for query in ["中石油", "腾讯", "AAPL"][:3]:
            results = stock_mapper.search_stocks(query, limit=3)
            print(f"  '{query}': {len(results)} 个结果")
            for r in results[:2]:
                market = r.get('market', '未知')
                print(f"    - {r['symbol']} - {r['name']} ({market})")
        
        print("\n✅ 股票映射器测试完成")
        
    except Exception as e:
        print(f"❌ 股票映射器测试失败: {e}")
    
    print("\n" + "=" * 60)
    print("4. A股数量详细统计")
    print("-" * 30)
    
    try:
        # 获取A股详细信息
        a_stocks = universal_stock_fetcher.get_all_a_stocks(force_refresh=False)
        
        # 按交易所分类统计
        sh_count = sum(1 for code in a_stocks.keys() if code.endswith('.SH'))
        sz_count = sum(1 for code in a_stocks.keys() if code.endswith('.SZ'))
        
        # 按板块分类统计
        main_board_sh = sum(1 for code in a_stocks.keys() if code.startswith('600') or code.startswith('601') or code.startswith('603') or code.startswith('605'))
        sci_tech_board = sum(1 for code in a_stocks.keys() if code.startswith('688') or code.startswith('689'))
        sme_board = sum(1 for code in a_stocks.keys() if code.startswith('002'))
        startup_board = sum(1 for code in a_stocks.keys() if code.startswith('300'))
        sz_main_board = sum(1 for code in a_stocks.keys() if code.startswith('000'))
        
        print(f"🏛️ A股详细统计:")
        print(f"  上海交易所: {sh_count:,} 只")
        print(f"    - 主板: {main_board_sh:,} 只 (60x)")
        print(f"    - 科创板: {sci_tech_board:,} 只 (688/689)")
        print(f"  深圳交易所: {sz_count:,} 只")
        print(f"    - 主板: {sz_main_board:,} 只 (000)")
        print(f"    - 中小板: {sme_board:,} 只 (002)")
        print(f"    - 创业板: {startup_board:,} 只 (300)")
        print(f"  总计A股: {len(a_stocks):,} 只")
        
        print(f"\n📈 这比原来的283只股票增加了 {len(a_stocks) - 283:,} 只A股!")
        
    except Exception as e:
        print(f"❌ A股统计失败: {e}")

if __name__ == "__main__":
    test_universal_stock_system()
