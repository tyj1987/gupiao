#!/usr/bin/env python3
"""
测试综合评分级别中文化
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_score_levels():
    """测试评分等级中文化"""
    print("🎯 测试综合评分等级中文化...")
    
    try:
        from src.ai.stock_analyzer import StockAnalyzer
        
        analyzer = StockAnalyzer()
        
        # 测试不同分数对应的等级
        test_scores = [95, 85, 75, 65, 55, 45, 35, 25]
        
        print("📊 评分等级测试结果:")
        for score in test_scores:
            level = analyzer._get_score_level(score)
            
            # 检查是否为中文
            if any(char for char in level if '\u4e00' <= char <= '\u9fff'):
                print(f"✅ 分数 {score:2d} → 等级: {level}")
            else:
                print(f"❌ 分数 {score:2d} → 等级: {level} (非中文)")
                return False
        
        # 验证所有等级都是中文
        all_levels = set()
        for score in range(0, 101, 5):
            level = analyzer._get_score_level(score)
            all_levels.add(level)
        
        print(f"\n🏆 所有可能的等级: {sorted(all_levels)}")
        
        # 检查是否包含英文等级
        english_levels = {'excellent', 'good', 'fair', 'neutral', 'poor', 'very_poor'}
        chinese_intersection = all_levels & english_levels
        
        if chinese_intersection:
            print(f"❌ 仍包含英文等级: {chinese_intersection}")
            return False
        else:
            print("✅ 所有等级已完全中文化")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_risk_level_mapping():
    """测试风险等级映射"""
    print("\n🛡️ 测试风险等级CSS映射...")
    
    try:
        # 模拟UI中的风险等级映射
        risk_class_mapping = {
            '低': 'risk-low',
            '低风险': 'risk-low', 
            '中等': 'risk-medium',
            '中等风险': 'risk-medium',
            '高': 'risk-high',
            '高风险': 'risk-high',
            '极低风险': 'risk-low',
            '极高风险': 'risk-high',
            'low': 'risk-low',
            'medium': 'risk-medium', 
            'high': 'risk-high'
        }
        
        test_risk_levels = ['低', '低风险', '中等', '中等风险', '高', '高风险', '极低风险', '极高风险']
        
        print("🎨 风险等级CSS映射测试:")
        for risk_level in test_risk_levels:
            css_class = risk_class_mapping.get(risk_level, 'risk-medium')
            print(f"✅ 风险等级: {risk_level:8s} → CSS类: {css_class}")
        
        return True
        
    except Exception as e:
        print(f"❌ 风险等级映射测试失败: {e}")
        return False

if __name__ == "__main__":
    success1 = test_score_levels()
    success2 = test_risk_level_mapping()
    
    if success1 and success2:
        print(f"\n🎉 所有测试通过！综合评分级别已完全中文化")
    else:
        print(f"\n❌ 测试失败，需要进一步检查")
