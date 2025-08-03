#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动交易系统
提供模拟交易和实盘交易功能，专为新手设计
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from loguru import logger
import time
import json
from pathlib import Path
import threading
from dataclasses import dataclass, asdict
from enum import Enum

from ..data.data_fetcher import DataFetcher
from ..ai.stock_analyzer import StockAnalyzer
from ..ai.risk_manager import RiskManager
from config.config import config

class TradeType(Enum):
    """交易类型"""
    BUY = "买入"
    SELL = "卖出"

class TradeStatus(Enum):
    """交易状态"""
    PENDING = "待成交"
    FILLED = "已成交"
    CANCELLED = "已取消"
    FAILED = "失败"

@dataclass
class Trade:
    """交易记录"""
    id: str
    symbol: str
    trade_type: TradeType
    quantity: int
    price: float
    timestamp: datetime
    status: TradeStatus = TradeStatus.PENDING
    reason: str = ""
    commission: float = 0.0
    
    def to_dict(self):
        return asdict(self)

@dataclass
class Position:
    """持仓信息"""
    symbol: str
    quantity: int
    avg_cost: float
    current_price: float
    market_value: float
    profit_loss: float
    profit_loss_pct: float
    
    def to_dict(self):
        return asdict(self)

@dataclass
class Portfolio:
    """投资组合"""
    cash: float
    total_value: float
    positions: List[Position]
    daily_pnl: float
    total_pnl: float
    
    def to_dict(self):
        return {
            'cash': self.cash,
            'total_value': self.total_value,
            'positions': [pos.to_dict() for pos in self.positions],
            'daily_pnl': self.daily_pnl,
            'total_pnl': self.total_pnl
        }

class TradingStrategy:
    """交易策略基类"""
    
    def __init__(self, name: str, risk_level: str = "medium"):
        self.name = name
        self.risk_level = risk_level
        self.analyzer = StockAnalyzer()
        self.risk_manager = RiskManager()
    
    def generate_signals(self, stock_data: pd.DataFrame, analysis: Dict) -> List[Dict]:
        """生成交易信号"""
        raise NotImplementedError
    
    def should_buy(self, symbol: str, analysis: Dict) -> Tuple[bool, str]:
        """是否应该买入"""
        score = analysis.get('overall_score', 0)
        recommendation = analysis.get('recommendation', '持有')
        
        if recommendation == '买入' and score >= 75:
            return True, f"AI推荐买入，评分: {score}"
        
        return False, f"不满足买入条件，评分: {score}"
    
    def should_sell(self, symbol: str, position: Position, analysis: Dict) -> Tuple[bool, str]:
        """是否应该卖出"""
        # 止损条件
        if position.profit_loss_pct <= -10:
            return True, f"止损卖出，亏损: {position.profit_loss_pct:.2f}%"
        
        # 止盈条件
        if position.profit_loss_pct >= 20:
            return True, f"止盈卖出，盈利: {position.profit_loss_pct:.2f}%"
        
        # AI建议卖出
        recommendation = analysis.get('recommendation', '持有')
        if recommendation == '卖出':
            return True, "AI推荐卖出"
        
        return False, "继续持有"

class ConservativeStrategy(TradingStrategy):
    """保守型策略"""
    
    def __init__(self):
        super().__init__("保守型", "low")
    
    def should_buy(self, symbol: str, analysis: Dict) -> Tuple[bool, str]:
        score = analysis.get('overall_score', 0)
        recommendation = analysis.get('recommendation', '持有')
        risk_level = analysis.get('risk_level', '中等')
        
        if (recommendation == '买入' and 
            score >= 80 and 
            risk_level in ['低', '低风险']):
            return True, f"保守策略买入信号，评分: {score}, 风险: {risk_level}"
        
        return False, f"保守策略不建议买入，评分: {score}, 风险: {risk_level}"
    
    def should_sell(self, symbol: str, position: Position, analysis: Dict) -> Tuple[bool, str]:
        # 更严格的止损
        if position.profit_loss_pct <= -5:
            return True, f"保守策略止损，亏损: {position.profit_loss_pct:.2f}%"
        
        # 更早止盈
        if position.profit_loss_pct >= 15:
            return True, f"保守策略止盈，盈利: {position.profit_loss_pct:.2f}%"
        
        return super().should_sell(symbol, position, analysis)

