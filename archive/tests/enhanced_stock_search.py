#!/usr/bin/env python3
"""
股票搜索工具 - 测试增强搜索功能
"""

import sys
import os
sys.path.append('/home/tyj/gupiao')

from src.data.stock_mapper import stock_mapper
from src.data.stock_search_enhancer import stock_search_enhancer
from src.data.data_fetcher import DataFetcher
from src.ai.risk_manager import RiskManager

def search_and_analyze(query: str):
    """搜索并分析股票"""
    print(f"\n{'='*60}")
    print(f"搜索查询: '{query}'")
    print(f"{'='*60}")
    
    try:
        # 初始化组件
        data_fetcher = DataFetcher()
        risk_manager = RiskManager()
        
        # 执行增强搜索
        results = stock_search_enhancer.enhanced_search(query, stock_mapper, data_fetcher)
        
        if not results:
            print("❌ 未找到任何匹配的股票")
            
            # 提供搜索建议
            suggestions = stock_search_enhancer.suggest_alternatives(query, stock_mapper)
            if suggestions:
                print("\n💡 搜索建议:")
                for suggestion in suggestions[:5]:
                    print(f"   • {suggestion}")
            return
        
        print(f"✅ 找到 {len(results)} 个匹配结果\n")
        
        # 显示搜索统计
        stats = stock_search_enhancer.get_search_statistics(query, stock_mapper, data_fetcher)
        print("📊 搜索统计:")
        print(f"   • 总结果数: {stats['total_results']}")
        print(f"   • 有数据的股票: {stats['data_available_count']}")
        print(f"   • 无数据的股票: {stats['data_unavailable_count']}")
        
        if stats['by_search_type']:
            print("   • 按搜索类型:")
            for search_type, count in stats['by_search_type'].items():
                print(f"     - {search_type}: {count}个")
        
        if stats['by_market']:
            print("   • 按市场分布:")
            for market, count in stats['by_market'].items():
                print(f"     - {market}: {count}个")
        
        print("\n" + "-"*60)
        
        # 详细显示前10个结果
        for i, result in enumerate(results[:10], 1):
            symbol = result['symbol']
            name = result['name']
            search_type = result['search_type']
            market = result['market']
            data_available = result.get('data_available', False)
            latest_price = result.get('latest_price')
            
            status_icon = "✅" if data_available else "❌"
            print(f"\n{i}. {status_icon} {symbol} - {name}")
            print(f"   🔍 搜索方式: {search_type}")
            print(f"   🏢 市场: {market}")
            
            if latest_price:
                print(f"   💰 最新价格: {latest_price:.2f}")
            
            # 如果有额外的匹配信息
            if 'matched_alias' in result:
                print(f"   🏷️ 匹配别名: {result['matched_alias']}")
            if 'matched_pattern' in result:
                print(f"   🔤 匹配模式: {result['matched_pattern']}")
            if 'original_company' in result:
                print(f"   🏢 原始公司: {result['original_company']}")
            
            # 对A股进行详细分析
            if data_available and symbol.endswith(('.SH', '.SZ')):
                try:
                    print(f"   📈 正在获取详细数据...")
                    stock_data = data_fetcher.get_stock_data(symbol, period='1m')
                    
                    if stock_data is not None and not stock_data.empty:
                        # 基本信息
                        latest = stock_data.iloc[-1]
                        price_change = stock_data['pct_chg'].iloc[-1] if 'pct_chg' in stock_data.columns else 0
                        
                        print(f"   📊 今日涨跌: {price_change:.2f}%")
                        print(f"   📊 成交量: {latest.get('volume', 'N/A')}")
                        
                        # 风险评估
                        print(f"   🔄 进行风险评估...")
                        risk_result = risk_manager.assess_risk(stock_data)
                        overall_risk = risk_result.get('overall_risk', {})
                        
                        risk_level = overall_risk.get('level', 'N/A')
                        risk_score = overall_risk.get('score', 'N/A')
                        
                        print(f"   ⚡ 风险等级: {risk_level}")
                        print(f"   📊 风险评分: {risk_score}")
                        
                        # 主要风险因子
                        main_risks = []
                        risk_components = ['market_risk', 'liquidity_risk', 'volatility_risk']
                        for comp in risk_components:
                            comp_data = risk_result.get(comp, {})
                            if comp_data:
                                level = comp_data.get('level', 'N/A')
                                if level in ['高风险', '极高风险']:
                                    main_risks.append(f"{comp}({level})")
                        
                        if main_risks:
                            print(f"   ⚠️ 主要风险: {', '.join(main_risks)}")
                        
                except Exception as e:
                    print(f"   ❌ 详细分析失败: {e}")
            
            elif not data_available:
                error_msg = result.get('error', '数据源不支持此股票')
                print(f"   ❌ 数据不可用: {error_msg}")
        
        # 如果结果太多，显示省略信息
        if len(results) > 10:
            print(f"\n... 还有 {len(results) - 10} 个结果未显示")
        
    except Exception as e:
        print(f"❌ 搜索过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

def interactive_search():
    """交互式搜索"""
    print("🔍 股票增强搜索工具")
    print("=" * 60)
    print("输入股票名称、代码、简称或关键词进行搜索")
    print("输入 'quit' 或 'exit' 退出")
    print("输入 'help' 查看帮助")
    print("-" * 60)
    
    while True:
        try:
            query = input("\n🔍 请输入搜索内容: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['quit', 'exit', '退出']:
                print("👋 再见！")
                break
            
            if query.lower() in ['help', '帮助']:
                print_help()
                continue
            
            search_and_analyze(query)
            
        except KeyboardInterrupt:
            print("\n\n👋 用户中断，再见！")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")

def print_help():
    """显示帮助信息"""
    print("\n📖 搜索帮助:")
    print("1. 股票代码搜索:")
    print("   • 601857")
    print("   • 601857.SH")
    print("   • 000001.SZ")
    print()
    print("2. 公司名称搜索:")
    print("   • 中国石油")
    print("   • 贵州茅台")
    print("   • 比亚迪")
    print()
    print("3. 简称搜索:")
    print("   • 中石油")
    print("   • 茅台")
    print("   • 工行")
    print()
    print("4. 行业关键词:")
    print("   • 银行")
    print("   • 石油")
    print("   • 新能源")
    print()
    print("5. 跨市场搜索:")
    print("   • 腾讯 (港股)")
    print("   • 阿里 (港股+美股)")
    print("   • AAPL (美股)")

def batch_test():
    """批量测试"""
    test_queries = [
        "中国石油",    # A股精确匹配
        "中石油",      # 简称
        "601857",      # 代码
        "石油",        # 关键词
        "银行",        # 行业
        "茅台",        # 热门股票简称
        "比亚迪",      # 新能源
        "腾讯",        # 港股
        "阿里",        # 跨市场
        "AAPL",        # 美股
        "华为",        # 未上市
        "不存在公司",  # 无效查询
    ]
    
    print("🧪 批量测试模式")
    print("=" * 60)
    
    for query in test_queries:
        search_and_analyze(query)
        print("\n" + "🔄"*20 + " 下一个测试 " + "🔄"*20)

def main():
    """主函数"""
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            batch_test()
        else:
            # 直接搜索命令行参数
            query = ' '.join(sys.argv[1:])
            search_and_analyze(query)
    else:
        interactive_search()

if __name__ == "__main__":
    main()
