#!/usr/bin/env python3
"""
测试中国银行股票搜索和分析功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data.stock_mapper import stock_mapper
from src.ai.stock_analyzer import StockAnalyzer
from src.data.data_fetcher import DataFetcher

def test_bank_stock_search():
    """测试银行股票搜索功能"""
    print("=" * 60)
    print("测试银行股票搜索和分析功能")
    print("=" * 60)
    
    # 1. 测试中国银行搜索
    print("\n1. 测试中国银行搜索:")
    print("-" * 30)
    
    # 代码搜索
    print("📊 代码搜索:")
    results = stock_mapper.search_stocks('601988')
    for r in results:
        print(f"  ✓ {r['symbol']} - {r['name']} (匹配: {r['match_type']})")
    
    # 名称搜索
    print("\n🏦 名称搜索:")
    results = stock_mapper.search_stocks('中国银行')
    for r in results:
        print(f"  ✓ {r['symbol']} - {r['name']} (匹配: {r['match_type']})")
    
    # 部分匹配搜索
    print("\n🔍 部分匹配 '银行':")
    results = stock_mapper.search_stocks('银行', limit=15)
    for r in results[:10]:  # 只显示前10个
        print(f"  ✓ {r['symbol']} - {r['name']}")
    if len(results) > 10:
        print(f"  ... 还有 {len(results) - 10} 个结果")
    
    # 2. 测试代码名称转换
    print("\n\n2. 测试代码名称转换:")
    print("-" * 30)
    
    test_cases = [
        '601988.SH',  # 中国银行
        '601398.SH',  # 工商银行
        '601939.SH',  # 建设银行
        '600036.SH',  # 招商银行
        '000001.SZ'   # 平安银行
    ]
    
    for code in test_cases:
        name = stock_mapper.get_stock_name(code)
        reverse_code = stock_mapper.get_stock_symbol(name)
        status = "✓" if reverse_code == code else "⚠️"
        print(f"  {status} {code} -> {name} -> {reverse_code}")
    
    # 3. 测试股票数据获取
    print("\n\n3. 测试中国银行数据获取:")
    print("-" * 30)
    
    try:
        data_fetcher = DataFetcher()
        print("  🔄 正在获取中国银行(601988.SH)数据...")
        
        stock_data = data_fetcher.get_stock_data('601988.SH', period='1m')
        if stock_data is not None and not stock_data.empty:
            print(f"  ✅ 成功获取 {len(stock_data)} 天的数据")
            print(f"  📅 数据时间范围: {stock_data.index[0].date()} 到 {stock_data.index[-1].date()}")
            print(f"  💰 最新价格: {stock_data['close'].iloc[-1]:.2f}")
            print(f"  📈 近期涨跌: {((stock_data['close'].iloc[-1] / stock_data['close'].iloc[0] - 1) * 100):+.2f}%")
        else:
            print("  ❌ 无法获取股票数据")
    except Exception as e:
        print(f"  ❌ 数据获取失败: {e}")
    
    # 4. 测试智能股票分析
    print("\n\n4. 测试中国银行智能分析:")
    print("-" * 30)
    
    try:
        analyzer = StockAnalyzer()
        print("  🔄 正在分析中国银行...")
        
        # 使用较短的数据周期以提高测试速度
        analysis_result = analyzer.analyze_stock('601988.SH')
        
        if analysis_result:
            print("  ✅ 分析完成!")
            
            # 显示基本信息
            basic_info = analysis_result.get('basic_info', {})
            print(f"  📊 股票名称: {basic_info.get('name', '中国银行')}")
            print(f"  🏷️  股票代码: {basic_info.get('symbol', '601988.SH')}")
            
            # 显示评分
            overall_score = analysis_result.get('overall_score', {})
            if isinstance(overall_score, dict):
                score = overall_score.get('score', 0)
                level = overall_score.get('level', '未知')
                print(f"  ⭐ 综合评分: {score:.1f}分 ({level})")
            
            # 显示风险评估
            risk_assessment = analysis_result.get('risk_assessment', {})
            risk_level = risk_assessment.get('level', '未知风险')
            risk_score = risk_assessment.get('score', 0)
            print(f"  ⚠️  风险评估: {risk_level} (评分: {risk_score:.1f})")
            
            # 显示投资建议
            recommendation = analysis_result.get('recommendation', {})
            action = recommendation.get('action', '观望')
            confidence = recommendation.get('confidence', 0)
            reason = recommendation.get('reason', '无特殊说明')
            print(f"  💡 投资建议: {action} (置信度: {confidence:.1f}%)")
            print(f"  📝 建议理由: {reason}")
            
        else:
            print("  ❌ 分析失败")
            
    except Exception as e:
        print(f"  ❌ 分析失败: {e}")
    
    # 5. 测试智能建议
    print("\n\n5. 测试智能建议功能:")
    print("-" * 30)
    
    suggestions = stock_mapper.get_stock_suggestions('中国')
    print("  💡 输入 '中国' 的建议:")
    for suggestion in suggestions[:5]:
        print(f"    → {suggestion}")
    
    suggestions = stock_mapper.get_stock_suggestions('601')
    print("\n  💡 输入 '601' 的建议:")
    for suggestion in suggestions[:5]:
        print(f"    → {suggestion}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！中国银行股票搜索和分析功能已优化")
    print("=" * 60)

if __name__ == "__main__":
    test_bank_stock_search()
