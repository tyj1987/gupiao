#!/usr/bin/env python3
"""
测试动态股票池功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.data.dynamic_stock_pool import DynamicStockPool

def test_dynamic_stock_pool():
    """测试动态股票池功能"""
    print("🧪 测试动态股票池功能")
    print("=" * 50)
    
    # 创建动态股票池管理器
    pool_manager = DynamicStockPool()
    
    # 测试1: 混合市场，所有行业
    print("\n📊 测试1: 混合市场，所有行业，30只股票")
    stocks1 = pool_manager.get_stock_pool(
        market="混合",
        sector="全部", 
        market_cap="不限",
        pool_size=30
    )
    print(f"生成股票数量: {len(stocks1)}")
    print(f"股票列表: {stocks1[:10]}..." if len(stocks1) > 10 else f"股票列表: {stocks1}")
    
    # 测试2: 中国A股，科技行业
    print("\n🇨🇳 测试2: 中国A股，科技行业")
    stocks2 = pool_manager.get_stock_pool(
        market="中国A股",
        sector="科技",
        market_cap="不限",
        pool_size=10
    )
    print(f"生成股票数量: {len(stocks2)}")
    print(f"股票列表: {stocks2}")
    
    # 测试3: 美股，科技行业
    print("\n🇺🇸 测试3: 美股，科技行业")
    stocks3 = pool_manager.get_stock_pool(
        market="美股",
        sector="科技",
        market_cap="不限",
        pool_size=10
    )
    print(f"生成股票数量: {len(stocks3)}")
    print(f"股票列表: {stocks3}")
    
    # 测试4: 大盘股偏好
    print("\n📈 测试4: 大盘股偏好")
    stocks4 = pool_manager.get_stock_pool(
        market="混合",
        sector="全部",
        market_cap="大盘股",
        pool_size=15
    )
    print(f"生成股票数量: {len(stocks4)}")
    print(f"股票列表: {stocks4}")
    
    # 测试5: 获取可用行业
    print("\n🏢 测试5: 获取可用行业")
    sectors_mixed = pool_manager.get_available_sectors("混合")
    sectors_china = pool_manager.get_available_sectors("中国A股")
    sectors_us = pool_manager.get_available_sectors("美股")
    
    print(f"混合市场行业: {sectors_mixed}")
    print(f"中国A股行业: {sectors_china}")
    print(f"美股行业: {sectors_us}")
    
    # 测试6: 随机股票
    print("\n🎲 测试6: 获取随机股票")
    random_stocks = pool_manager.get_random_stocks(count=12)
    print(f"随机股票数量: {len(random_stocks)}")
    print(f"随机股票列表: {random_stocks}")
    
    # 测试7: 多次生成验证随机性
    print("\n🔄 测试7: 验证随机性（生成3次）")
    for i in range(3):
        stocks = pool_manager.get_stock_pool(
            market="混合",
            sector="全部",
            market_cap="不限",
            pool_size=10
        )
        print(f"第{i+1}次: {stocks[:5]}...")
    
    print("\n✅ 动态股票池测试完成！")

if __name__ == "__main__":
    test_dynamic_stock_pool()
