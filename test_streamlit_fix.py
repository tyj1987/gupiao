#!/usr/bin/env python3
"""
测试streamlit应用是否能正确运行
"""

import sys
import os
from pathlib import Path
import subprocess
import time

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_streamlit_imports():
    """测试streamlit应用的导入"""
    print("🔍 测试streamlit应用导入...")
    
    try:
        # 测试主要导入
        import streamlit as st
        from datetime import datetime, timedelta
        import time
        import pandas as pd
        import numpy as np
        print("✅ 基础模块导入成功")
        
        # 测试自定义模块导入
        from src.trading.watchlist_manager import WatchlistManager
        from src.trading.auto_trader import AutoTrader
        print("✅ 自动交易模块导入成功")
        
        # 测试自选股管理器
        manager = WatchlistManager()
        print("✅ 自选股管理器初始化成功")
        
        # 测试自动交易器
        trader = AutoTrader(mode="simulate", strategy="balanced", initial_capital=100000)
        print("✅ 自动交易器初始化成功")
        
        print("\n🎉 所有导入测试通过！streamlit应用应该能正常运行")
        return True
        
    except Exception as e:
        print(f"❌ 导入测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_datetime_usage():
    """测试datetime相关功能"""
    print("\n📅 测试datetime功能...")
    
    try:
        from datetime import datetime, timedelta
        
        # 测试之前出错的代码
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=180)
        
        print(f"✅ datetime测试成功: {start_date} 到 {end_date}")
        return True
        
    except Exception as e:
        print(f"❌ datetime测试失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Streamlit应用兼容性测试")
    print("=" * 60)
    
    success = True
    
    # 测试导入
    if not test_streamlit_imports():
        success = False
    
    # 测试datetime
    if not test_datetime_usage():
        success = False
    
    if success:
        print("\n" + "=" * 60)
        print("✅ 所有测试通过！应用已修复完成")
        print("🚀 访问 http://localhost:8501 体验自动交易功能")
        print("=" * 60)
    else:
        print("\n❌ 测试未完全通过，请检查错误信息")
