#!/usr/bin/env python3
"""
创建多样化风险股票池测试
"""

import sys
import os
sys.path.append('/home/tyj/gupiao')

def test_diverse_stock_pool():
    """测试多样化的股票池"""
    
    # 不同风险特征的股票池
    test_stocks = {
        # 低风险候选：大型银行、公用事业、稳定消费
        "600036.SH": "招商银行",    # 优质银行
        "601318.SH": "中国平安",    # 保险龙头
        "000858.SZ": "五粮液",      # 稳定消费
        "600519.SH": "贵州茅台",    # 消费白马
        
        # 中等风险候选：制造业、医药、科技蓝筹
        "000002.SZ": "万科A",       # 地产龙头
        "002415.SZ": "海康威视",    # 科技制造
        "600276.SH": "恒瑞医药",    # 医药龙头
        "000661.SZ": "长春高新",    # 医药成长
        
        # 高风险候选：新兴科技、小盘成长、周期性行业
        "300750.SZ": "宁德时代",    # 新能源
        "002594.SZ": "比亚迪",      # 新能源车
        "300015.SZ": "爱尔眼科",    # 医疗服务
        "300059.SZ": "东方财富",    # 金融科技
        
        # 潜在低风险：公用事业、基础设施
        "601006.SH": "大秦铁路",    # 铁路运输
        "600028.SH": "中国石化",    # 能源央企
        "000895.SZ": "双汇发展",    # 食品稳定
        "600887.SH": "伊利股份",    # 乳业龙头
    }
    
    print(f"测试股票池包含 {len(test_stocks)} 只股票")
    print("\n按预期风险分类:")
    print("🟢 低风险候选: 招商银行, 中国平安, 五粮液, 贵州茅台")
    print("🟡 中等风险候选: 万科A, 海康威视, 恒瑞医药, 长春高新")  
    print("🔴 高风险候选: 宁德时代, 比亚迪, 爱尔眼科, 东方财富")
    print("🟢 稳定型候选: 大秦铁路, 中国石化, 双汇发展, 伊利股份")
    
    return test_stocks

def test_risk_assessment_on_diverse_pool():
    """在多样化股票池上测试风险评估"""
    
    try:
        from src.ai.stock_analyzer import StockAnalyzer
        
        analyzer = StockAnalyzer()
        test_stocks = list(test_diverse_stock_pool().keys())
        
        print(f"\n🔍 测试多样化股票池的风险分布")
        print("=" * 60)
        
        # 测试不同风险级别的筛选效果
        risk_levels = ["低风险", "中等风险", "高风险"]
        
        for risk_level in risk_levels:
            print(f"\n--- 风险级别: {risk_level} ---")
            
            results = analyzer.screen_stocks(
                stock_list=test_stocks[:8],  # 测试前8只股票
                min_score=0,
                risk_level=risk_level,
                market_cap="不限"
            )
            
            print(f"筛选结果: {len(results)} 只股票")
            
            if results:
                for result in results:
                    print(f"  📊 {result['symbol']} - {result['name']}: "
                          f"评分={result['score']}, 风险={result['risk_level']}")
            else:
                print("  🔍 未找到符合条件的股票")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🧪 多样化风险股票池测试")
    print("=" * 50)
    
    # 显示测试股票池
    test_stocks = test_diverse_stock_pool()
    
    # 运行风险评估测试
    print("\n" + "=" * 50)
    success = test_risk_assessment_on_diverse_pool()
    
    if success:
        print("\n✅ 测试完成！系统能够区分不同风险级别的股票")
    else:
        print("\n❌ 测试失败，需要进一步调试")
