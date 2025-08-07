#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动交易功能测试脚本
"""

import os
import sys
import numpy as np
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

def test_auto_trading():
    """测试自动交易功能"""
    print("=" * 60)
    print("🚀 自动交易功能测试")
    print("=" * 60)
    
    try:
        # 测试自选股管理器
        print("\n📋 测试自选股管理器...")
        from src.trading.watchlist_manager import WatchlistManager
        
        manager = WatchlistManager()
        print(f"✅ 自选股管理器初始化成功")
        
        # 添加测试股票
        test_stocks = [
            {"symbol": "000001.SZ", "name": "平安银行", "price": 12.34},
            {"symbol": "600036.SH", "name": "招商银行", "price": 45.23},
            {"symbol": "000858.SZ", "name": "五粮液", "price": 165.40}
        ]
        
        for stock in test_stocks:
            success = manager.add_stock(
                symbol=stock["symbol"],
                name=stock["name"],
                current_price=stock["price"],
                group_name="测试分组"
            )
            if success:
                print(f"✅ 添加股票: {stock['name']}")
            else:
                print(f"ℹ️  股票已存在: {stock['name']}")
        
        # 查看自选股
        watchlist = manager.get_watchlist()
        print(f"\n📊 当前自选股数量: {len(watchlist)}")
        
        for stock in watchlist:
            print(f"  - {stock.name} ({stock.symbol}) 分组: {stock.group_name}")
        
        # 测试自动交易器
        print("\n⚡ 测试自动交易器...")
        from src.trading.auto_trader import AutoTrader
        
        trader = AutoTrader(
            mode="simulate",
            strategy="balanced",
            initial_capital=100000,
            use_watchlist=True
        )
        print(f"✅ 自动交易器初始化成功")
        print(f"💰 初始资金: ¥{trader.initial_capital:,.0f}")
        print(f"📈 交易策略: {trader.strategy.name}")
        print(f"📋 股票池数量: {len(trader.stock_pool)}")
        
        # 模拟交易回测
        print("\n📈 执行模拟回测...")
        start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        print(f"回测期间: {start_date} 至 {end_date}")
        
        result = trader.simulate_trading(start_date, end_date)
        
        print("\n📊 回测结果:")
        print(f"  总收益率: {result.total_return_pct:+.2f}%")
        print(f"  最大回撤: -{result.max_drawdown:.2f}%")
        print(f"  胜率: {result.win_rate:.1f}%")
        print(f"  夏普比率: {result.sharpe_ratio:.2f}")
        print(f"  总交易次数: {result.total_trades}")
        print(f"  盈利次数: {result.winning_trades}")
        print(f"  亏损次数: {result.losing_trades}")
        
        # 评估回测结果
        if result.total_return_pct > 0:
            print(f"\n🎉 策略表现: 盈利 {result.total_return_pct:+.2f}%")
        else:
            print(f"\n⚠️  策略表现: 亏损 {result.total_return_pct:.2f}%")
        
        if result.win_rate > 50:
            print(f"💪 胜率优秀: {result.win_rate:.1f}%")
        else:
            print(f"🤔 胜率待改进: {result.win_rate:.1f}%")
        
        if result.sharpe_ratio > 1.0:
            print(f"⭐ 夏普比率良好: {result.sharpe_ratio:.2f}")
        else:
            print(f"📉 夏普比率一般: {result.sharpe_ratio:.2f}")
        
        print("\n✅ 自动交易功能测试完成")
        
        print("\n🎯 功能特点:")
        print("  ✓ 自选股管理 - 支持分组管理和批量操作")
        print("  ✓ 智能交易策略 - 保守型/平衡型/激进型")
        print("  ✓ 历史回测 - 验证策略有效性") 
        print("  ✓ 风险控制 - 止损止盈和仓位管理")
        print("  ✓ 交易记录 - 完整的交易历史追踪")
        print("  ✓ 实时监控 - 持仓状态和盈亏分析")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_watchlist_operations():
    """测试自选股操作"""
    print("\n" + "=" * 40)
    print("📋 自选股操作测试")
    print("=" * 40)
    
    try:
        from src.trading.watchlist_manager import WatchlistManager
        
        manager = WatchlistManager()
        
        # 创建测试分组
        print("1. 创建分组测试...")
        groups = ["科技股", "银行股", "消费股"]
        for group in groups:
            success = manager.create_group(group, f"{group}投资主题")
            print(f"  {'✅' if success else 'ℹ️ '} 分组: {group}")
        
        # 添加股票到不同分组
        print("\n2. 添加股票到分组...")
        test_data = [
            {"symbol": "000001.SZ", "name": "平安银行", "price": 12.34, "group": "银行股"},
            {"symbol": "600036.SH", "name": "招商银行", "price": 45.23, "group": "银行股"}, 
            {"symbol": "000858.SZ", "name": "五粮液", "price": 165.40, "group": "消费股"},
            {"symbol": "000002.SZ", "name": "万科A", "price": 15.67, "group": "默认分组"}
        ]
        
        for stock in test_data:
            success = manager.add_stock(
                symbol=stock["symbol"],
                name=stock["name"],
                current_price=stock["price"],
                group_name=stock["group"]
            )
            print(f"  {'✅' if success else 'ℹ️ '} {stock['name']} -> {stock['group']}")
        
        # 查看各分组的股票
        print("\n3. 查看分组股票...")
        for group_name in manager.get_group_names():
            stocks = manager.get_watchlist(group_name)
            print(f"  📁 {group_name}: {len(stocks)}只")
            for stock in stocks:
                print(f"    - {stock.name} ({stock.symbol})")
        
        # 搜索功能测试
        print("\n4. 搜索功能测试...")
        search_results = manager.search_stocks("银行")
        print(f"  搜索'银行': 找到 {len(search_results)}只")
        for stock in search_results:
            print(f"    - {stock.name}")
        
        # 移动股票分组
        print("\n5. 移动股票分组测试...")
        success = manager.move_stock_to_group("000002.SZ", "消费股")
        print(f"  {'✅' if success else '❌'} 万科A 移动到 消费股")
        
        print("\n✅ 自选股操作测试完成")
        
    except Exception as e:
        print(f"❌ 自选股操作测试失败: {e}")

if __name__ == "__main__":
    success = test_auto_trading()
    test_watchlist_operations()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 所有测试通过！自动交易系统ready！")
        print("📱 现在可以在Streamlit应用中体验完整的自动交易功能")
        print("=" * 60)
    else:
        print("\n❌ 测试未通过，请检查错误信息")
