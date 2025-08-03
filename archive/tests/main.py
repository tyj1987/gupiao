#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票AI分析助手 - 主程序入口
为新手股民提供智能股票分析、选股建议和交易辅助
"""

import asyncio
import sys
import os
from pathlib import Path
from loguru import logger
import click

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.config import config
from src.data.data_fetcher import DataFetcher
from src.ai.stock_analyzer import StockAnalyzer
from src.ui.streamlit_app import launch_app
from src.trading.auto_trader import AutoTrader

def setup_logging():
    """配置日志系统"""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    logger.add(
        "logs/app_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="1 day",
        retention="30 days"
    )

@click.group()
def cli():
    """股票AI分析助手命令行工具"""
    setup_logging()
    logger.info("股票AI分析助手启动")

@cli.command()
@click.option('--port', default=8501, help='Web应用端口号')
@click.option('--host', default='localhost', help='Web应用主机地址')
def web(port, host):
    """启动Web界面"""
    logger.info(f"启动Web界面: http://{host}:{port}")
    launch_app(host=host, port=port)

@cli.command()
@click.option('--symbol', required=True, help='股票代码')
@click.option('--period', default='1y', help='分析周期')
def analyze(symbol, period):
    """分析单只股票"""
    logger.info(f"开始分析股票: {symbol}")
    
    try:
        # 初始化数据获取器和分析器
        data_fetcher = DataFetcher()
        analyzer = StockAnalyzer()
        
        # 获取股票数据
        stock_data = data_fetcher.get_stock_data(symbol, period=period)
        financial_data = data_fetcher.get_financial_data(symbol)
        
        # 执行分析
        analysis_result = analyzer.analyze_stock(
            stock_data=stock_data,
            financial_data=financial_data
        )
        
        # 输出分析结果
        print("\n" + "="*50)
        print(f"股票代码: {symbol}")
        print(f"分析时间: {analysis_result.get('analysis_time', 'N/A')}")
        print(f"综合评分: {analysis_result.get('overall_score', 'N/A')}/100")
        print(f"投资建议: {analysis_result.get('recommendation', 'N/A')}")
        print(f"风险等级: {analysis_result.get('risk_level', 'N/A')}")
        print("="*50)
        
        # 显示技术指标
        if 'technical_indicators' in analysis_result:
            print("\n技术指标:")
            for indicator, value in analysis_result['technical_indicators'].items():
                print(f"  {indicator}: {value}")
        
        # 显示买卖信号
        if 'signals' in analysis_result:
            print(f"\n交易信号:")
            for signal_type, signal in analysis_result['signals'].items():
                print(f"  {signal_type}: {signal}")
                
    except Exception as e:
        logger.error(f"分析失败: {e}")
        print(f"错误: {e}")

@cli.command()
@click.option('--mode', default='simulate', type=click.Choice(['simulate', 'live']), help='交易模式')
@click.option('--strategy', default='conservative', help='交易策略')
def trade(mode, strategy):
    """启动自动交易"""
    logger.info(f"启动自动交易模式: {mode}, 策略: {strategy}")
    
    try:
        trader = AutoTrader(mode=mode, strategy=strategy)
        
        if mode == 'simulate':
            print("⚠️  模拟交易模式 - 不会执行真实交易")
        else:
            print("🚨 实盘交易模式 - 请谨慎操作!")
            
        trader.start_trading()
        
    except Exception as e:
        logger.error(f"交易启动失败: {e}")
        print(f"错误: {e}")

@cli.command()
def screen():
    """执行选股筛选"""
    logger.info("开始执行智能选股")
    
    try:
        # 初始化组件
        data_fetcher = DataFetcher()
        analyzer = StockAnalyzer()
        
        # 获取股票列表
        stock_list = data_fetcher.get_stock_list()
        
        print(f"开始筛选 {len(stock_list)} 只股票...")
        
        recommendations = []
        for i, stock in enumerate(stock_list[:50]):  # 限制处理数量以免过长
            try:
                symbol = stock['ts_code']
                print(f"分析进度: {i+1}/50 - {symbol}")
                
                # 获取数据并分析
                stock_data = data_fetcher.get_stock_data(symbol, period='6m')
                analysis = analyzer.analyze_stock(stock_data)
                
                if analysis.get('overall_score', 0) >= 70:  # 高分股票
                    recommendations.append({
                        'symbol': symbol,
                        'name': stock.get('name', ''),
                        'score': analysis.get('overall_score', 0),
                        'recommendation': analysis.get('recommendation', ''),
                        'risk_level': analysis.get('risk_level', '')
                    })
                    
            except Exception as e:
                logger.warning(f"分析股票 {symbol} 失败: {e}")
                continue
        
        # 按评分排序
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"\n推荐股票 (共{len(recommendations)}只):")
        print("-" * 80)
        for rec in recommendations[:10]:  # 显示前10只
            print(f"{rec['symbol']} {rec['name']} | 评分: {rec['score']}/100 | 建议: {rec['recommendation']} | 风险: {rec['risk_level']}")
            
    except Exception as e:
        logger.error(f"选股失败: {e}")
        print(f"错误: {e}")

if __name__ == '__main__':
    cli()