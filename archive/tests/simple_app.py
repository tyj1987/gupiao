#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票AI分析助手 - 简化示例脚本
演示核心功能的使用方法
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def create_sample_data(symbol: str = "000001.SZ", days: int = 100) -> pd.DataFrame:
    """创建示例股票数据用于演示"""
    
    # 生成日期序列
    dates = pd.date_range(start=datetime.now() - timedelta(days=days), 
                         end=datetime.now(), freq='D')
    
    # 生成模拟股票数据
    np.random.seed(42)  # 固定随机种子以便复现
    
    base_price = 12.0
    returns = np.random.normal(0.001, 0.02, len(dates))  # 日收益率
    
    prices = [base_price]
    for i in range(1, len(dates)):
        new_price = prices[-1] * (1 + returns[i])
        prices.append(max(new_price, 0.1))  # 确保价格为正
    
    # 创建OHLCV数据
    data = []
    for i, (date, close) in enumerate(zip(dates, prices)):
        # 模拟开高低价
        volatility = 0.03
        high = close * (1 + np.random.uniform(0, volatility))
        low = close * (1 - np.random.uniform(0, volatility))
        open_price = close * (1 + np.random.uniform(-volatility/2, volatility/2))
        
        # 模拟成交量
        volume = np.random.uniform(1000000, 5000000)
        
        data.append({
            'trade_date': date.strftime('%Y%m%d'),
            'ts_code': symbol,
            'open': round(open_price, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(close, 2),
            'pre_close': round(prices[i-1] if i > 0 else close, 2),
            'change': round(close - (prices[i-1] if i > 0 else close), 2),
            'pct_chg': round((close - (prices[i-1] if i > 0 else close)) / (prices[i-1] if i > 0 else close) * 100, 2),
            'vol': round(volume),
            'amount': round(volume * close, 2)
        })
    
    df = pd.DataFrame(data)
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df = df.set_index('trade_date')
    
    return df

def demo_stock_analysis():
    """演示股票分析功能"""
    print("=" * 60)
    print("🔬 股票AI分析演示")
    print("=" * 60)
    
    # 创建示例数据
    symbol = "000001.SZ"
    print(f"📊 正在分析股票: {symbol} (平安银行)")
    
    stock_data = create_sample_data(symbol)
    print(f"✅ 生成了 {len(stock_data)} 天的模拟数据")
    
    # 模拟分析结果
    latest_price = stock_data['close'].iloc[-1]
    prev_price = stock_data['close'].iloc[-2]
    change = latest_price - prev_price
    change_pct = (change / prev_price) * 100
    
    # 计算简单技术指标
    ma5 = stock_data['close'].rolling(5).mean().iloc[-1]
    ma20 = stock_data['close'].rolling(20).mean().iloc[-1]
    
    # 模拟AI评分
    score = np.random.uniform(65, 85)
    
    print(f"\n📈 基本信息:")
    print(f"   最新价格: ¥{latest_price:.2f}")
    print(f"   涨跌幅: {change:+.2f} ({change_pct:+.2f}%)")
    print(f"   5日均线: ¥{ma5:.2f}")
    print(f"   20日均线: ¥{ma20:.2f}")
    
    print(f"\n🤖 AI分析结果:")
    print(f"   综合评分: {score:.1f}/100")
    
    if score >= 80:
        recommendation = "买入"
        risk_level = "低风险"
    elif score >= 70:
        recommendation = "持有"
        risk_level = "中等风险"
    else:
        recommendation = "观望"
        risk_level = "中等风险"
    
    print(f"   投资建议: {recommendation}")
    print(f"   风险等级: {risk_level}")
    
    # 交易信号
    print(f"\n⚡ 交易信号:")
    if latest_price > ma5 > ma20:
        print("   趋势信号: 多头排列 📈")
    elif latest_price < ma5 < ma20:
        print("   趋势信号: 空头排列 📉")
    else:
        print("   趋势信号: 震荡整理 📊")
    
    if change_pct > 3:
        print("   价格信号: 强势上涨 🚀")
    elif change_pct > 1:
        print("   价格信号: 温和上涨 📈")
    elif change_pct < -3:
        print("   价格信号: 大幅下跌 📉")
    elif change_pct < -1:
        print("   价格信号: 温和下跌 📊")
    else:
        print("   价格信号: 震荡整理 ⚖️")

def demo_stock_screening():
    """演示智能选股功能"""
    print("=" * 60)
    print("🎯 智能选股演示")
    print("=" * 60)
    
    # 模拟股票池
    stock_pool = [
        {"code": "000001.SZ", "name": "平安银行", "score": 82, "price": 12.34},
        {"code": "000002.SZ", "name": "万科A", "score": 78, "price": 15.67},
        {"code": "600000.SH", "name": "浦发银行", "score": 75, "price": 8.45},
        {"code": "000858.SZ", "name": "五粮液", "score": 73, "price": 128.50},
        {"code": "600036.SH", "name": "招商银行", "score": 80, "price": 35.20},
        {"code": "000166.SZ", "name": "申万宏源", "score": 68, "price": 4.25},
        {"code": "600519.SH", "name": "贵州茅台", "score": 85, "price": 1680.00},
        {"code": "000725.SZ", "name": "京东方A", "score": 65, "price": 3.84}
    ]
    
    print("🔍 筛选条件: 评分 >= 75分")
    print("\n📊 筛选结果:")
    print("-" * 70)
    print(f"{'排名':<4} {'股票代码':<12} {'股票名称':<12} {'AI评分':<8} {'当前价格':<10} {'投资建议'}")
    print("-" * 70)
    
    # 按评分排序并筛选
    filtered_stocks = [stock for stock in stock_pool if stock["score"] >= 75]
    filtered_stocks.sort(key=lambda x: x["score"], reverse=True)
    
    for i, stock in enumerate(filtered_stocks, 1):
        if stock["score"] >= 80:
            recommendation = "买入"
        else:
            recommendation = "持有"
        
        print(f"{i:<4} {stock['code']:<12} {stock['name']:<12} {stock['score']:<8} ¥{stock['price']:<9.2f} {recommendation}")
    
    print(f"\n✅ 共筛选出 {len(filtered_stocks)} 只优质股票")

def demo_auto_trading():
    """演示自动交易功能"""
    print("=" * 60)
    print("⚡ 自动交易演示")
    print("=" * 60)
    
    print("🤖 自动交易系统状态:")
    print("   模式: 模拟交易")
    print("   策略: 保守型")
    print("   初始资金: ¥100,000")
    
    # 模拟交易记录
    trades = [
        {"time": "2024-01-15 09:30", "stock": "平安银行", "action": "买入", "price": 12.34, "quantity": 1000, "amount": 12340},
        {"time": "2024-01-15 14:25", "stock": "万科A", "action": "买入", "price": 15.67, "quantity": 800, "amount": 12536},
        {"time": "2024-01-16 10:15", "stock": "平安银行", "action": "卖出", "price": 13.45, "quantity": 1000, "amount": 13450}
    ]
    
    print("\n📝 最近交易记录:")
    print("-" * 80)
    print(f"{'时间':<17} {'股票':<10} {'操作':<6} {'价格':<8} {'数量':<8} {'金额':<10}")
    print("-" * 80)
    
    for trade in trades:
        print(f"{trade['time']:<17} {trade['stock']:<10} {trade['action']:<6} ¥{trade['price']:<7.2f} {trade['quantity']:<8} ¥{trade['amount']:<9}")
    
    # 模拟收益统计
    total_profit = 1110  # 示例盈利
    profit_rate = 1.11   # 1.11%
    
    print("\n📊 交易统计:")
    print(f"   总收益: ¥{total_profit:+}")
    print(f"   收益率: {profit_rate:+.2f}%")
    print("   胜率: 75.0%")
    print("   最大回撤: -3.2%")
    
    print("\n⚠️  风险提示:")
    print("   • 模拟交易仅供学习使用")
    print("   • 实盘交易请谨慎操作")
    print("   • 投资有风险，入市需谨慎")

def demo_risk_management():
    """演示风险管理功能"""
    print("=" * 60)
    print("🛡️  风险管理演示")
    print("=" * 60)
    
    # 模拟投资组合
    portfolio = {
        "总资产": 115000,
        "现金": 25000,
        "股票市值": 90000,
        "持仓股票": [
            {"name": "平安银行", "value": 25000, "weight": 21.7, "risk": "低"},
            {"name": "万科A", "value": 20000, "weight": 17.4, "risk": "中"},
            {"name": "招商银行", "value": 30000, "weight": 26.1, "risk": "低"},
            {"name": "五粮液", "value": 15000, "weight": 13.0, "risk": "中"}
        ]
    }
    
    print("📊 投资组合分析:")
    print(f"   总资产: ¥{portfolio['总资产']:,}")
    print(f"   现金比例: {portfolio['现金']/portfolio['总资产']*100:.1f}%")
    print(f"   股票仓位: {portfolio['股票市值']/portfolio['总资产']*100:.1f}%")
    
    print("\n🏢 持仓分布:")
    print("-" * 50)
    print(f"{'股票名称':<10} {'市值':<12} {'权重':<8} {'风险等级'}")
    print("-" * 50)
    
    for holding in portfolio["持仓股票"]:
        print(f"{holding['name']:<10} ¥{holding['value']:,<11} {holding['weight']:<7.1f}% {holding['risk']}")
    
    print("\n⚠️  风险分析:")
    
    # 集中度风险
    max_weight = max(h['weight'] for h in portfolio["持仓股票"])
    if max_weight > 30:
        print("   🔴 集中度风险: 高 (单只股票权重过大)")
    elif max_weight > 20:
        print("   🟡 集中度风险: 中 (建议适当分散)")
    else:
        print("   🟢 集中度风险: 低 (分散度良好)")
    
    # 行业风险
    finance_weight = sum(h['weight'] for h in portfolio["持仓股票"] if h['name'] in ['平安银行', '招商银行'])
    if finance_weight > 40:
        print("   🔴 行业风险: 高 (金融股占比过大)")
    else:
        print("   🟡 行业风险: 中 (建议关注行业分布)")
    
    # 流动性风险
    cash_ratio = portfolio['现金']/portfolio['总资产']
    if cash_ratio < 0.1:
        print("   🔴 流动性风险: 高 (现金比例过低)")
    elif cash_ratio < 0.2:
        print("   🟡 流动性风险: 中 (现金比例适中)")
    else:
        print("   🟢 流动性风险: 低 (现金充足)")
    
    print("\n💡 风险建议:")
    print("   • 考虑增加其他行业股票降低行业集中度")
    print("   • 保持合理的现金比例以应对市场波动")
    print("   • 定期重新平衡投资组合")
    print("   • 关注市场整体风险变化")

def main():
    """主演示函数"""
    print("🎉 欢迎使用股票AI分析助手!")
    print("专为新手股民设计的智能投资工具")
    
    while True:
        print("\n" + "="*60)
        print("请选择演示功能:")
        print("1. 📊 股票分析演示")
        print("2. 🎯 智能选股演示") 
        print("3. ⚡ 自动交易演示")
        print("4. 🛡️  风险管理演示")
        print("5. 🌐 启动Web界面")
        print("0. 退出")
        print("="*60)
        
        choice = input("请输入选择 (0-5): ").strip()
        
        if choice == "1":
            demo_stock_analysis()
        elif choice == "2":
            demo_stock_screening()
        elif choice == "3":
            demo_auto_trading()
        elif choice == "4":
            demo_risk_management()
        elif choice == "5":
            print("\n🌐 启动Web界面...")
            print("请在浏览器中访问: http://localhost:8501")
            print("命令: python -m streamlit run src/ui/streamlit_app.py")
            break
        elif choice == "0":
            print("\n👋 感谢使用股票AI分析助手!")
            print("💡 提示: 投资有风险，入市需谨慎")
            break
        else:
            print("❌ 无效选择，请重新输入")
        
        input("\n按回车键继续...")

if __name__ == "__main__":
    main()

def main():
    print("=" * 50)
    print("股票AI分析助手 - 简化版")
    print("=" * 50)
    
    # 检查Python版本
    print(f"Python版本: {sys.version}")
    
    # 检查项目结构
    print("\n项目结构检查:")
    project_files = [
        "src/data/data_fetcher.py",
        "src/ai/stock_analyzer.py",
        "src/ui/streamlit_app.py",
        "config/config.py",
        "requirements.txt"
    ]
    
    for file_path in project_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path} - 存在")
        else:
            print(f"✗ {file_path} - 缺失")
    
    # 检查依赖包
    print("\n依赖包检查:")
    required_packages = [
        "pandas", "numpy", "requests", "streamlit", 
        "plotly", "scikit-learn", "loguru"
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} - 已安装")
        except ImportError:
            print(f"✗ {package} - 未安装")
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("\n使用说明:")
    print("1. 等待依赖包安装完成")
    print("2. 配置API密钥 (可选)")
    print("3. 运行: streamlit run src/ui/streamlit_app.py")
    print("=" * 50)

if __name__ == "__main__":
    main()