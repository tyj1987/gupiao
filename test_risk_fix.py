#!/usr/bin/env python3
"""
测试风险等级修复效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ai.risk_manager import RiskManager
from src.ai.stock_analyzer import StockAnalyzer
from src.data.dynamic_stock_pool import DynamicStockPool
import pandas as pd

def test_risk_levels():
    """测试风险等级是否正确显示中文"""
    print("=" * 50)
    print("测试风险等级修复效果")
    print("=" * 50)
    
    # 1. 测试风险管理器
    print("\n1. 测试风险管理器:")
    risk_manager = RiskManager()
    
    # 测试不同风险等级
    test_cases = [
        (20, "低风险"),
        (40, "中等风险"), 
        (70, "高风险"),
        (85, "极高风险"),
        (10, "极低风险")
    ]
    
    for score, expected in test_cases:
        result = risk_manager._get_risk_level(score)
        print(f"  风险评分: {score} -> {result} (期望: {expected})")
    
    # 2. 测试动态股票池的风险筛选
    print("\n2. 测试股票池风险筛选:")
    try:
        pool = DynamicStockPool()
        
        # 测试不同风险过滤条件
        risk_filters = ['低风险', '中等风险', '高风险']
        for risk_filter in risk_filters:
            stocks = pool.get_stocks_by_criteria(risk_level=risk_filter, limit=3)
            print(f"  {risk_filter}股票: {len(stocks)}只")
            for stock in stocks[:2]:  # 只显示前2只
                print(f"    - {stock['code']} ({stock['name']}) - 风险: {stock.get('risk_level', '未知')}")
    
    except Exception as e:
        print(f"  股票池测试失败: {e}")
    
    # 3. 测试智能选股功能
    print("\n3. 测试智能选股:")
    try:
        analyzer = StockAnalyzer()
        
        # 使用一些主要股票进行测试
        test_stocks = ['000001', '000002', '600036', '600519', '000858']
        
        for risk_filter in ['低风险', '中等风险', '高风险']:
            result = analyzer.screen_stocks(test_stocks, risk_level=risk_filter)
            if result:
                print(f"  {risk_filter}筛选结果: {len(result)}只股票")
                for stock in result[:2]:  # 只显示前2只
                    risk_info = stock.get('risk_assessment', {})
                    print(f"    - {stock['symbol']}: {risk_info.get('level', '未知风险')}")
            else:
                print(f"  {risk_filter}筛选结果: 0只股票")
    
    except Exception as e:
        print(f"  智能选股测试失败: {e}")
    
    print("\n" + "=" * 50)
    print("测试完成！")

if __name__ == "__main__":
    test_risk_levels()
