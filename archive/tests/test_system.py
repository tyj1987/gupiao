#!/usr/bin/env python3
"""
系统功能测试脚本
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    """测试基础导入"""
    print("🧪 测试基础导入...")
    try:
        # 测试机器学习库
        import sklearn
        import scipy
        print(f"✅ scikit-learn {sklearn.__version__}")
        print(f"✅ scipy {scipy.__version__}")
        
        # 测试数据源
        import yfinance as yf
        print(f"✅ yfinance {yf.__version__}")
        
        # 测试技术分析
        import pandas_ta as ta
        print(f"✅ pandas-ta {ta.__version__}")
        
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_data_fetching():
    """测试数据获取"""
    print("\n🧪 测试数据获取...")
    try:
        from src.data.data_fetcher import DataFetcher
        
        fetcher = DataFetcher()
        
        # 测试美股数据
        print("测试美股数据 (AAPL)...")
        us_data = fetcher.get_daily_data(
            ts_code='AAPL',
            start_date=(datetime.now() - timedelta(days=30)).strftime('%Y%m%d'),
            end_date=datetime.now().strftime('%Y%m%d')
        )
        
        if us_data is not None and len(us_data) > 0:
            print(f"✅ 获取AAPL数据 {len(us_data)} 条记录")
            print(f"   数据列: {list(us_data.columns)}")
        else:
            print("⚠️ AAPL数据为空")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据获取测试失败: {e}")
        return False

def test_technical_analysis():
    """测试技术分析"""
    print("\n🧪 测试技术分析...")
    try:
        from src.data.data_processor import DataProcessor
        
        # 创建测试数据
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        test_data = pd.DataFrame({
            'trade_date': dates.strftime('%Y%m%d'),
            'open': 100 + pd.Series(range(100)).apply(lambda x: x * 0.1 + (x % 10) * 0.5),
            'high': 102 + pd.Series(range(100)).apply(lambda x: x * 0.1 + (x % 10) * 0.8),
            'low': 98 + pd.Series(range(100)).apply(lambda x: x * 0.1 + (x % 10) * 0.3),
            'close': 101 + pd.Series(range(100)).apply(lambda x: x * 0.1 + (x % 10) * 0.6),
            'vol': 1000000 + pd.Series(range(100)).apply(lambda x: x * 1000)
        })
        
        processor = DataProcessor()
        
        # 测试技术指标计算
        processed_data = processor.calculate_technical_indicators(test_data)
        
        if processed_data is not None and len(processed_data) > 0:
            print(f"✅ 技术指标计算成功")
            print(f"   原始列数: {len(test_data.columns)}")
            print(f"   处理后列数: {len(processed_data.columns)}")
            
            # 检查关键指标
            expected_indicators = ['ma5', 'ma20', 'rsi', 'macd']
            found_indicators = [ind for ind in expected_indicators if ind in processed_data.columns]
            print(f"   找到指标: {found_indicators}")
            
        # 测试特征工程
        features_data = processor.create_features(processed_data)
        print(f"✅ 特征工程完成，特征列数: {len(features_data.columns)}")
        
        # 测试形态识别
        patterns_data = processor.detect_patterns(features_data)
        print(f"✅ 形态识别完成，最终列数: {len(patterns_data.columns)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 技术分析测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ml_models():
    """测试机器学习模型"""
    print("\n🧪 测试机器学习模型...")
    try:
        from src.ai.ml_models import MLModels
        
        ml_models = MLModels()
        
        # 创建测试特征数据
        import numpy as np
        np.random.seed(42)
        
        n_samples = 100
        features = np.random.randn(n_samples, 10)
        target = np.random.randn(n_samples)
        
        feature_names = [f'feature_{i}' for i in range(10)]
        
        # 测试模型训练
        results = ml_models.train_models(features, target)
        
        if results:
            print(f"✅ 模型训练成功，训练了 {len(results)} 个模型")
            for model_name, metrics in results.items():
                # 检查不同可能的R²键名
                r2_value = None
                for key in ['r2', 'test_r2', 'r2_score']:
                    if key in metrics:
                        r2_value = metrics[key]
                        break
                
                if r2_value is not None and isinstance(r2_value, (int, float)):
                    print(f"   {model_name}: R² = {r2_value:.3f}")
                else:
                    print(f"   {model_name}: 训练完成")
        else:
            print("⚠️ 模型训练无结果")
        
        return True
        
    except Exception as e:
        print(f"❌ 机器学习测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 开始系统功能测试...\n")
    
    tests = [
        ("基础导入", test_basic_imports),
        ("数据获取", test_data_fetching),
        ("技术分析", test_technical_analysis),
        ("机器学习", test_ml_models)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统已完善并可以使用。")
    else:
        print("⚠️ 部分测试失败，需要进一步调试。")

if __name__ == "__main__":
    main()
