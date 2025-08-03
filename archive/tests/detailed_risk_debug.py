#!/usr/bin/env python3
"""详细风险分析调试脚本 - 深入分析每只股票的风险构成"""

import sys
import pandas as pd
sys.path.append('.')

from src.ai.stock_analyzer import StockAnalyzer
from src.ai.risk_manager import RiskManager

def detailed_risk_analysis():
    """详细分析每只股票的风险构成"""
    
    # 创建风险管理器和股票分析器
    analyzer = StockAnalyzer()
    risk_manager = RiskManager()
    
    # 多样化股票池
    stocks = [
        # 银行股 - 预期低风险
        '600036.SH',  # 招商银行
        '601318.SH',  # 中国平安
        
        # 消费股 - 预期低到中等风险
        '000858.SZ',  # 五粮液
        '600519.SH',  # 贵州茅台
        
        # 地产股 - 预期中等到高风险
        '000002.SZ',  # 万科A
        
        # 科技股 - 预期高风险
        '002415.SZ',  # 海康威视
        '600276.SH',  # 恒瑞医药
        '000661.SZ',  # 长春高新
        
        # 新能源 - 预期极高风险
        '300750.SZ',  # 宁德时代
        '002594.SZ',  # 比亚迪
    ]
    
    print("🔍 详细风险分析报告")
    print("=" * 80)
    
    # 收集所有股票的风险数据
    all_scores = []
    all_levels = []
    
    for stock in stocks:
        print(f"\n📊 分析股票: {stock}")
        print("-" * 50)
        
        try:
            # 获取股票数据
            data = analyzer.data_fetcher.get_stock_data(stock, period='6m')
            if data is None or data.empty:
                print(f"⚠️ 无法获取 {stock} 数据，跳过")
                continue
            
            # 直接调用风险管理器分析单只股票
            current_price = data['close'].iloc[-1]
            volume = data['vol'].iloc[-1] if 'vol' in data.columns else 0
            market_cap = current_price * volume * 100  # 简化市值计算
            
            # 计算各个风险组件
            market_risk = risk_manager._assess_market_risk(data)
            liquidity_risk = risk_manager._assess_liquidity_risk(data)
            volatility_risk = risk_manager._assess_volatility_risk(data)
            fundamental_risk = risk_manager._assess_fundamental_risk(stock, data)
            technical_risk = risk_manager._assess_technical_risk(data)
            concentration_risk = risk_manager._assess_concentration_risk(market_cap)
            
            # 计算总体风险得分
            overall_score = risk_manager.assess_risk(stock, data)
            risk_level = risk_manager._get_risk_level(overall_score)
            
            all_scores.append(overall_score)
            all_levels.append(risk_level)
            
            print(f"💰 当前价格: {current_price:.2f}")
            print(f"📈 市场风险: {market_risk:.2f}")
            print(f"💧 流动性风险: {liquidity_risk:.2f}")
            print(f"📊 波动性风险: {volatility_risk:.2f}")
            print(f"🏢 基本面风险: {fundamental_risk:.2f}")
            print(f"📉 技术面风险: {technical_risk:.2f}")
            print(f"🎯 集中度风险: {concentration_risk:.2f}")
            print(f"🎯 总体风险得分: {overall_score:.2f}")
            print(f"🏷️ 风险等级: {risk_level}")
            
            # 分析风险等级分布
            print(f"\n🔍 风险等级阈值分析:")
            print(f"   得分 {overall_score:.2f} 对应等级判定:")
            if overall_score >= 75:
                print(f"   ✅ >= 75 → 极低风险")
            elif overall_score >= 60:
                print(f"   ✅ >= 60 → 低风险")
            elif overall_score >= 40:
                print(f"   ✅ >= 40 → 中等风险")
            elif overall_score >= 25:
                print(f"   ✅ >= 25 → 高风险")
            else:
                print(f"   ✅ < 25 → 极高风险")
            
        except Exception as e:
            print(f"❌ 分析股票 {stock} 时出错: {e}")
            continue
    
    # 统计分析
    if all_scores:
        print(f"\n📈 风险得分统计")
        print("=" * 50)
        print(f"最高得分: {max(all_scores):.2f}")
        print(f"最低得分: {min(all_scores):.2f}")
        print(f"平均得分: {sum(all_scores)/len(all_scores):.2f}")
        print(f"得分范围: {max(all_scores) - min(all_scores):.2f}")
        
        print(f"\n📊 风险等级分布")
        print("=" * 50)
        level_counts = {}
        for level in all_levels:
            level_counts[level] = level_counts.get(level, 0) + 1
        
        for level, count in level_counts.items():
            percentage = (count / len(all_levels)) * 100
            print(f"{level}: {count} 只股票 ({percentage:.1f}%)")
    
    # 测试风险等级筛选
    print(f"\n🎯 测试风险等级筛选")
    print("=" * 50)
    
    risk_levels = ['低风险', '中等风险', '高风险']
    for target_risk in risk_levels:
        print(f"\n--- 筛选 {target_risk} 股票 ---")
        try:
            # 使用stock_analyzer的筛选功能
            results = analyzer.screen_stocks(
                stock_list=stocks,
                min_score=0,
                risk_level=target_risk,
                market_cap="不限"
            )
            
            if results:
                print(f"找到 {len(results)} 只符合条件的股票:")
                for rec in results:
                    print(f"  📊 {rec['code']} - {rec.get('name', 'N/A')}: "
                          f"评分={rec['score']:.1f}, 风险={rec['risk_level']}")
            else:
                print("🔍 未找到符合条件的股票")
        except Exception as e:
            print(f"❌ 筛选 {target_risk} 股票时出错: {e}")

if __name__ == "__main__":
    detailed_risk_analysis()
