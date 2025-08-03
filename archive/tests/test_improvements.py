#!/usr/bin/env python3
"""
测试改进后的功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def test_stock_mapper():
    """测试股票代码与名称映射"""
    print("🧪 测试股票代码与名称映射")
    print("=" * 50)
    
    from src.data.stock_mapper import stock_mapper
    
    # 测试获取股票名称
    test_symbols = ['000001.SZ', '600519.SH', 'AAPL', 'TSLA']
    for symbol in test_symbols:
        name = stock_mapper.get_stock_name(symbol)
        print(f"📊 {symbol} -> {name}")
    
    # 测试获取总股票数
    all_stocks = stock_mapper.get_all_stocks()
    print(f"\n📈 总股票数: {len(all_stocks)}")
    
    # 按市场分类统计
    a_stocks = stock_mapper.get_stocks_by_market("中国A股")
    us_stocks = stock_mapper.get_stocks_by_market("美股")
    print(f"🇨🇳 中国A股: {len(a_stocks)} 只")
    print(f"🇺🇸 美股: {len(us_stocks)} 只")

def test_enhanced_stock_pool():
    """测试增强的动态股票池"""
    print("\n🧪 测试增强的动态股票池")
    print("=" * 50)
    
    from src.data.dynamic_stock_pool import DynamicStockPool
    
    pool_manager = DynamicStockPool()
    
    # 测试获取所有股票
    all_stocks = pool_manager.get_all_stocks()
    print(f"📊 所有可用股票数量: {len(all_stocks)}")
    
    # 测试股票池统计
    stats = pool_manager.get_pool_statistics()
    print(f"📈 股票池统计: {stats}")
    
    # 测试不同市场的股票池
    mixed_pool = pool_manager.get_stock_pool(market="混合", pool_size=20)
    china_pool = pool_manager.get_stock_pool(market="中国A股", pool_size=15)
    us_pool = pool_manager.get_stock_pool(market="美股", pool_size=10)
    
    print(f"🌍 混合市场股票池 (20只): {len(mixed_pool)} 只")
    print(f"🇨🇳 中国A股股票池 (15只): {len(china_pool)} 只")
    print(f"🇺🇸 美股股票池 (10只): {len(us_pool)} 只")
    
    # 显示部分股票名称
    from src.data.stock_mapper import stock_mapper
    print(f"混合市场前5只股票:")
    for symbol in mixed_pool[:5]:
        name = stock_mapper.get_stock_name(symbol)
        print(f"  • {symbol} - {name}")

def test_market_data():
    """测试市场数据获取"""
    print("\n🧪 测试市场数据获取")
    print("=" * 50)
    
    try:
        from src.data.market_data_fetcher import market_data_fetcher
        
        # 测试获取市场指数
        indices = market_data_fetcher.get_market_indices()
        print(f"📊 获取到 {len(indices)} 个市场指数:")
        
        for name, data in indices.items():
            change_sign = "+" if data['change'] >= 0 else ""
            print(f"  📈 {name}: {data['current']:.2f} ({change_sign}{data['change_pct']:.2f}%)")
        
        # 测试获取热门板块
        hot_sectors = market_data_fetcher.get_hot_sectors()
        print(f"\n🔥 获取到 {len(hot_sectors)} 个热门板块:")
        for sector in hot_sectors[:3]:  # 显示前3个
            print(f"  🏢 {sector['板块']}: {sector['涨跌幅']} (领涨: {sector['领涨股']})")
            
    except Exception as e:
        print(f"❌ 市场数据获取失败: {e}")
        print("💡 这可能是因为网络连接或API限制，这是正常的")

def main():
    """运行所有测试"""
    print("🚀 开始测试改进后的功能")
    print("=" * 70)
    
    test_stock_mapper()
    test_enhanced_stock_pool()
    test_market_data()
    
    print("\n✅ 所有测试完成！")
    print("=" * 70)

if __name__ == "__main__":
    main()
