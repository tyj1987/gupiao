#!/usr/bin/env python3
"""
快速测试股票分析功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_stock_analysis():
    """测试股票分析功能"""
    print("🧪 测试股票分析功能...")
    
    try:
        from src.ai.stock_analyzer import StockAnalyzer
        from src.data.data_fetcher import DataFetcher
        
        # 初始化
        data_fetcher = DataFetcher()
        analyzer = StockAnalyzer()
        
        # 测试股票代码
        symbol = '000001.SZ'
        
        print(f"📊 分析股票: {symbol}")
        
        # 获取股票数据
        stock_data = data_fetcher.get_stock_data(symbol, period='3m')
        
        if stock_data is not None and not stock_data.empty:
            print(f"✅ 获取股票数据成功: {len(stock_data)} 条记录")
            
            # 进行AI分析 (使用新的参数格式)
            result = analyzer.analyze_stock(
                ts_code_or_data=stock_data,
                financial_data=None
            )
            
            if result:
                print("✅ 股票AI分析成功")
                
                # 检查关键结果
                overall_score = result.get('overall_score', {})
                score = overall_score.get('score', 0)
                level = overall_score.get('level', 'unknown')
                
                print(f"   📈 AI综合评分: {score:.2f}/100")
                print(f"   📊 评分级别: {level}")
                print(f"   💡 投资建议: {result.get('recommendation', 'N/A')}")
                print(f"   🎯 置信度: {result.get('confidence', 0):.2f}")
                
                # 检查权重配置
                weights = overall_score.get('weights', {})
                weight_sum = sum(weights.values()) if weights else 0
                print(f"   ⚖️ 权重总和: {weight_sum:.3f}")
                
                if abs(weight_sum - 1.0) < 0.01:
                    print("   ✅ 权重配置正确")
                else:
                    print("   ⚠️ 权重配置异常")
                
                return True
            else:
                print("❌ 股票AI分析失败 - 返回空结果")
                return False
        else:
            print("❌ 无法获取股票数据")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🚀 股票分析功能快速测试")
    print("=" * 40)
    
    if test_stock_analysis():
        print("\n🎉 股票分析功能正常！")
        print("📱 现在您可以在Web界面中正常使用股票分析功能")
        print("🌐 访问地址: http://localhost:8501")
    else:
        print("\n❌ 股票分析功能仍有问题，需要进一步检查")

if __name__ == "__main__":
    main()
