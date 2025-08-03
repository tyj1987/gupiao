#!/usr/bin/env python3
"""
风险分析调试脚本
检查风险评估系统的问题
"""

import sys
import os
sys.path.append('/home/tyj/gupiao')

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def test_enhanced_search_functionality():
    """测试增强的股票搜索功能"""
    print("=== 增强股票搜索功能测试 ===")
    
    try:
        from src.data.stock_mapper import stock_mapper
        from src.data.stock_search_enhancer import stock_search_enhancer
        from src.data.data_fetcher import DataFetcher
        from src.ai.risk_manager import RiskManager
        
        data_fetcher = DataFetcher()
        risk_manager = RiskManager()
        
        # 测试难搜索的股票
        difficult_searches = [
            "中石油",     # 简称
            "ZGSYC",      # 拼音缩写
            "石油公司",   # 部分描述
            "601857",     # 纯代码
            "中国石油化工", # 相似名称
            "华为",       # 未上市公司
            "腾讯",       # 港股
            "阿里",       # 港股+美股
            "Tesla",      # 美股
            "苹果",       # 美股中文名
            "不存在的公司", # 无效搜索
        ]
        
        print(f"测试 {len(difficult_searches)} 个困难搜索场景\n")
        
        for i, query in enumerate(difficult_searches, 1):
            print(f"{i}. 搜索: '{query}'")
            
            # 使用增强搜索
            enhanced_results = stock_search_enhancer.enhanced_search(
                query, stock_mapper, data_fetcher
            )
            
            print(f"   找到 {len(enhanced_results)} 个结果")
            
            for j, result in enumerate(enhanced_results[:3], 1):
                symbol = result['symbol']
                name = result['name']
                search_type = result['search_type']
                market = result['market']
                data_available = result.get('data_available', 'Unknown')
                latest_price = result.get('latest_price', 'N/A')
                
                status_icon = "✅" if data_available else "❌"
                print(f"   {j}. {status_icon} {symbol} - {name}")
                print(f"      � 搜索类型: {search_type}")
                print(f"      🏢 市场: {market}")
                if latest_price and latest_price != 'N/A':
                    print(f"      💰 最新价格: {latest_price:.2f}")
                
                # 获取风险信息（仅对有数据的股票）
                if data_available and symbol.endswith(('.SH', '.SZ')):
                    try:
                        stock_data = data_fetcher.get_stock_data(symbol, period='1m')
                        if stock_data is not None and not stock_data.empty:
                            risk_result = risk_manager.assess_risk(stock_data)
                            overall_risk = risk_result.get('overall_risk', {})
                            risk_level = overall_risk.get('level', 'N/A')
                            print(f"      ⚡ 风险等级: {risk_level}")
                    except:
                        pass
            
            # 显示搜索建议
            suggestions = stock_search_enhancer.suggest_alternatives(query, stock_mapper)
            if suggestions:
                print(f"   💡 搜索建议: {suggestions[:2]}")
            
            # 显示统计信息
            stats = stock_search_enhancer.get_search_statistics(query, stock_mapper)
            print(f"   � 统计: 总计{stats['total_results']}个, 有数据{stats['data_available_count']}个")
            print()
        
        print("✅ 增强搜索功能测试完成")
        
    except Exception as e:
        print(f"❌ 增强搜索功能测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_search_precision_and_coverage():
    """测试搜索精度和覆盖率"""
    print("=== 搜索精度和覆盖率测试 ===")
    
    try:
        from src.data.stock_mapper import stock_mapper
        
        # 测试精确匹配
        precision_tests = [
            ("601857.SH", "中国石油"),
            ("600028.SH", "中国石化"),
            ("600519.SH", "贵州茅台"),
            ("000001.SZ", "平安银行"),
            ("000002.SZ", "万科A"),
            ("300750.SZ", "宁德时代"),
            ("002594.SZ", "比亚迪"),
        ]
        
        print("精确匹配测试:")
        success_count = 0
        
        for code, expected_name in precision_tests:
            # 通过代码搜索
            results = stock_mapper.search_stocks(code, limit=1)
            if results and results[0]['symbol'] == code:
                actual_name = results[0]['name']
                if expected_name in actual_name or actual_name in expected_name:
                    print(f"  ✅ {code}: {actual_name}")
                    success_count += 1
                else:
                    print(f"  ⚠️ {code}: 期望'{expected_name}', 实际'{actual_name}'")
            else:
                print(f"  ❌ {code}: 未找到精确匹配")
        
        print(f"精确匹配成功率: {success_count}/{len(precision_tests)} ({success_count/len(precision_tests)*100:.1f}%)")
        
        # 测试搜索覆盖率
        print("\n搜索覆盖率测试:")
        all_stocks = stock_mapper.get_comprehensive_stocks()
        total_stocks = len(all_stocks)
        
        # 随机测试一些股票的搜索能力
        import random
        sample_stocks = random.sample(list(all_stocks.items()), min(10, total_stocks))
        
        searchable_count = 0
        for code, name in sample_stocks:
            # 尝试通过名称搜索
            name_results = stock_mapper.search_stocks(name, limit=5)
            # 尝试通过代码搜索
            code_results = stock_mapper.search_stocks(code, limit=5)
            
            found_by_name = any(r['symbol'] == code for r in name_results)
            found_by_code = any(r['symbol'] == code for r in code_results)
            
            if found_by_name or found_by_code:
                searchable_count += 1
                status = "✅"
                methods = []
                if found_by_name:
                    methods.append("名称")
                if found_by_code:
                    methods.append("代码")
                print(f"  {status} {code} ({name}) - 可通过{'/'.join(methods)}搜索")
            else:
                print(f"  ❌ {code} ({name}) - 搜索失败")
        
        print(f"搜索覆盖率: {searchable_count}/{len(sample_stocks)} ({searchable_count/len(sample_stocks)*100:.1f}%)")
        print(f"总股票数据库大小: {total_stocks} 只股票")
        
    except Exception as e:
        print(f"❌ 搜索精度测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_risk_manager():
    """测试风险管理器"""
    print("=== 风险管理器测试 ===")
    
    try:
        from src.ai.risk_manager import RiskManager
        from src.data.data_fetcher import DataFetcher
        
        # 初始化
        risk_manager = RiskManager()
        data_fetcher = DataFetcher()
        
        # 测试股票列表 - 包含不同风险级别的股票（使用扩展股票池）
        test_stocks = [
            "601857.SH",  # 中国石油
            "600028.SH",  # 中国石化
            "601398.SH",  # 工商银行
            "600519.SH",  # 贵州茅台
            "000002.SZ",  # 万科A
            "300750.SZ",  # 宁德时代
            "002594.SZ",  # 比亚迪
            "000063.SZ",  # 中兴通讯
            "002415.SZ",  # 海康威视
            "000661.SZ",  # 长春高新
        ]
        
        print(f"测试股票: {test_stocks}")
        print()
        
        for stock_code in test_stocks:
            print(f"--- 分析 {stock_code} ---")
            
            # 获取股票数据
            try:
                stock_data = data_fetcher.get_stock_data(stock_code, period='6m')
                if stock_data is None or stock_data.empty:
                    print(f"❌ 无法获取 {stock_code} 的数据")
                    continue
                
                print(f"✅ 数据获取成功，记录数: {len(stock_data)}")
                print(f"价格范围: {stock_data['close'].min():.2f} - {stock_data['close'].max():.2f}")
                
                # 计算收益率统计
                returns = stock_data['close'].pct_change().dropna()
                if len(returns) > 0:
                    print(f"日收益率统计:")
                    print(f"  平均: {returns.mean():.4f}")
                    print(f"  标准差: {returns.std():.4f}")
                    print(f"  最大: {returns.max():.4f}")
                    print(f"  最小: {returns.min():.4f}")
                
                # 进行风险评估
                risk_result = risk_manager.assess_risk(stock_data)
                
                # 显示结果
                overall_risk = risk_result.get('overall_risk', {})
                print(f"综合风险评估:")
                print(f"  评分: {overall_risk.get('score', 'N/A')}")
                print(f"  等级: {overall_risk.get('level', 'N/A')}")
                
                # 显示各组件风险
                components = ['market_risk', 'liquidity_risk', 'volatility_risk', 
                             'fundamental_risk', 'technical_risk', 'concentration_risk']
                
                print(f"  组件风险:")
                for comp in components:
                    comp_data = risk_result.get(comp, {})
                    if comp_data:
                        score = comp_data.get('score', 'N/A')
                        level = comp_data.get('level', 'N/A')
                        print(f"    {comp}: {score} ({level})")
                
                print()
                
            except Exception as e:
                print(f"❌ 分析 {stock_code} 时出错: {e}")
                print()
                
    except Exception as e:
        print(f"❌ 风险管理器初始化失败: {e}")

def test_stock_analyzer():
    """测试股票分析器的风险筛选"""
    print("=== 股票分析器风险筛选测试 ===")
    
    try:
        from src.ai.stock_analyzer import StockAnalyzer
        
        # 初始化
        analyzer = StockAnalyzer()
        
        # 测试股票池（使用扩展的股票池）
        test_stocks = [
            "601857.SH",  # 中国石油
            "600028.SH",  # 中国石化
            "601398.SH",  # 工商银行
            "600519.SH",  # 贵州茅台
            "000002.SZ",  # 万科A
            "300750.SZ",  # 宁德时代
            "002594.SZ",  # 比亚迪
            "000063.SZ",  # 中兴通讯
        ]
        
        # 测试不同风险级别的筛选
        risk_levels = ["低风险", "中等风险", "高风险"]
        
        for risk_level in risk_levels:
            print(f"--- 测试风险级别: {risk_level} ---")
            
            results = analyzer.screen_stocks(
                stock_list=test_stocks,
                min_score=0,  # 降低评分要求以看到更多结果
                risk_level=risk_level,
                market_cap="不限"
            )
            
            print(f"筛选结果数量: {len(results)}")
            
            if results:
                print("筛选到的股票:")
                for result in results:
                    print(f"  {result['symbol']} - {result['name']}: "
                          f"评分={result['score']}, 风险={result['risk_level']}")
            else:
                print("  无符合条件的股票")
            
            print()
            
    except Exception as e:
        print(f"❌ 股票分析器测试失败: {e}")

def test_individual_risk_components():
    """测试个别风险组件"""
    print("=== 风险组件独立测试 ===")
    
    try:
        from src.ai.risk_manager import RiskManager
        from src.data.data_fetcher import DataFetcher
        
        risk_manager = RiskManager()
        data_fetcher = DataFetcher()
        
        # 获取一只股票的数据（测试中国石油）
        stock_code = "601857.SH"  # 中国石油
        stock_data = data_fetcher.get_stock_data(stock_code, period='6m')
        
        if stock_data is None or stock_data.empty:
            print("❌ 无法获取测试数据")
            return
        
        print(f"测试股票: {stock_code}")
        print(f"数据量: {len(stock_data)} 天")
        
        # 测试各个风险组件
        print("\n--- 市场风险 ---")
        market_risk = risk_manager._assess_market_risk(stock_data, None)
        print(f"评分: {market_risk.get('score')}, 等级: {market_risk.get('level')}")
        print(f"详情: {market_risk.get('details', {})}")
        
        print("\n--- 流动性风险 ---")
        liquidity_risk = risk_manager._assess_liquidity_risk(stock_data)
        print(f"评分: {liquidity_risk.get('score')}, 等级: {liquidity_risk.get('level')}")
        print(f"详情: {liquidity_risk.get('details', {})}")
        
        print("\n--- 波动性风险 ---")
        volatility_risk = risk_manager._assess_volatility_risk(stock_data)
        print(f"评分: {volatility_risk.get('score')}, 等级: {volatility_risk.get('level')}")
        print(f"详情: {volatility_risk.get('details', {})}")
        
        print("\n--- 基本面风险 ---")
        fundamental_risk = risk_manager._assess_fundamental_risk(None)
        print(f"评分: {fundamental_risk.get('score')}, 等级: {fundamental_risk.get('level')}")
        
        print("\n--- 技术面风险 ---")
        technical_risk = risk_manager._assess_technical_risk(stock_data)
        print(f"评分: {technical_risk.get('score')}, 等级: {technical_risk.get('level')}")
        
        print("\n--- 集中度风险 ---")
        concentration_risk = risk_manager._assess_concentration_risk(stock_data)
        print(f"评分: {concentration_risk.get('score')}, 等级: {concentration_risk.get('level')}")
        
        # 测试综合风险计算
        print("\n--- 综合风险计算 ---")
        overall_risk = risk_manager._calculate_overall_risk(
            market_risk, liquidity_risk, volatility_risk,
            fundamental_risk, technical_risk, concentration_risk
        )
        print(f"综合评分: {overall_risk.get('score')}")
        print(f"综合等级: {overall_risk.get('level')}")
        print(f"权重配置: {overall_risk.get('weights', {})}")
        print(f"组件评分: {overall_risk.get('component_scores', {})}")
        
    except Exception as e:
        print(f"❌ 风险组件测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔍 开始风险分析系统调试")
    print("=" * 50)
    
    # 首先运行增强搜索功能测试
    test_enhanced_search_functionality()
    print("\n" + "=" * 50)
    test_search_precision_and_coverage()
    print("\n" + "=" * 50)
    
    # 然后运行原有的风险分析测试
    test_individual_risk_components()
    print("\n" + "=" * 50)
    test_risk_manager()
    print("\n" + "=" * 50)
    test_stock_analyzer()
    
    print("\n🎯 调试完成")