class BalancedStrategy(TradingStrategy):
    """平衡型策略"""
    
    def __init__(self):
        super().__init__("平衡型", "medium")

class AggressiveStrategy(TradingStrategy):
    """激进型策略"""
    
    def __init__(self):
        super().__init__("激进型", "high")
    
    def should_buy(self, symbol: str, analysis: Dict) -> Tuple[bool, str]:
        score = analysis.get('overall_score', 0)
        recommendation = analysis.get('recommendation', '持有')
        
        if recommendation == '买入' and score >= 65:
            return True, f"激进策略买入信号，评分: {score}"
        
        return False, f"激进策略不建议买入，评分: {score}"
    
    def should_sell(self, symbol: str, position: Position, analysis: Dict) -> Tuple[bool, str]:
        # 更宽松的止损
        if position.profit_loss_pct <= -15:
            return True, f"激进策略止损，亏损: {position.profit_loss_pct:.2f}%"
        
        # 更高的止盈目标
        if position.profit_loss_pct >= 30:
            return True, f"激进策略止盈，盈利: {position.profit_loss_pct:.2f}%"
        
        return super().should_sell(symbol, position, analysis)

class AutoTrader:
    """自动交易器"""
    
    def __init__(self, mode: str = "simulate", strategy: str = "conservative", initial_capital: float = 100000):
        """
        初始化自动交易器
        
        Args:
            mode: 交易模式 (simulate/live)
            strategy: 交易策略 (conservative/balanced/aggressive)
            initial_capital: 初始资金
        """
        self.mode = mode
        self.initial_capital = initial_capital
        self.is_running = False
        
        # 初始化组件
        self.data_fetcher = DataFetcher()
        self.analyzer = StockAnalyzer()
        
        # 选择策略
        if strategy == "conservative":
            self.strategy = ConservativeStrategy()
        elif strategy == "balanced":
            self.strategy = BalancedStrategy()
        elif strategy == "aggressive":
            self.strategy = AggressiveStrategy()
        else:
            self.strategy = BalancedStrategy()
        
        # 初始化投资组合
        self.portfolio = Portfolio(
            cash=initial_capital,
            total_value=initial_capital,
            positions=[],
            daily_pnl=0.0,
            total_pnl=0.0
        )
        
        # 交易记录
        self.trades_history = []
        
        # 股票池
        self.stock_pool = [
            "000001.SZ", "000002.SZ", "600000.SH", "600036.SH", "000858.SZ"
        ]
        
        # 风险控制参数
        self.max_position_pct = 0.2  # 单只股票最大仓位比例
        self.max_positions = 5  # 最大持仓数量
        
        # 数据存储路径
        self.data_dir = Path("data/trading")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"自动交易器初始化完成 - 模式: {mode}, 策略: {strategy}, 初始资金: {initial_capital}")
    
    def start_trading(self):
        """启动自动交易"""
        if self.is_running:
            logger.warning("交易已在运行中")
            return
        
        self.is_running = True
        logger.info("启动自动交易")
        
        # 在后台线程中运行交易循环
        self.trading_thread = threading.Thread(target=self._trading_loop, daemon=True)
        self.trading_thread.start()
    
    def stop_trading(self):
        """停止自动交易"""
        self.is_running = False
        logger.info("停止自动交易")
    
    def _trading_loop(self):
        """交易主循环"""
        while self.is_running:
            try:
                # 更新投资组合
                self._update_portfolio()
                
                # 检查卖出信号
                self._check_sell_signals()
                
                # 检查买入信号
                self._check_buy_signals()
                
                # 保存交易数据
                self._save_trading_data()
                
                # 输出状态信息
                self._log_status()
                
                # 等待下一轮
                time.sleep(60)  # 1分钟检查一次
                
            except Exception as e:
                logger.error(f"交易循环错误: {e}")
                time.sleep(30)  # 发生错误时等待30秒
    
    def _update_portfolio(self):
        """更新投资组合"""
        total_value = self.portfolio.cash
        
        for position in self.portfolio.positions:
            try:
                # 获取最新价格
                stock_data = self.data_fetcher.get_stock_data(position.symbol, period="1d")
                if not stock_data.empty:
                    current_price = stock_data['close'].iloc[-1]
                    position.current_price = current_price
                    position.market_value = position.quantity * current_price
                    position.profit_loss = position.market_value - (position.quantity * position.avg_cost)
                    position.profit_loss_pct = (position.profit_loss / (position.quantity * position.avg_cost)) * 100
                    
                    total_value += position.market_value
                    
            except Exception as e:
                logger.warning(f"更新持仓 {position.symbol} 失败: {e}")
        
        # 更新总价值
        prev_total = self.portfolio.total_value
        self.portfolio.total_value = total_value
        self.portfolio.daily_pnl = total_value - prev_total
        self.portfolio.total_pnl = total_value - self.initial_capital
    
    def _check_sell_signals(self):
        """检查卖出信号"""
        positions_to_sell = []
        
        for position in self.portfolio.positions:
            try:
                # 获取股票分析
                stock_data = self.data_fetcher.get_stock_data(position.symbol, period="3m")
                analysis = self.analyzer.analyze_stock(stock_data)
                
                # 检查是否应该卖出
                should_sell, reason = self.strategy.should_sell(position.symbol, position, analysis)
                
                if should_sell:
                    positions_to_sell.append((position, reason))
                    
            except Exception as e:
                logger.warning(f"检查卖出信号 {position.symbol} 失败: {e}")
        
        # 执行卖出操作
        for position, reason in positions_to_sell:
            self._execute_sell(position, reason)
    
    def _check_buy_signals(self):
        """检查买入信号"""
        # 如果现金不足或持仓已满，则不买入
        if self.portfolio.cash < self.portfolio.total_value * 0.1:  # 保留10%现金
            return
        
        if len(self.portfolio.positions) >= self.max_positions:
            return
        
        for symbol in self.stock_pool:
            try:
                # 检查是否已持有
                if any(pos.symbol == symbol for pos in self.portfolio.positions):
                    continue
                
                # 获取股票分析
                stock_data = self.data_fetcher.get_stock_data(symbol, period="3m")
                analysis = self.analyzer.analyze_stock(stock_data)
                
                # 检查是否应该买入
                should_buy, reason = self.strategy.should_buy(symbol, analysis)
                
                if should_buy:
                    self._execute_buy(symbol, reason)
                    break  # 一次只买入一只股票
                    
            except Exception as e:
                logger.warning(f"检查买入信号 {symbol} 失败: {e}")
    
    def _execute_buy(self, symbol: str, reason: str):
        """执行买入操作"""
        try:
            # 获取当前价格
            stock_data = self.data_fetcher.get_stock_data(symbol, period="1d")
            if stock_data.empty:
                return
            
            current_price = stock_data['close'].iloc[-1]
            
            # 计算买入数量
            max_invest = self.portfolio.total_value * self.max_position_pct
            available_cash = min(self.portfolio.cash * 0.9, max_invest)  # 保留10%现金
            quantity = int(available_cash / current_price / 100) * 100  # 买入整手
            
            if quantity < 100:  # 至少买入1手
                return
            
            invest_amount = quantity * current_price
            commission = invest_amount * 0.0003  # 万分之三手续费
            
            if self.mode == "simulate":
                # 模拟交易
                trade = Trade(
                    id=f"T{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    symbol=symbol,
                    trade_type=TradeType.BUY,
                    quantity=quantity,
                    price=current_price,
                    timestamp=datetime.now(),
                    status=TradeStatus.FILLED,
                    reason=reason,
                    commission=commission
                )
                
                # 更新投资组合
                self.portfolio.cash -= (invest_amount + commission)
                
                # 检查是否已有持仓
                existing_position = None
                for pos in self.portfolio.positions:
                    if pos.symbol == symbol:
                        existing_position = pos
                        break
                
                if existing_position:
                    # 更新现有持仓
                    total_cost = existing_position.avg_cost * existing_position.quantity + invest_amount
                    total_quantity = existing_position.quantity + quantity
                    existing_position.avg_cost = total_cost / total_quantity
                    existing_position.quantity = total_quantity
                else:
                    # 创建新持仓
                    position = Position(
                        symbol=symbol,
                        quantity=quantity,
                        avg_cost=current_price,
                        current_price=current_price,
                        market_value=invest_amount,
                        profit_loss=0.0,
                        profit_loss_pct=0.0
                    )
                    self.portfolio.positions.append(position)
                
                self.trades_history.append(trade)
                logger.info(f"买入成功: {symbol} {quantity}股 @{current_price:.2f} 原因: {reason}")
                
            else:
                # 实盘交易 - 这里需要接入真实的交易接口
                logger.warning("实盘交易接口未实现")
                
        except Exception as e:
            logger.error(f"买入失败 {symbol}: {e}")
    
    def _execute_sell(self, position: Position, reason: str):
        """执行卖出操作"""
        try:
            if self.mode == "simulate":
                # 模拟交易
                sell_amount = position.quantity * position.current_price
                commission = sell_amount * 0.0003  # 万分之三手续费
                
                trade = Trade(
                    id=f"T{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    symbol=position.symbol,
                    trade_type=TradeType.SELL,
                    quantity=position.quantity,
                    price=position.current_price,
                    timestamp=datetime.now(),
                    status=TradeStatus.FILLED,
                    reason=reason,
                    commission=commission
                )
                
                # 更新投资组合
                self.portfolio.cash += (sell_amount - commission)
                self.portfolio.positions.remove(position)
                
                self.trades_history.append(trade)
                logger.info(f"卖出成功: {position.symbol} {position.quantity}股 @{position.current_price:.2f} 盈亏: {position.profit_loss:.2f} 原因: {reason}")
                
            else:
                # 实盘交易 - 这里需要接入真实的交易接口
                logger.warning("实盘交易接口未实现")
                
        except Exception as e:
            logger.error(f"卖出失败 {position.symbol}: {e}")
    
    def _save_trading_data(self):
        """保存交易数据"""
        try:
            # 保存投资组合
            portfolio_file = self.data_dir / "portfolio.json"
            with open(portfolio_file, 'w', encoding='utf-8') as f:
                json.dump(self.portfolio.to_dict(), f, ensure_ascii=False, indent=2, default=str)
            
            # 保存交易历史
            trades_file = self.data_dir / "trades_history.json"
            with open(trades_file, 'w', encoding='utf-8') as f:
                trades_data = [trade.to_dict() for trade in self.trades_history]
                json.dump(trades_data, f, ensure_ascii=False, indent=2, default=str)
                
        except Exception as e:
            logger.warning(f"保存交易数据失败: {e}")
    
    def _log_status(self):
        """输出状态信息"""
        logger.info(f"投资组合状态 - 总价值: {self.portfolio.total_value:.2f}, 现金: {self.portfolio.cash:.2f}, 持仓: {len(self.portfolio.positions)}, 总盈亏: {self.portfolio.total_pnl:.2f}")
    
    def get_portfolio_summary(self) -> Dict:
        """获取投资组合摘要"""
        return {
            "total_value": self.portfolio.total_value,
            "cash": self.portfolio.cash,
            "positions_count": len(self.portfolio.positions),
            "total_pnl": self.portfolio.total_pnl,
            "total_pnl_pct": (self.portfolio.total_pnl / self.initial_capital) * 100,
            "daily_pnl": self.portfolio.daily_pnl,
            "positions": [pos.to_dict() for pos in self.portfolio.positions]
        }
    
    def get_trades_history(self) -> List[Dict]:
        """获取交易历史"""
        return [trade.to_dict() for trade in self.trades_history]
    
    def add_to_stock_pool(self, symbol: str):
        """添加股票到股票池"""
        if symbol not in self.stock_pool:
            self.stock_pool.append(symbol)
            logger.info(f"添加股票到股票池: {symbol}")
    
    def remove_from_stock_pool(self, symbol: str):
        """从股票池移除股票"""
        if symbol in self.stock_pool:
            self.stock_pool.remove(symbol)
            logger.info(f"从股票池移除股票: {symbol}")
