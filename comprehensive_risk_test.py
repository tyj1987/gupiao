#!/usr/bin/env python3
"""全面的风险分析测试脚本"""

import sys
sys.path.append('.')

from src.ai.risk_manager import RiskManager
from src.data.data_fetcher import DataFetcher

def comprehensive_risk_test():
    """全面的风险分析测试"""
    
    print("🔍 全面风险分析测试")
    print("=" * 80)
    
    # 创建实例
    risk_manager = RiskManager()
    data_fetcher = DataFetcher()
    
    # 多样化股票池 - 不同行业、不同特性的股票
    test_stocks = [
        # 银行股（预期低风险）
        ('600036.SH', '招商银行'),
        ('601318.SH', '中国平安'),
        
        # 消费股（预期低到中等风险）
        ('000858.SZ', '五粮液'),
        ('600519.SH', '贵州茅台'),
        
        # 地产股（预期中等到高风险）
        ('000002.SZ', '万科A'),
        
        # 科技股（预期高风险）
        ('002415.SZ', '海康威视'),
        ('600276.SH', '恒瑞医药'),
        
        # 成长股（预期高到极高风险）
        ('000661.SZ', '长春高新'),
    ]
    
    results = []
    
    for code, name in test_stocks:
        print(f"\n📊 分析 {code} - {name}")
        print("-" * 50)
        
        try:
            # 获取数据
            data = data_fetcher.get_stock_data(code, period='6m')
            if data is None or data.empty:
                print(f"❌ 无法获取 {code} 数据")
                continue
            
            # 风险评估
            risk_result = risk_manager.assess_risk(data)
            
            if 'overall_risk' in risk_result:
                overall_risk = risk_result['overall_risk']
                score = overall_risk.get('score', 0)
                level = overall_risk.get('level', '未知')
                
                # 转换英文level为中文
                level_map = {
                    'very_low': '极低风险',
                    'low': '低风险', 
                    'medium': '中等风险',
                    'high': '高风险',
                    'very_high': '极高风险'
                }
                chinese_level = level_map.get(level, level)
                
                results.append({
                    'code': code,
                    'name': name,
                    'score': score,
                    'level': chinese_level,
                    'english_level': level
                })
                
                print(f"💰 风险得分: {score:.2f}")
                print(f"🏷️ 风险等级: {chinese_level}")
                
                # 显示各项风险分数
                if 'market_risk' in risk_result:
                    market_score = risk_result['market_risk'].get('score', 0)
                    print(f"📈 市场风险: {market_score:.1f}")
                
                if 'liquidity_risk' in risk_result:
                    liquidity_score = risk_result['liquidity_risk'].get('score', 0)
                    print(f"💧 流动性风险: {liquidity_score:.1f}")
                
                if 'volatility_risk' in risk_result:
                    volatility_score = risk_result['volatility_risk'].get('score', 0)
                    print(f"📊 波动性风险: {volatility_score:.1f}")
                    
            else:
                print(f"❌ 风险评估失败")
                
        except Exception as e:
            print(f"❌ 分析 {code} 时出错: {e}")
            continue
    
    # 统计分析
    if results:
        print(f"\n📈 风险分析统计")
        print("=" * 80)
        
        scores = [r['score'] for r in results]
        print(f"📊 风险得分分布:")
        print(f"   最高得分: {max(scores):.2f}")
        print(f"   最低得分: {min(scores):.2f}")
        print(f"   平均得分: {sum(scores)/len(scores):.2f}")
        print(f"   得分范围: {max(scores) - min(scores):.2f}")
        
        # 风险等级分布
        level_counts = {}
        for r in results:
            level = r['level']
            level_counts[level] = level_counts.get(level, 0) + 1
        
        print(f"\n🏷️ 风险等级分布:")
        for level, count in level_counts.items():
            percentage = (count / len(results)) * 100
            print(f"   {level}: {count} 只股票 ({percentage:.1f}%)")
        
        # 按风险等级分组显示
        print(f"\n📋 按风险等级分组:")
        risk_levels = ['极低风险', '低风险', '中等风险', '高风险', '极高风险']
        for level in risk_levels:
            stocks_in_level = [r for r in results if r['level'] == level]
            if stocks_in_level:
                print(f"\n🔸 {level}:")
                for stock in stocks_in_level:
                    print(f"   📊 {stock['code']} - {stock['name']}: {stock['score']:.2f}")
        
        # 检查阈值分布是否合理
        print(f"\n🎯 风险阈值验证:")
        print(f"   极低风险 (≥75): {len([r for r in results if r['score'] >= 75])} 只")
        print(f"   低风险 (60-75): {len([r for r in results if 60 <= r['score'] < 75])} 只")
        print(f"   中等风险 (40-60): {len([r for r in results if 40 <= r['score'] < 60])} 只") 
        print(f"   高风险 (25-40): {len([r for r in results if 25 <= r['score'] < 40])} 只")
        print(f"   极高风险 (<25): {len([r for r in results if r['score'] < 25])} 只")
    
    print(f"\n✅ 全面风险分析测试完成")
    return results

if __name__ == "__main__":
    comprehensive_risk_test()
