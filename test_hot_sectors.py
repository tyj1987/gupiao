#!/usr/bin/env python3
"""
测试热点板块数据显示
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.market_data_fetcher import market_data_fetcher

def test_hot_sectors():
    """测试热点板块数据"""
    print("🔥 测试热点板块数据获取...")
    
    try:
        # 获取热点板块数据
        hot_sectors = market_data_fetcher.get_hot_sectors()
        
        print(f"✅ 获取到 {len(hot_sectors)} 个热点板块")
        
        if not hot_sectors:
            print("❌ 热点板块数据为空")
            return False
            
        # 验证数据格式
        sample_sector = hot_sectors[0]
        required_fields = ['name', 'change_pct', 'volume']
        
        print(f"\n📊 第一个板块示例: {sample_sector}")
        
        # 检查必须字段
        for field in required_fields:
            if field in sample_sector:
                print(f"✅ {field}: {sample_sector[field]}")
            else:
                print(f"❌ 缺少字段: {field}")
                return False
        
        # 显示所有板块的涨跌情况
        print(f"\n📈 热点板块排行:")
        for i, sector in enumerate(hot_sectors[:6], 1):
            change_pct = sector.get('change_pct', 0)
            icon = "📈" if change_pct > 0 else "📉" if change_pct < 0 else "➖"
            print(f"{i}. {sector.get('name', 'Unknown')} {icon} {change_pct:+.2f}% (成交:{sector.get('volume', 0):.1f}亿)")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_hot_sectors()
