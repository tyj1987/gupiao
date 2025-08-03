#!/usr/bin/env python3
"""
本地测试脚本 - 验证股票分析系统基本功能
"""

import sys
import os
sys.path.append('.')

def test_imports():
    """测试导入"""
    print("🔍 测试模块导入...")
    try:
        import streamlit as st
        print("✅ Streamlit 导入成功")
        
        import pandas as pd
        print("✅ Pandas 导入成功")
        
        import numpy as np
        print("✅ NumPy 导入成功")
        
        from src.data.universal_stock_fetcher import UniversalStockFetcher
        print("✅ UniversalStockFetcher 导入成功")
        
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_api_keys():
    """测试API密钥配置"""
    print("\n🔑 测试API密钥配置...")
    try:
        from config.api_keys import TUSHARE_TOKEN
        if TUSHARE_TOKEN and TUSHARE_TOKEN != "your_tushare_token_here":
            print("✅ Tushare Token 已配置")
            return True
        else:
            print("❌ Tushare Token 未配置")
            return False
    except Exception as e:
        print(f"❌ API密钥配置错误: {e}")
        return False

def test_stock_fetcher():
    """测试股票获取器"""
    print("\n📊 测试股票数据获取器...")
    try:
        from src.data.universal_stock_fetcher import UniversalStockFetcher
        
        # 使用缓存数据，避免网络请求
        fetcher = UniversalStockFetcher()
        
        # 检查缓存文件
        cache_file = "/tmp/stock_cache/all_stocks_cache.json"
        if os.path.exists(cache_file):
            print("✅ 发现股票缓存文件")
            
            # 加载缓存数据
            cached_stocks = fetcher._load_cache()
            if cached_stocks:
                print(f"✅ 成功加载 {len(cached_stocks)} 只股票缓存")
                
                # 统计各市场股票数量
                stats = {
                    'total': len(cached_stocks),
                    'a_stock_sh': sum(1 for k in cached_stocks.keys() if k.endswith('.SH')),
                    'a_stock_sz': sum(1 for k in cached_stocks.keys() if k.endswith('.SZ')),
                    'hk_stock': sum(1 for k in cached_stocks.keys() if k.endswith('.HK')),
                    'us_stock': sum(1 for k in cached_stocks.keys() if not k.endswith(('.SH', '.SZ', '.HK')))
                }
                
                print("📈 股票市场分布:")
                print(f"  A股上海: {stats['a_stock_sh']} 只")
                print(f"  A股深圳: {stats['a_stock_sz']} 只")
                print(f"  港股: {stats['hk_stock']} 只")
                print(f"  美股: {stats['us_stock']} 只")
                print(f"  总计: {stats['total']} 只")
                
                return True
            else:
                print("❌ 缓存文件为空")
        else:
            print("⚠️  未发现缓存文件，需要首次获取数据")
            print("💡 建议: 运行 Streamlit 应用将自动获取数据")
        
        return False
    except Exception as e:
        print(f"❌ 股票获取器测试失败: {e}")
        return False

def test_search_functionality():
    """测试搜索功能"""
    print("\n🔍 测试股票搜索功能...")
    try:
        from src.data.universal_stock_fetcher import UniversalStockFetcher
        
        fetcher = UniversalStockFetcher()
        cached_stocks = fetcher._load_cache()
        
        if not cached_stocks:
            print("⚠️  无缓存数据，跳过搜索测试")
            return False
        
        # 测试几个搜索案例
        test_cases = [
            ("600036", "代码搜索"),
            ("中国银行", "名称搜索"),
            ("zhyh", "拼音搜索"),
            ("600", "前缀搜索")
        ]
        
        for query, test_type in test_cases:
            results = fetcher.search_stocks(query)
            if results:
                print(f"✅ {test_type} '{query}': 找到 {len(results)} 个结果")
                # 显示前3个结果
                for i, (code, name) in enumerate(list(results.items())[:3]):
                    print(f"    {code}: {name}")
            else:
                print(f"❌ {test_type} '{query}': 未找到结果")
        
        return True
    except Exception as e:
        print(f"❌ 搜索功能测试失败: {e}")
        return False

def test_streamlit_app():
    """测试Streamlit应用文件"""
    print("\n🌐 测试Streamlit应用...")
    try:
        app_file = "src/ui/streamlit_app.py"
        if os.path.exists(app_file):
            print(f"✅ 找到Streamlit应用文件: {app_file}")
            
            # 简单语法检查
            with open(app_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'st.title' in content and 'st.sidebar' in content:
                    print("✅ Streamlit应用结构正常")
                    return True
                else:
                    print("❌ Streamlit应用结构异常")
        else:
            print(f"❌ 未找到Streamlit应用文件: {app_file}")
        
        return False
    except Exception as e:
        print(f"❌ Streamlit应用测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始本地测试...")
    print("=" * 50)
    
    tests = [
        ("模块导入", test_imports),
        ("API密钥", test_api_keys),
        ("股票获取器", test_stock_fetcher),
        ("搜索功能", test_search_functionality),
        ("Streamlit应用", test_streamlit_app)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试出错: {e}")
            results.append((test_name, False))
    
    # 显示测试结果摘要
    print("\n" + "=" * 50)
    print("📋 测试结果摘要:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 测试通过率: {passed}/{len(results)} ({passed/len(results)*100:.1f}%)")
    
    if passed == len(results):
        print("\n🎉 所有测试通过！系统准备就绪")
        print("\n💡 启动建议:")
        print("  1. 直接启动: streamlit run src/ui/streamlit_app.py --server.port 8501")
        print("  2. Docker部署: ./docker-quick-deploy.sh")
        print("  3. 传统部署: ./deploy.sh")
    else:
        print("\n⚠️  部分测试失败，请检查上述错误信息")
        
        if passed >= len(results) // 2:
            print("\n💡 基础功能正常，可以尝试启动:")
            print("  streamlit run src/ui/streamlit_app.py --server.port 8501")

if __name__ == "__main__":
    main()
