#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动交易系统
提供模拟交易和实盘交易功能，专为新手设计
"""

import pandas as pd
import numpy as np
import uuid
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
from .watchlist_manager import WatchlistManager
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

@dataclass
class SimulationResult:
    """模拟交易结果"""
    start_date: str
    end_date: str
    initial_capital: float
    final_capital: float
    total_return: float
    total_return_pct: float
    max_drawdown: float
    sharpe_ratio: float
    win_rate: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win: float
    avg_loss: float
    
    def to_dict(self):
        return asdict(self)

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
    
    def __init__(self, mode: str = "simulate", strategy: str = "conservative", 
                 initial_capital: float = 100000, use_watchlist: bool = True):
        """
        初始化自动交易器
        
        Args:
            mode: 交易模式 (simulate/live)
            strategy: 交易策略 (conservative/balanced/aggressive)
            initial_capital: 初始资金
            use_watchlist: 是否使用自选股作为交易股票池
        """
        self.mode = mode
        self.initial_capital = initial_capital
        self.use_watchlist = use_watchlist
        self.is_running = False
        
        # 初始化组件
        self.data_fetcher = DataFetcher()
        self.analyzer = StockAnalyzer()
        self.watchlist_manager = WatchlistManager()
        
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
        
        # 股票池 - 支持自选股
        if use_watchlist and self.watchlist_manager.get_stock_count() > 0:
            # 使用自选股作为股票池
            watchlist = self.watchlist_manager.get_watchlist()
            self.stock_pool = [stock.symbol for stock in watchlist]
            logger.info(f"使用自选股作为交易股票池，共 {len(self.stock_pool)} 只股票")
        else:
            # 使用默认股票池
            self.stock_pool = [
                "000001.SZ", "000002.SZ", "600000.SH", "600036.SH", "000858.SZ"
            ]
            logger.info(f"使用默认股票池，共 {len(self.stock_pool)} 只股票")
        
        # 风险控制参数
        self.max_position_pct = 0.2  # 单只股票最大仓位比例
        self.max_positions = 5  # 最大持仓数量
        self.commission_rate = 0.0003  # 手续费率
        
        # 数据存储路径
        self.data_dir = Path("data/trading")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"自动交易器初始化完成 - 模式: {mode}, 策略: {strategy}, 初始资金: {initial_capital}")
    
    def update_stock_pool(self, use_watchlist: bool = True, custom_stocks: List[str] = None):
        """
        更新股票池
        
        Args:
            use_watchlist: 是否使用自选股
            custom_stocks: 自定义股票列表
        """
        try:
            if custom_stocks:
                self.stock_pool = custom_stocks
                logger.info(f"使用自定义股票池，共 {len(self.stock_pool)} 只股票")
            elif use_watchlist:
                watchlist = self.watchlist_manager.get_watchlist()
                if watchlist:
                    self.stock_pool = [stock.symbol for stock in watchlist]
                    logger.info(f"使用自选股作为交易股票池，共 {len(self.stock_pool)} 只股票")
                else:
                    logger.warning("自选股为空，使用默认股票池")
                    self.stock_pool = ["000001.SZ", "000002.SZ", "600000.SH", "600036.SH", "000858.SZ"]
            else:
                self.stock_pool = ["000001.SZ", "000002.SZ", "600000.SH", "600036.SH", "000858.SZ"]
                logger.info(f"使用默认股票池，共 {len(self.stock_pool)} 只股票")
                
            self.use_watchlist = use_watchlist
            
        except Exception as e:
            logger.error(f"更新股票池失败: {e}")
    
    def simulate_trading(self, start_date: str, end_date: str, 
                        selected_stocks: List[str] = None) -> SimulationResult:
        """
        模拟自动交易
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            selected_stocks: 指定的股票列表，为None时使用当前股票池
            
        Returns:
            模拟交易结果
        """
        try:
            logger.info(f"开始模拟交易: {start_date} 到 {end_date}")
            
            # 使用指定的股票列表或当前股票池
            stocks_to_trade = selected_stocks if selected_stocks else self.stock_pool
            
            # 初始化模拟环境
            sim_portfolio = Portfolio(
                cash=self.initial_capital,
                total_value=self.initial_capital,
                positions=[],
                daily_pnl=0.0,
                total_pnl=0.0
            )
            
            sim_trades = []
            daily_values = []
            
            # 转换日期
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            
            current_date = start_dt
            
            while current_date <= end_dt:
                try:
                    # 模拟每日交易逻辑
                    date_str = current_date.strftime("%Y-%m-%d")
                    
                    # 更新持仓价格和市值
                    self._update_portfolio_value(sim_portfolio, date_str, stocks_to_trade)
                    
                    # 记录每日资产价值
                    daily_values.append({
                        'date': date_str,
                        'total_value': sim_portfolio.total_value,
                        'cash': sim_portfolio.cash,
                        'positions_value': sim_portfolio.total_value - sim_portfolio.cash
                    })
                    
                    # 执行交易策略
                    trades = self._execute_strategy(sim_portfolio, date_str, stocks_to_trade)
                    sim_trades.extend(trades)
                    
                    current_date += timedelta(days=1)
                    
                except Exception as e:
                    logger.warning(f"模拟交易日期 {current_date} 出错: {e}")
                    current_date += timedelta(days=1)
                    continue
            
            # 计算模拟结果
            result = self._calculate_simulation_result(
                start_date, end_date, self.initial_capital, 
                sim_portfolio.total_value, sim_trades, daily_values
            )
            
            logger.info(f"模拟交易完成 - 总收益率: {result.total_return_pct:.2f}%")
            return result
            
        except Exception as e:
            logger.error(f"模拟交易失败: {e}")
            # 返回默认结果
            return SimulationResult(
                start_date=start_date,
                end_date=end_date,
                initial_capital=self.initial_capital,
                final_capital=self.initial_capital,
                total_return=0.0,
                total_return_pct=0.0,
                max_drawdown=0.0,
                sharpe_ratio=0.0,
                win_rate=0.0,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                avg_win=0.0,
                avg_loss=0.0
            )
    
    def _update_portfolio_value(self, portfolio: Portfolio, date_str: str, stocks: List[str]):
        """更新投资组合价值"""
        try:
            total_value = portfolio.cash
            
            for position in portfolio.positions:
                # 模拟获取股票价格（这里使用随机价格变化）
                price_change = np.random.normal(0, 0.02)  # 平均0，标准差2%的价格变化
                new_price = position.current_price * (1 + price_change)
                
                # 更新持仓信息
                position.current_price = new_price
                position.market_value = position.quantity * new_price
                position.profit_loss = position.market_value - (position.quantity * position.avg_cost)
                position.profit_loss_pct = position.profit_loss / (position.quantity * position.avg_cost) * 100
                
                total_value += position.market_value
            
            # 更新投资组合总价值
            portfolio.total_value = total_value
            portfolio.total_pnl = total_value - self.initial_capital
            
        except Exception as e:
            logger.warning(f"更新投资组合价值失败: {e}")
    
    def _execute_strategy(self, portfolio: Portfolio, date_str: str, stocks: List[str]) -> List[Trade]:
        """执行交易策略"""
        trades = []
        
        try:
            # 检查卖出信号
            for position in portfolio.positions[:]:  # 使用副本避免修改时出错
                # 模拟分析结果
                mock_analysis = {
                    'overall_score': np.random.randint(40, 90),
                    'recommendation': np.random.choice(['买入', '卖出', '持有'], p=[0.3, 0.2, 0.5])
                }
                
                should_sell, reason = self.strategy.should_sell(position.symbol, position, mock_analysis)
                
                if should_sell:
                    trade = self._create_sell_trade(portfolio, position, reason, date_str)
                    if trade:
                        trades.append(trade)
            
            # 检查买入信号
            available_cash = portfolio.cash
            max_investment_per_stock = portfolio.total_value * self.max_position_pct
            
            if available_cash > 1000 and len(portfolio.positions) < self.max_positions:
                for symbol in stocks:
                    # 检查是否已持有
                    if any(p.symbol == symbol for p in portfolio.positions):
                        continue
                    
                    # 模拟分析结果
                    mock_analysis = {
                        'overall_score': np.random.randint(60, 95),
                        'recommendation': np.random.choice(['买入', '卖出', '持有'], p=[0.4, 0.1, 0.5])
                    }
                    
                    should_buy, reason = self.strategy.should_buy(symbol, mock_analysis)
                    
                    if should_buy:
                        # 计算买入金额
                        investment_amount = min(available_cash, max_investment_per_stock)
                        if investment_amount >= 1000:  # 最小投资金额
                            trade = self._create_buy_trade(portfolio, symbol, investment_amount, reason, date_str)
                            if trade:
                                trades.append(trade)
                                available_cash -= investment_amount
                                
                                # 限制每日买入数量
                                if len([t for t in trades if t.trade_type == TradeType.BUY]) >= 2:
                                    break
        
        except Exception as e:
            logger.warning(f"执行交易策略失败: {e}")
        
        return trades
    
    def _create_buy_trade(self, portfolio: Portfolio, symbol: str, amount: float, reason: str, date_str: str) -> Optional[Trade]:
        """创建买入交易"""
        try:
            # 模拟股票价格
            price = np.random.uniform(10, 50)  # 随机价格
            
            # 计算可买入股票数量（按手计算，1手=100股）
            shares = int(amount / price / 100) * 100
            
            if shares <= 0:
                return None
            
            actual_amount = shares * price
            commission = actual_amount * self.commission_rate
            total_cost = actual_amount + commission
            
            if total_cost > portfolio.cash:
                return None
            
            # 创建交易记录
            trade = Trade(
                id=str(uuid.uuid4()),
                symbol=symbol,
                trade_type=TradeType.BUY,
                quantity=shares,
                price=price,
                timestamp=datetime.strptime(date_str, "%Y-%m-%d"),
                status=TradeStatus.FILLED,
                reason=reason,
                commission=commission
            )
            
            # 更新投资组合
            portfolio.cash -= total_cost
            
            # 创建持仓
            position = Position(
                symbol=symbol,
                quantity=shares,
                avg_cost=price,
                current_price=price,
                market_value=actual_amount,
                profit_loss=0.0,
                profit_loss_pct=0.0
            )
            portfolio.positions.append(position)
            
            logger.info(f"买入: {symbol} {shares}股 @ {price:.2f}")
            return trade
            
        except Exception as e:
            logger.error(f"创建买入交易失败: {e}")
            return None
    
    def _create_sell_trade(self, portfolio: Portfolio, position: Position, reason: str, date_str: str) -> Optional[Trade]:
        """创建卖出交易"""
        try:
            price = position.current_price
            shares = position.quantity
            
            actual_amount = shares * price
            commission = actual_amount * self.commission_rate
            net_amount = actual_amount - commission
            
            # 创建交易记录
            trade = Trade(
                id=str(uuid.uuid4()),
                symbol=position.symbol,
                trade_type=TradeType.SELL,
                quantity=shares,
                price=price,
                timestamp=datetime.strptime(date_str, "%Y-%m-%d"),
                status=TradeStatus.FILLED,
                reason=reason,
                commission=commission
            )
            
            # 更新投资组合
            portfolio.cash += net_amount
            portfolio.positions.remove(position)
            
            logger.info(f"卖出: {position.symbol} {shares}股 @ {price:.2f}")
            return trade
            
        except Exception as e:
            logger.error(f"创建卖出交易失败: {e}")
            return None
    
    def _calculate_simulation_result(self, start_date: str, end_date: str, 
                                   initial_capital: float, final_capital: float,
                                   trades: List[Trade], daily_values: List[Dict]) -> SimulationResult:
        """计算模拟交易结果"""
        try:
            # 基本收益计算
            total_return = final_capital - initial_capital
            total_return_pct = (total_return / initial_capital) * 100
            
            # 计算最大回撤
            max_drawdown = 0.0
            peak_value = initial_capital
            
            for daily_value in daily_values:
                current_value = daily_value['total_value']
                if current_value > peak_value:
                    peak_value = current_value
                
                drawdown = (peak_value - current_value) / peak_value * 100
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
            
            # 计算交易统计
            total_trades = len(trades)
            buy_trades = [t for t in trades if t.trade_type == TradeType.BUY]
            sell_trades = [t for t in trades if t.trade_type == TradeType.SELL]
            
            # 计算盈亏
            winning_trades = 0
            losing_trades = 0
            wins = []
            losses = []
            
            for sell_trade in sell_trades:
                # 找到对应的买入交易
                buy_trade = None
                for bt in buy_trades:
                    if (bt.symbol == sell_trade.symbol and 
                        bt.timestamp < sell_trade.timestamp):
                        buy_trade = bt
                        break
                
                if buy_trade:
                    profit = (sell_trade.price - buy_trade.price) * sell_trade.quantity
                    profit -= sell_trade.commission + buy_trade.commission
                    
                    if profit > 0:
                        winning_trades += 1
                        wins.append(profit)
                    else:
                        losing_trades += 1
                        losses.append(abs(profit))
            
            # 胜率和平均盈亏
            win_rate = (winning_trades / max(1, winning_trades + losing_trades)) * 100
            avg_win = np.mean(wins) if wins else 0.0
            avg_loss = np.mean(losses) if losses else 0.0
            
            # 夏普比率（简化计算）
            if daily_values:
                returns = []
                for i in range(1, len(daily_values)):
                    ret = (daily_values[i]['total_value'] - daily_values[i-1]['total_value']) / daily_values[i-1]['total_value']
                    returns.append(ret)
                
                if returns and np.std(returns) > 0:
                    sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252)  # 年化夏普比率
                else:
                    sharpe_ratio = 0.0
            else:
                sharpe_ratio = 0.0
            
            return SimulationResult(
                start_date=start_date,
                end_date=end_date,
                initial_capital=initial_capital,
                final_capital=final_capital,
                total_return=total_return,
                total_return_pct=total_return_pct,
                max_drawdown=max_drawdown,
                sharpe_ratio=sharpe_ratio,
                win_rate=win_rate,
                total_trades=total_trades,
                winning_trades=winning_trades,
                losing_trades=losing_trades,
                avg_win=avg_win,
                avg_loss=avg_loss
            )
            
        except Exception as e:
            logger.error(f"计算模拟结果失败: {e}")
            return SimulationResult(
                start_date=start_date,
                end_date=end_date,
                initial_capital=initial_capital,
                final_capital=final_capital,
                total_return=0.0,
                total_return_pct=0.0,
                max_drawdown=0.0,
                sharpe_ratio=0.0,
                win_rate=0.0,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                avg_win=0.0,
                avg_loss=0.0
            )
    
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
