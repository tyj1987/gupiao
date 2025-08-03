import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from loguru import logger
try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logger.warning("scipy.stats不可用，部分风险计算功能受限")
import warnings
warnings.filterwarnings('ignore')

from config.config import config

class RiskManager:
    """风险管理器"""
    
    def __init__(self):
        """
        初始化风险管理器
        """
        self.risk_free_rate = 0.03  # 无风险利率，年化3%
        self.trading_days = 252  # 年交易日数
        
        logger.info("风险管理器初始化完成")
    
    def assess_risk(self, 
                   stock_data: pd.DataFrame,
                   financial_data: Dict = None,
                   market_data: Dict = None) -> Dict[str, any]:
        """
        综合风险评估
        
        Args:
            stock_data: 股票价格数据
            financial_data: 财务数据
            market_data: 市场数据
            
        Returns:
            风险评估结果
        """
        try:
            if stock_data.empty:
                return self._empty_risk_assessment()
            
            # 市场风险评估
            market_risk = self._assess_market_risk(stock_data, market_data)
            
            # 流动性风险评估
            liquidity_risk = self._assess_liquidity_risk(stock_data)
            
            # 波动性风险评估
            volatility_risk = self._assess_volatility_risk(stock_data)
            
            # 基本面风险评估
            fundamental_risk = self._assess_fundamental_risk(financial_data)
            
            # 技术面风险评估
            technical_risk = self._assess_technical_risk(stock_data)
            
            # 集中度风险评估
            concentration_risk = self._assess_concentration_risk(stock_data)
            
            # 综合风险评分
            overall_risk = self._calculate_overall_risk(
                market_risk, liquidity_risk, volatility_risk,
                fundamental_risk, technical_risk, concentration_risk
            )
            
            # 风险建议
            risk_recommendations = self._generate_risk_recommendations(
                overall_risk, market_risk, liquidity_risk, volatility_risk
            )
            
            # VaR计算
            var_metrics = self._calculate_var(stock_data)
            
            # 最大回撤
            drawdown_metrics = self._calculate_drawdown(stock_data)
            
            return {
                'overall_risk': overall_risk,
                'market_risk': market_risk,
                'liquidity_risk': liquidity_risk,
                'volatility_risk': volatility_risk,
                'fundamental_risk': fundamental_risk,
                'technical_risk': technical_risk,
                'concentration_risk': concentration_risk,
                'var_metrics': var_metrics,
                'drawdown_metrics': drawdown_metrics,
                'recommendations': risk_recommendations,
                'assessment_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"风险评估失败: {e}")
            return self._empty_risk_assessment()
    
    def _assess_market_risk(self, stock_data: pd.DataFrame, market_data: Dict = None) -> Dict[str, any]:
        """
        评估市场风险
        
        Args:
            stock_data: 股票数据
            market_data: 市场数据
            
        Returns:
            市场风险评估结果
        """
        try:
            if 'close' not in stock_data.columns:
                return {'score': 50, 'level': 'medium', 'details': {}}
            
            stock_returns = stock_data['close'].pct_change().dropna()
            
            if len(stock_returns) < 20:
                return {'score': 50, 'level': 'medium', 'details': {}}
            
            score = 50
            details = {}
            
            # Beta风险
            if market_data and '上证指数' in market_data:
                index_data = market_data['上证指数']
                if not index_data.empty and 'close' in index_data.columns:
                    index_returns = index_data['close'].pct_change().dropna()
                    
                    # 对齐数据
                    common_index = stock_returns.index.intersection(index_returns.index)
                    if len(common_index) >= 20:
                        stock_aligned = stock_returns.loc[common_index]
                        index_aligned = index_returns.loc[common_index]
                        
                        # 计算Beta
                        covariance = np.cov(stock_aligned, index_aligned)[0, 1]
                        market_variance = np.var(index_aligned)
                        
                        if market_variance > 0:
                            beta = covariance / market_variance
                            details['beta'] = beta
                            
                            # Beta风险评分
                            if beta > 1.5:
                                score += 15  # 高Beta，高风险
                            elif beta > 1.2:
                                score += 8
                            elif beta < 0.5:
                                score -= 5  # 低Beta，低风险
                            
                            # 相关性
                            correlation = np.corrcoef(stock_aligned, index_aligned)[0, 1]
                            details['market_correlation'] = correlation
                            
                            if abs(correlation) > 0.8:
                                score += 5  # 高相关性，系统性风险高
            
            # 收益率分布风险
            if len(stock_returns) >= 30:
                if SCIPY_AVAILABLE:
                    # 偏度
                    skewness = stats.skew(stock_returns)
                    details['skewness'] = skewness
                    
                    if skewness < -1:
                        score += 10  # 负偏度，左尾风险
                    elif skewness < -0.5:
                        score += 5
                    
                    # 峰度
                    kurtosis = stats.kurtosis(stock_returns)
                    details['kurtosis'] = kurtosis
                    
                    if kurtosis > 3:
                        score += 8  # 高峰度，极端事件风险
                else:
                    # 简化的偏度和峰度计算
                    mean_return = stock_returns.mean()
                    std_return = stock_returns.std()
                    
                    # 简化偏度
                    skewness = ((stock_returns - mean_return) ** 3).mean() / (std_return ** 3)
                    details['skewness'] = skewness
                    
                    if skewness < -1:
                        score += 10
                    elif skewness < -0.5:
                        score += 5
                    
                    # 简化峰度检查
                    if abs(skewness) > 2:  # 使用偏度来近似极端分布
                        score += 3
            
            # 下行风险
            negative_returns = stock_returns[stock_returns < 0]
            if len(negative_returns) > 0:
                downside_deviation = np.std(negative_returns)
                details['downside_deviation'] = downside_deviation
                
                # 下行风险评分
                if downside_deviation > 0.05:
                    score += 12
                elif downside_deviation > 0.03:
                    score += 6
            
            # 确保分数在0-100范围内
            score = max(0, min(100, score))
            
            return {
                'score': score,
                'level': self._get_risk_level(score),
                'details': details
            }
            
        except Exception as e:
            logger.error(f"市场风险评估失败: {e}")
            return {'score': 50, 'level': 'medium', 'details': {}}
    
    def _assess_liquidity_risk(self, stock_data: pd.DataFrame) -> Dict[str, any]:
        """
        评估流动性风险
        
        Args:
            stock_data: 股票数据
            
        Returns:
            流动性风险评估结果
        """
        try:
            score = 50
            details = {}
            
            if 'vol' not in stock_data.columns:
                return {'score': score, 'level': self._get_risk_level(score), 'details': details}
            
            volume = stock_data['vol']
            
            if len(volume) < 20:
                return {'score': score, 'level': self._get_risk_level(score), 'details': details}
            
            # 平均成交量
            avg_volume = volume.mean()
            details['avg_volume'] = avg_volume
            
            # 成交量稳定性
            volume_cv = volume.std() / avg_volume if avg_volume > 0 else 0
            details['volume_cv'] = volume_cv
            
            if volume_cv > 2:
                score += 15  # 成交量不稳定，流动性风险高
            elif volume_cv > 1:
                score += 8
            elif volume_cv < 0.5:
                score -= 5  # 成交量稳定，流动性风险低
            
            # 零成交量天数
            zero_volume_days = (volume == 0).sum()
            zero_volume_ratio = zero_volume_days / len(volume)
            details['zero_volume_ratio'] = zero_volume_ratio
            
            if zero_volume_ratio > 0.1:
                score += 20  # 经常零成交，流动性极差
            elif zero_volume_ratio > 0.05:
                score += 10
            
            # 成交量趋势
            if len(volume) >= 60:
                recent_volume = volume.tail(20).mean()
                historical_volume = volume.head(40).mean()
                
                if historical_volume > 0:
                    volume_trend = (recent_volume - historical_volume) / historical_volume
                    details['volume_trend'] = volume_trend
                    
                    if volume_trend < -0.5:
                        score += 10  # 成交量大幅下降
                    elif volume_trend < -0.2:
                        score += 5
            
            # 价格影响（用价格波动代替）
            if 'close' in stock_data.columns and len(stock_data) >= 20:
                price_volatility = stock_data['close'].pct_change().std()
                details['price_volatility'] = price_volatility
                
                # 高波动可能意味着流动性不足
                if price_volatility > 0.05:
                    score += 8
                elif price_volatility > 0.03:
                    score += 3
            
            # 确保分数在0-100范围内
            score = max(0, min(100, score))
            
            return {
                'score': score,
                'level': self._get_risk_level(score),
                'details': details
            }
            
        except Exception as e:
            logger.error(f"流动性风险评估失败: {e}")
            return {'score': 50, 'level': 'medium', 'details': {}}
    
    def _assess_volatility_risk(self, stock_data: pd.DataFrame) -> Dict[str, any]:
        """
        评估波动性风险
        
        Args:
            stock_data: 股票数据
            
        Returns:
            波动性风险评估结果
        """
        try:
            score = 50
            details = {}
            
            if 'close' not in stock_data.columns or len(stock_data) < 20:
                return {'score': score, 'level': 'medium', 'details': details}
            
            returns = stock_data['close'].pct_change().dropna()
            
            # 历史波动率
            volatility = returns.std() * np.sqrt(self.trading_days)
            details['annualized_volatility'] = volatility
            
            # 波动率风险评分
            if volatility > 0.6:
                score += 20  # 极高波动
            elif volatility > 0.4:
                score += 15
            elif volatility > 0.3:
                score += 10
            elif volatility > 0.2:
                score += 5
            elif volatility < 0.1:
                score -= 5  # 低波动
            
            # 波动率聚类
            if len(returns) >= 60:
                # 计算滚动波动率
                rolling_vol = returns.rolling(20).std()
                vol_of_vol = rolling_vol.std()
                details['volatility_of_volatility'] = vol_of_vol
                
                if vol_of_vol > rolling_vol.mean() * 0.5:
                    score += 8  # 波动率不稳定
            
            # 极端收益率
            if len(returns) >= 30:
                # 计算极端收益率的频率
                extreme_threshold = returns.std() * 2
                extreme_returns = returns[abs(returns) > extreme_threshold]
                extreme_ratio = len(extreme_returns) / len(returns)
                details['extreme_return_ratio'] = extreme_ratio
                
                if extreme_ratio > 0.1:
                    score += 12  # 频繁极端收益
                elif extreme_ratio > 0.05:
                    score += 6
            
            # 最大单日跌幅
            max_daily_loss = returns.min()
            details['max_daily_loss'] = max_daily_loss
            
            if max_daily_loss < -0.15:
                score += 15  # 单日大幅下跌
            elif max_daily_loss < -0.1:
                score += 10
            elif max_daily_loss < -0.05:
                score += 5
            
            # GARCH波动率预测（简化版）
            if len(returns) >= 50:
                # 使用简单的EWMA模型
                lambda_param = 0.94
                ewma_var = returns.var()
                
                for ret in returns:
                    ewma_var = lambda_param * ewma_var + (1 - lambda_param) * ret**2
                
                predicted_vol = np.sqrt(ewma_var * self.trading_days)
                details['predicted_volatility'] = predicted_vol
                
                # 预测波动率风险
                if predicted_vol > volatility * 1.2:
                    score += 5  # 预期波动率上升
            
            # 确保分数在0-100范围内
            score = max(0, min(100, score))
            
            return {
                'score': score,
                'level': self._get_risk_level(score),
                'details': details
            }
            
        except Exception as e:
            logger.error(f"波动性风险评估失败: {e}")
            return {'score': 50, 'level': 'medium', 'details': {}}
    
    def _assess_fundamental_risk(self, financial_data: Dict = None) -> Dict[str, any]:
        """
        评估基本面风险 (改进版本)
        
        Args:
            financial_data: 财务数据
            
        Returns:
            基本面风险评估结果
        """
        try:
            score = 50  # 基准分数
            details = {}
            
            # 如果没有财务数据，采用保守的风险评估策略
            if not financial_data or 'indicators' not in financial_data:
                # 根据股票类型进行简化评估
                # 银行股通常风险较低，大盘股相对稳定
                score = 45  # 略低于基准，表示相对稳健
                details['assessment_method'] = 'simplified_without_financial_data'
                return {
                    'score': score,
                    'level': self._get_risk_level(score),
                    'details': details
                }
            
            indicators = financial_data['indicators']
            if indicators.empty:
                score = 45  # 略低于基准
                details['assessment_method'] = 'empty_financial_data'
                return {
                    'score': score,
                    'level': self._get_risk_level(score),
                    'details': details
                }
            
            latest = indicators.iloc[0]
            details['assessment_method'] = 'full_financial_analysis'
            
            # 杠杆风险
            debt_ratio = latest.get('debt_to_assets', None)
            if debt_ratio is not None:
                details['debt_ratio'] = debt_ratio
                
                if debt_ratio > 0.8:
                    score += 20  # 高杠杆风险
                elif debt_ratio > 0.6:
                    score += 10
                elif debt_ratio < 0.2:
                    score -= 5  # 低杠杆，降低风险
            
            # 流动性风险
            current_ratio = latest.get('current_ratio', None)
            if current_ratio is not None:
                details['current_ratio'] = current_ratio
                
                if current_ratio < 1:
                    score += 15  # 流动性不足
                elif current_ratio < 1.5:
                    score += 5
                elif current_ratio > 3:
                    score += 5  # 过高也可能表示资金利用效率低
            
            # 盈利能力风险
            roe = latest.get('roe', None)
            if roe is not None:
                details['roe'] = roe
                
                if roe < 0:
                    score += 20  # 亏损
                elif roe < 5:
                    score += 10  # 低盈利能力
                elif roe > 25:
                    score -= 5  # 优秀的盈利能力
            
            # 估值风险
            pe = latest.get('pe_ratio', None)
            if pe is not None:
                details['pe_ratio'] = pe
                
                if pe < 0:
                    score += 15  # 负PE表示亏损
                elif pe > 50:
                    score += 15  # 高估值风险
                elif pe > 30:
                    score += 8
                elif pe < 10:
                    score -= 5  # 低估值，降低风险
            
            pb = latest.get('pb_ratio', None)
            if pb is not None:
                details['pb_ratio'] = pb
                
                if pb > 10:
                    score += 10  # 极高市净率
                elif pb > 5:
                    score += 5
                elif pb < 1:
                    score -= 3  # 破净可能是价值股
            
            # 成长性风险
            revenue_growth = latest.get('revenue_yoy', None)
            if revenue_growth is not None:
                details['revenue_growth'] = revenue_growth
                
                if revenue_growth < -20:
                    score += 15  # 营收大幅下滑
                elif revenue_growth < -10:
                    score += 10
                elif revenue_growth < 0:
                    score += 5
                elif revenue_growth > 30:
                    score -= 5  # 高成长降低风险
            
            profit_growth = latest.get('profit_yoy', None)
            if profit_growth is not None:
                details['profit_growth'] = profit_growth
                
                if profit_growth < -30:
                    score += 15  # 利润大幅下滑
                elif profit_growth < -15:
                    score += 10
                elif profit_growth < 0:
                    score += 5
                elif profit_growth > 50:
                    score -= 5  # 高利润增长
            
            # 确保分数在0-100范围内
            score = max(0, min(100, score))
            
            return {
                'score': score,
                'level': self._get_risk_level(score),
                'details': details
            }
            
        except Exception as e:
            logger.error(f"基本面风险评估失败: {e}")
            return {'score': 50, 'level': self._get_risk_level(50), 'details': {}}
    
    def _assess_technical_risk(self, stock_data: pd.DataFrame) -> Dict[str, any]:
        """
        评估技术面风险
        
        Args:
            stock_data: 股票数据
            
        Returns:
            技术面风险评估结果
        """
        try:
            score = 50
            details = {}
            
            if 'close' not in stock_data.columns or len(stock_data) < 20:
                return {'score': score, 'level': self._get_risk_level(score), 'details': details}
            
            close = stock_data['close']
            
            # 趋势风险
            if len(close) >= 60:
                # 短期vs长期趋势
                ma_short = close.rolling(10).mean().iloc[-1]
                ma_long = close.rolling(60).mean().iloc[-1]
                current_price = close.iloc[-1]
                
                details['ma_short'] = ma_short
                details['ma_long'] = ma_long
                
                # 价格相对于均线的位置
                if current_price < ma_long * 0.9:
                    score += 10  # 远离长期均线
                elif current_price < ma_long:
                    score += 5
                
                # 均线排列
                if ma_short < ma_long:
                    score += 8  # 空头排列
            
            # 支撑阻力风险
            if len(close) >= 30:
                # 计算近期高低点
                recent_high = close.tail(20).max()
                recent_low = close.tail(20).min()
                current_price = close.iloc[-1]
                
                details['recent_high'] = recent_high
                details['recent_low'] = recent_low
                
                # 接近重要阻力位
                if current_price > recent_high * 0.98:
                    score += 5  # 接近阻力位
                
                # 跌破重要支撑位
                if current_price < recent_low * 1.02:
                    score += 10  # 接近或跌破支撑位
            
            # 技术指标风险
            if len(close) >= 14:
                # RSI超买超卖
                delta = close.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                
                current_rsi = rsi.iloc[-1]
                details['rsi'] = current_rsi
                
                if current_rsi > 80:
                    score += 8  # 严重超买
                elif current_rsi > 70:
                    score += 5  # 超买
                elif current_rsi < 20:
                    score += 8  # 严重超卖
                elif current_rsi < 30:
                    score += 3  # 超卖（可能是机会）
            
            # 价格形态风险
            if len(close) >= 10:
                # 连续下跌
                recent_changes = close.pct_change().tail(5)
                consecutive_down = (recent_changes < 0).sum()
                
                details['consecutive_down_days'] = consecutive_down
                
                if consecutive_down >= 4:
                    score += 10  # 连续下跌
                elif consecutive_down >= 3:
                    score += 5
                
                # 跳空缺口
                if len(stock_data) >= 2 and 'open' in stock_data.columns:
                    yesterday_close = close.iloc[-2]
                    today_open = stock_data['open'].iloc[-1]
                    
                    gap = (today_open - yesterday_close) / yesterday_close
                    details['gap'] = gap
                    
                    if gap < -0.05:
                        score += 8  # 向下跳空
                    elif gap > 0.05:
                        score += 3  # 向上跳空（可能回补）
            
            # 确保分数在0-100范围内
            score = max(0, min(100, score))
            
            return {
                'score': score,
                'level': self._get_risk_level(score),
                'details': details
            }
            
        except Exception as e:
            logger.error(f"技术面风险评估失败: {e}")
            return {'score': 50, 'level': 'medium', 'details': {}}
    
    def _assess_concentration_risk(self, stock_data: pd.DataFrame) -> Dict[str, any]:
        """
        评估集中度风险
        
        Args:
            stock_data: 股票数据
            
        Returns:
            集中度风险评估结果
        """
        try:
            # 这里主要评估单一股票的集中度风险
            # 在实际应用中，这个函数会在组合层面进行评估
            
            score = 30  # 单一股票默认有一定集中度风险
            details = {'single_stock_risk': True}
            
            # 如果有行业或板块信息，可以进一步评估
            # 这里简化处理
            
            return {
                'score': score,
                'level': self._get_risk_level(score),
                'details': details
            }
            
        except Exception as e:
            logger.error(f"集中度风险评估失败: {e}")
            return {'score': 30, 'level': self._get_risk_level(30), 'details': {}}
    
    def _calculate_overall_risk(self, *risk_components) -> Dict[str, any]:
        """
        计算综合风险评分 (优化版本 - 增强差异化)
        
        Args:
            *risk_components: 各风险组件
            
        Returns:
            综合风险评分
        """
        try:
            # 优化权重配置 - 增加差异化
            weights = {
                'market': 0.30,      # 增加市场风险权重
                'liquidity': 0.10,    # 减少流动性权重
                'volatility': 0.30,   # 增加波动性权重
                'fundamental': 0.20,
                'technical': 0.10,
                'concentration': 0.00  # 暂时降低集中度权重
            }
            
            scores = [component.get('score', 50) for component in risk_components]
            weight_values = list(weights.values())
            
            # 加权平均
            overall_score = sum(score * weight for score, weight in zip(scores, weight_values))
            
            # 增强差异化：应用非线性调整
            if overall_score > 60:
                # 对高分区间进行拉伸
                overall_score = 60 + (overall_score - 60) * 1.5
            elif overall_score < 40:
                # 对低分区间进行压缩
                overall_score = 40 - (40 - overall_score) * 1.2
            
            # 确保分数在0-100范围内
            overall_score = max(0, min(100, overall_score))
            
            return {
                'score': overall_score,
                'level': self._get_risk_level(overall_score),
                'weights': weights,
                'component_scores': {
                    'market': scores[0] if len(scores) > 0 else 50,
                    'liquidity': scores[1] if len(scores) > 1 else 50,
                    'volatility': scores[2] if len(scores) > 2 else 50,
                    'fundamental': scores[3] if len(scores) > 3 else 50,
                    'technical': scores[4] if len(scores) > 4 else 50,
                    'concentration': scores[5] if len(scores) > 5 else 50
                }
            }
            
        except Exception as e:
            logger.error(f"综合风险计算失败: {e}")
            return {'score': 50, 'level': self._get_risk_level(50)}
    
    def _calculate_var(self, stock_data: pd.DataFrame, confidence_levels: List[float] = [0.95, 0.99]) -> Dict[str, any]:
        """
        计算风险价值(VaR)
        
        Args:
            stock_data: 股票数据
            confidence_levels: 置信水平列表
            
        Returns:
            VaR指标
        """
        try:
            if 'close' not in stock_data.columns or len(stock_data) < 30:
                return {}
            
            returns = stock_data['close'].pct_change().dropna()
            
            var_results = {}
            
            for confidence in confidence_levels:
                # 历史模拟法
                var_historical = np.percentile(returns, (1 - confidence) * 100)
                
                # 参数法（假设正态分布）
                mean_return = returns.mean()
                std_return = returns.std()
                
                if SCIPY_AVAILABLE:
                    var_parametric = stats.norm.ppf(1 - confidence, mean_return, std_return)
                else:
                    # 简化的正态分布分位数计算
                    # 使用近似公式计算正态分布的分位数
                    z_score = -1.96 if confidence == 0.95 else -2.58 if confidence == 0.99 else -1.65
                    var_parametric = mean_return + z_score * std_return
                
                var_results[f'var_{int(confidence*100)}'] = {
                    'historical': var_historical,
                    'parametric': var_parametric
                }
            
            # 条件风险价值(CVaR/Expected Shortfall)
            for confidence in confidence_levels:
                var_threshold = var_results[f'var_{int(confidence*100)}']['historical']
                tail_returns = returns[returns <= var_threshold]
                
                if len(tail_returns) > 0:
                    cvar = tail_returns.mean()
                    var_results[f'cvar_{int(confidence*100)}'] = cvar
            
            return var_results
            
        except Exception as e:
            logger.error(f"VaR计算失败: {e}")
            return {}
    
    def _calculate_drawdown(self, stock_data: pd.DataFrame) -> Dict[str, any]:
        """
        计算最大回撤
        
        Args:
            stock_data: 股票数据
            
        Returns:
            回撤指标
        """
        try:
            if 'close' not in stock_data.columns or len(stock_data) < 10:
                return {}
            
            prices = stock_data['close']
            
            # 计算累计收益
            cumulative_returns = (1 + prices.pct_change()).cumprod()
            
            # 计算滚动最大值
            rolling_max = cumulative_returns.expanding().max()
            
            # 计算回撤
            drawdown = (cumulative_returns - rolling_max) / rolling_max
            
            # 最大回撤
            max_drawdown = drawdown.min()
            
            # 最大回撤持续时间
            drawdown_duration = 0
            max_duration = 0
            current_duration = 0
            
            for dd in drawdown:
                if dd < 0:
                    current_duration += 1
                    max_duration = max(max_duration, current_duration)
                else:
                    current_duration = 0
            
            # 当前回撤
            current_drawdown = drawdown.iloc[-1]
            
            # 回撤恢复时间
            recovery_time = None
            if current_drawdown < 0:
                # 找到当前回撤开始的时间
                for i in range(len(drawdown) - 1, -1, -1):
                    if drawdown.iloc[i] == 0:
                        recovery_time = len(drawdown) - 1 - i
                        break
            
            return {
                'max_drawdown': max_drawdown,
                'max_drawdown_duration': max_duration,
                'current_drawdown': current_drawdown,
                'recovery_time': recovery_time,
                'drawdown_series': drawdown.to_dict()
            }
            
        except Exception as e:
            logger.error(f"回撤计算失败: {e}")
            return {}
    
    def _generate_risk_recommendations(self, 
                                     overall_risk: Dict,
                                     market_risk: Dict,
                                     liquidity_risk: Dict,
                                     volatility_risk: Dict) -> List[str]:
        """
        生成风险管理建议
        
        Args:
            overall_risk: 综合风险
            market_risk: 市场风险
            liquidity_risk: 流动性风险
            volatility_risk: 波动性风险
            
        Returns:
            风险管理建议列表
        """
        try:
            recommendations = []
            
            overall_level = overall_risk.get('level', 'medium')
            
            # 综合风险建议
            if overall_level == 'very_high':
                recommendations.append("整体风险极高，建议避免投资或立即减仓")
                recommendations.append("建议设置较紧的止损位（5-8%）")
            elif overall_level == 'high':
                recommendations.append("整体风险较高，建议谨慎投资，控制仓位")
                recommendations.append("建议设置止损位（8-12%）")
            elif overall_level == 'medium':
                recommendations.append("风险适中，建议适度投资，注意风险控制")
                recommendations.append("建议设置止损位（12-15%）")
            else:
                recommendations.append("风险相对较低，可以考虑适当增加仓位")
            
            # 市场风险建议
            if market_risk.get('level') == 'high':
                recommendations.append("市场系统性风险较高，建议关注大盘走势")
                
                beta = market_risk.get('details', {}).get('beta')
                if beta and beta > 1.5:
                    recommendations.append(f"Beta系数{beta:.2f}较高，股价波动将放大市场波动")
            
            # 流动性风险建议
            if liquidity_risk.get('level') == 'high':
                recommendations.append("流动性风险较高，建议分批建仓和减仓")
                recommendations.append("避免在市场恐慌时大量交易")
            
            # 波动性风险建议
            if volatility_risk.get('level') == 'high':
                recommendations.append("波动性风险较高，建议降低仓位或使用期权对冲")
                
                volatility = volatility_risk.get('details', {}).get('annualized_volatility')
                if volatility and volatility > 0.4:
                    recommendations.append(f"年化波动率{volatility:.1%}较高，注意仓位管理")
            
            # 通用建议
            recommendations.extend([
                "建议分散投资，不要将所有资金投入单一股票",
                "定期评估和调整投资组合",
                "保持理性，避免情绪化交易"
            ])
            
            return recommendations
            
        except Exception as e:
            logger.error(f"生成风险建议失败: {e}")
            return ["请注意投资风险，谨慎决策"]
    
    def _get_risk_level(self, score: float) -> str:
        """
        根据评分获取风险等级 (基于实际分数分布优化)
        评分越高，风险越低；评分越低，风险越高
        
        Args:
            score: 风险评分 (0-100, 分数越高越安全)
            
        Returns:
            风险等级 (中文)
        """
        # 基于实际测试结果调整阈值，让分布更合理
        if score >= 65:
            return '极低风险'  # 65-100: 极低风险
        elif score >= 58:
            return '低风险'    # 58-65:  低风险 
        elif score >= 52:
            return '中等风险'  # 52-58:  中等风险
        elif score >= 45:
            return '高风险'    # 45-52:  高风险
        else:
            return '极高风险'  # 0-45:   极高风险
    
    def _empty_risk_assessment(self) -> Dict[str, any]:
        """
        返回空风险评估结果
        
        Returns:
            空风险评估结果
        """
        return {
            'overall_risk': {'score': 50, 'level': 'medium'},
            'market_risk': {'score': 50, 'level': 'medium', 'details': {}},
            'liquidity_risk': {'score': 50, 'level': 'medium', 'details': {}},
            'volatility_risk': {'score': 50, 'level': 'medium', 'details': {}},
            'fundamental_risk': {'score': 50, 'level': 'medium', 'details': {}},
            'technical_risk': {'score': 50, 'level': 'medium', 'details': {}},
            'concentration_risk': {'score': 30, 'level': self._get_risk_level(30), 'details': {}},
            'var_metrics': {},
            'drawdown_metrics': {},
            'recommendations': ['数据不足，无法进行风险评估'],
            'assessment_time': datetime.now().isoformat()
        }
    
    def calculate_position_size(self, 
                              account_value: float,
                              risk_per_trade: float,
                              entry_price: float,
                              stop_loss_price: float) -> Dict[str, any]:
        """
        计算仓位大小
        
        Args:
            account_value: 账户总价值
            risk_per_trade: 每笔交易风险比例
            entry_price: 入场价格
            stop_loss_price: 止损价格
            
        Returns:
            仓位计算结果
        """
        try:
            if entry_price <= 0 or stop_loss_price <= 0:
                return {'error': '价格必须大于0'}
            
            # 计算每股风险
            risk_per_share = abs(entry_price - stop_loss_price)
            
            if risk_per_share == 0:
                return {'error': '入场价格和止损价格不能相同'}
            
            # 计算总风险金额
            total_risk = account_value * risk_per_trade
            
            # 计算股票数量
            shares = int(total_risk / risk_per_share)
            
            # 计算实际投资金额
            investment_amount = shares * entry_price
            
            # 计算仓位比例
            position_ratio = investment_amount / account_value
            
            return {
                'shares': shares,
                'investment_amount': investment_amount,
                'position_ratio': position_ratio,
                'risk_amount': total_risk,
                'risk_per_share': risk_per_share,
                'effective_risk_ratio': (shares * risk_per_share) / account_value
            }
            
        except Exception as e:
            logger.error(f"仓位计算失败: {e}")
            return {'error': str(e)}