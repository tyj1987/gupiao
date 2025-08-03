#!/usr/bin/env python3
"""
简单演示
"""

print("🚀 股票分析系统状态检查")
print("="*50)

try:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    # 1. 依赖检查
    print("\n📦 依赖库检查:")
    
    try:
        import sklearn
        print(f"✅ scikit-learn {sklearn.__version__}")
    except Exception as e:
        print(f"❌ scikit-learn: {e}")
    
    try:
        import scipy
        print(f"✅ scipy {scipy.__version__}")
    except Exception as e:
        print(f"❌ scipy: {e}")
    
    try:
        import yfinance
        print(f"✅ yfinance {yfinance.__version__}")
    except Exception as e:
        print(f"❌ yfinance: {e}")
    
    try:
        import pandas_ta
        print(f"✅ pandas-ta {pandas_ta.__version__}")
    except Exception as e:
        print(f"❌ pandas-ta: {e}")
    
    # 2. 组件检查
    print("\n🔧 组件检查:")
    
    try:
        from src.data.data_processor import DataProcessor
        print("✅ DataProcessor 导入成功")
    except Exception as e:
        print(f"❌ DataProcessor: {e}")
    
    try:
        from src.ai.ml_models import MLModels
        print("✅ MLModels 导入成功")
    except Exception as e:
        print(f"❌ MLModels: {e}")
    
    try:
        from src.data.data_fetcher import DataFetcher
        print("✅ DataFetcher 导入成功")
    except Exception as e:
        print(f"❌ DataFetcher: {e}")
    
    print("\n🎉 系统检查完成！")
    
except Exception as e:
    print(f"❌ 系统检查失败: {e}")
    import traceback
    traceback.print_exc()
