#!/usr/bin/env python3
"""智能选股风险筛选测试"""

import sys
sys.path.append('.')

from src.ai.stock_analyzer import StockAnalyzer

def test_risk_based_screening():
    """测试基于风险等级的智能选股功能"""
    
    print("🎯 智能选股风险筛选测试")
    print("=" * 80)
    
    # 创建股票分析器
    analyzer = StockAnalyzer()
    
    # 测试股票池
    test_stocks = [
        '600036.SH', '601318.SH', '000858.SZ', '600519.SH',
        '000002.SZ', '002415.SZ', '600276.SH', '000661.SZ'
    ]
    
    # 测试不同风险偏好的筛选
    risk_preferences = ['低风险', '中等风险', '高风险']
    
    for risk_pref in risk_preferences:
        print(f"\n🔍 测试风险偏好: {risk_pref}")
        print("-" * 50)
        
        try:
            # 进行筛选
            results = analyzer.screen_stocks(
                stock_list=test_stocks,
                min_score=0,  # 降低评分要求，关注风险筛选
                risk_level=risk_pref,
                market_cap="不限"
            )
            
            if results:
                print(f"✅ 找到 {len(results)} 只符合条件的股票:")
                for stock in results:
                    code = stock.get('code', 'N/A')
                    name = stock.get('name', 'N/A')
                    score = stock.get('score', 0)
                    risk_level = stock.get('risk_level', 'N/A')
                    print(f"   📊 {code} - {name}: 评分={score:.1f}, 风险={risk_level}")
            else:
                print(f"❌ 未找到符合 {risk_pref} 偏好的股票")
                
        except Exception as e:
            print(f"❌ 测试 {risk_pref} 筛选时出错: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n✅ 智能选股风险筛选测试完成")

if __name__ == "__main__":
    test_risk_based_screening()
