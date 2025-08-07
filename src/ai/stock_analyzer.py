import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from loguru import logger
import joblib
import os

from .ml_models import MLModels
from .feature_engineer import FeatureEngineer
from .risk_manager import RiskManager
from config.config import config

class StockAnalyzer:
    """股票AI分析器"""
    
    def __init__(self):
        """
        初始化股票分析器
        """
        self.feature_engineer = FeatureEngineer()
        self.ml_models = MLModels()
        self.risk_manager = RiskManager()
        
        # 初始化数据获取器
        from src.data.data_fetcher import DataFetcher
        self.data_fetcher = DataFetcher()
        
        # 模型缓存
        self.models_cache = {}
        
        logger.info("股票AI分析器初始化完成")
    
    def analyze_stock(self, 
                     ts_code_or_data,
                     stock_data=None, 
                     financial_data: Dict = None,
                     market_data: Dict = None) -> Dict[str, any]:
        """
        综合分析单只股票
        
        Args:
            ts_code_or_data: 股票代码(str) 或 股票数据(DataFrame)
            stock_data: 股票价格数据 (当第一个参数是股票代码时使用)
            financial_data: 财务数据
            market_data: 市场数据
            
        Returns:
            分析结果字典
        """
        try:
            # 处理参数兼容性
            if isinstance(ts_code_or_data, str):
                # 第一个参数是股票代码
                ts_code = ts_code_or_data
                if stock_data is None:
                    # 自动获取股票数据
                    stock_data = self.data_fetcher.get_stock_data(ts_code, period='6m')
                    if stock_data is None or stock_data.empty:
                        return self._empty_analysis()
            else:
                # 第一个参数是股票数据
                stock_data = ts_code_or_data
                ts_code = "UNKNOWN"
            
            if stock_data.empty:
                return self._empty_analysis()
            
            # 特征工程
            features = self.feature_engineer.create_features(
                stock_data, financial_data, market_data
            )
            
            # 技术分析
            technical_score = self._calculate_technical_score(stock_data)
            
            # 基本面分析
            fundamental_score = self._calculate_fundamental_score(financial_data)
            
            # 市场情绪分析
            sentiment_score = self._calculate_sentiment_score(stock_data, market_data)
            
            # 机器学习预测
            ml_prediction = self._get_ml_prediction(features)
            
            # 风险评估
            risk_assessment = self.risk_manager.assess_risk(
                stock_data, financial_data, market_data
            )
            
            # 综合评分
            overall_score = self._calculate_overall_score(
                technical_score, fundamental_score, sentiment_score, ml_prediction
            )
            
            # 生成建议
            recommendation = self._generate_recommendation(
                overall_score, risk_assessment, stock_data
            )
            
            # 生成交易信号
            signals = self._generate_trading_signals(stock_data, overall_score.get('score', 50))
            
            # 计算技术指标
            technical_indicators = self._calculate_technical_indicators(stock_data)
            
            # 价格预测
            price_prediction = self._predict_price_target(stock_data, ml_prediction)
            
            return {
                'overall_score': overall_score,
                'technical_score': technical_score,
                'fundamental_score': fundamental_score,
                'sentiment_score': sentiment_score,
                'ml_prediction': ml_prediction,
                'risk_assessment': risk_assessment,
                'recommendation': recommendation['action'],
                'confidence': recommendation['confidence'],
                'reason': recommendation['reason'],
                'signals': signals,
                'technical_indicators': technical_indicators,
                'price_prediction': price_prediction,
                'risks': risk_assessment.get('warnings', []),
                'analysis_time': datetime.now().isoformat(),
                'features': features.to_dict() if not features.empty else {}
            }
            
        except Exception as e:
            logger.error(f"股票分析失败: {e}")
            return self._empty_analysis()
    
    def _calculate_technical_score(self, stock_data: pd.DataFrame) -> Dict[str, any]:
        """
        计算技术分析评分
        
        Args:
            stock_data: 股票数据
            
        Returns:
            技术分析评分
        """
        try:
            if len(stock_data) < 20:
                return {'score': 50, 'signals': [], 'details': {}}
            
            latest = stock_data.iloc[-1]
            signals = []
            score = 50  # 基础分数
            details = {}
            
            # 趋势分析 - 增加敏感度
            if 'ma5' in latest and 'ma20' in latest and 'ma60' in latest:
                ma5 = latest['ma5']
                ma20 = latest['ma20']
                ma60 = latest['ma60']
                price = latest['close']
                
                # 计算均线趋势强度
                ma5_slope = (ma5 - stock_data['ma5'].iloc[-5]) / stock_data['ma5'].iloc[-5] * 100 if len(stock_data) >= 5 else 0
                ma20_slope = (ma20 - stock_data['ma20'].iloc[-10]) / stock_data['ma20'].iloc[-10] * 100 if len(stock_data) >= 10 else 0
                
                # 均线排列 - 根据强度给分
                if ma5 > ma20 > ma60 and price > ma5:
                    base_score = 20
                    # 根据趋势强度调整
                    if ma5_slope > 3:  # 强势上涨
                        score += base_score + 10
                        signals.append('强势多头排列')
                    elif ma5_slope > 0:
                        score += base_score
                        signals.append('多头排列')
                    else:
                        score += base_score - 5
                        signals.append('多头排列(趋势减弱)')
                        
                elif ma5 < ma20 < ma60 and price < ma5:
                    base_score = -20
                    # 根据趋势强度调整
                    if ma5_slope < -3:  # 强势下跌
                        score += base_score - 10
                        signals.append('强势空头排列')
                    elif ma5_slope < 0:
                        score += base_score
                        signals.append('空头排列')
                    else:
                        score += base_score + 5
                        signals.append('空头排列(下跌减缓)')
                
                # 价格与均线的偏离度
                price_deviation = abs(price - ma20) / ma20 * 100
                if price_deviation > 10:  # 偏离过大
                    if price > ma20:
                        score -= 8  # 可能回调
                        signals.append('价格偏离均线过高')
                    else:
                        score += 8  # 可能反弹
                        signals.append('价格偏离均线过低')
                
                details['ma_trend'] = '上涨' if ma5 > ma20 else '下跌'
                details['ma5_slope'] = ma5_slope
                details['price_deviation'] = price_deviation
            
            # MACD分析 - 增加敏感度
            if 'macd' in latest and 'macd_signal' in latest:
                macd = latest['macd']
                macd_signal = latest['macd_signal']
                
                # 计算MACD强度
                macd_diff = macd - macd_signal
                macd_strength = abs(macd_diff) / abs(macd_signal) if abs(macd_signal) > 0.001 else 0
                
                if macd > macd_signal:  # 金叉
                    if macd > 0:
                        base_score = 15
                        if macd_strength > 0.1:  # 强金叉
                            score += base_score + 10
                            signals.append('MACD强势金叉')
                        else:
                            score += base_score
                            signals.append('MACD金叉向上')
                    else:
                        score += 8  # 零轴下方金叉
                        signals.append('MACD零下金叉')
                        
                elif macd < macd_signal:  # 死叉
                    if macd < 0:
                        base_score = -15
                        if macd_strength > 0.1:  # 强死叉
                            score += base_score - 10
                            signals.append('MACD强势死叉')
                        else:
                            score += base_score
                            signals.append('MACD死叉向下')
                    else:
                        score -= 8  # 零轴上方死叉
                        signals.append('MACD零上死叉')
                
                # MACD背离检测
                if len(stock_data) >= 10:
                    recent_price_high = stock_data['close'].tail(10).max()
                    recent_macd_high = stock_data['macd'].tail(10).max() if 'macd' in stock_data.columns else 0
                    
                    if latest['close'] >= recent_price_high and macd < recent_macd_high:
                        score -= 12
                        signals.append('MACD顶背离')
                    elif latest['close'] <= stock_data['close'].tail(10).min() and macd > stock_data['macd'].tail(10).min():
                        score += 12
                        signals.append('MACD底背离')
                
                details['macd_status'] = 'bullish' if macd > macd_signal else 'bearish'
                details['macd_strength'] = macd_strength
            
            # RSI分析 - 增加敏感度和层次
            if 'rsi6' in latest:
                rsi = latest['rsi6']
                
                # 多层次RSI分析
                if rsi < 20:  # 极度超卖
                    score += 18
                    signals.append('RSI极度超卖')
                elif rsi < 30:  # 超卖
                    score += 12
                    signals.append('RSI超卖')
                elif rsi < 40:  # 偏弱
                    score += 5
                    signals.append('RSI偏弱')
                elif rsi > 80:  # 极度超买
                    score -= 18
                    signals.append('RSI极度超买')
                elif rsi > 70:  # 超买
                    score -= 12
                    signals.append('RSI超买')
                elif rsi > 60:  # 偏强
                    score -= 5
                    signals.append('RSI偏强')
                elif 45 <= rsi <= 55:  # 中性区间
                    score += 3
                    signals.append('RSI中性')
                
                # RSI钝化检测
                if len(stock_data) >= 5 and 'rsi6' in stock_data.columns:
                    rsi_series = stock_data['rsi6'].tail(5)
                    if rsi > 70 and all(r > 65 for r in rsi_series):
                        score -= 8  # RSI高位钝化
                        signals.append('RSI高位钝化')
                    elif rsi < 30 and all(r < 35 for r in rsi_series):
                        score += 8  # RSI低位钝化
                        signals.append('RSI低位钝化')
                
                details['rsi_level'] = 'oversold' if rsi < 30 else 'overbought' if rsi > 70 else 'neutral'
                details['rsi_value'] = rsi
            
            # KDJ分析
            if 'kdj_k' in latest and 'kdj_d' in latest:
                k = latest['kdj_k']
                d = latest['kdj_d']
                
                if k > d and k < 80:
                    score += 5
                    signals.append('KDJ金叉')
                elif k < d and k > 20:
                    score -= 5
                    signals.append('KDJ死叉')
                
                details['kdj_status'] = 'bullish' if k > d else 'bearish'
            
            # 布林带分析
            if 'bb_upper' in latest and 'bb_lower' in latest and 'close' in latest:
                price = latest['close']
                bb_upper = latest['bb_upper']
                bb_lower = latest['bb_lower']
                bb_middle = latest.get('bb_middle', (bb_upper + bb_lower) / 2)
                
                if price < bb_lower:
                    score += 8
                    signals.append('布林带下轨支撑')
                elif price > bb_upper:
                    score -= 8
                    signals.append('布林带上轨压力')
                
                details['bb_position'] = 'below_lower' if price < bb_lower else 'above_upper' if price > bb_upper else 'middle'
            
            # 成交量分析
            if 'vol' in stock_data.columns and len(stock_data) >= 5:
                recent_vol = stock_data['vol'].tail(5).mean()
                avg_vol = stock_data['vol'].mean()
                
                if recent_vol > avg_vol * 1.5:
                    score += 5
                    signals.append('放量上涨' if latest['close'] > stock_data['close'].iloc[-2] else '放量下跌')
                
                details['volume_trend'] = 'increasing' if recent_vol > avg_vol else 'decreasing'
            
            # 价格动量
            if len(stock_data) >= 10:
                price_change_5d = (latest['close'] - stock_data['close'].iloc[-6]) / stock_data['close'].iloc[-6] * 100
                
                if price_change_5d > 5:
                    score += 5
                    signals.append('短期强势')
                elif price_change_5d < -5:
                    score -= 5
                    signals.append('短期弱势')
                
                details['momentum_5d'] = price_change_5d
            
            # 确保分数在0-100范围内
            score = max(0, min(100, score))
            
            return {
                'score': score,
                'signals': signals,
                'details': details,
                'level': self._get_score_level(score)
            }
            
        except Exception as e:
            logger.error(f"技术分析计算失败: {e}")
            return {'score': 50, 'signals': [], 'details': {}}
    
    def _calculate_fundamental_score(self, financial_data: Dict) -> Dict[str, any]:
        """
        计算基本面分析评分
        
        Args:
            financial_data: 财务数据
            
        Returns:
            基本面分析评分
        """
        try:
            if not financial_data or 'indicators' not in financial_data:
                return {'score': 50, 'signals': [], 'details': {}}
            
            indicators = financial_data['indicators']
            if indicators.empty:
                return {'score': 50, 'signals': [], 'details': {}}
            
            latest_indicators = indicators.iloc[0]
            score = 50
            signals = []
            details = {}
            
            # PE估值分析
            pe = latest_indicators.get('pe', None)
            if pe and pe > 0:
                if pe < 15:
                    score += 10
                    signals.append('PE估值偏低')
                elif pe > 50:
                    score -= 10
                    signals.append('PE估值偏高')
                
                details['pe_ratio'] = pe
            
            # PB估值分析
            pb = latest_indicators.get('pb', None)
            if pb and pb > 0:
                if pb < 1.5:
                    score += 8
                    signals.append('PB估值偏低')
                elif pb > 5:
                    score -= 8
                    signals.append('PB估值偏高')
                
                details['pb_ratio'] = pb
            
            # ROE分析
            roe = latest_indicators.get('roe', None)
            if roe:
                if roe > 15:
                    score += 12
                    signals.append('ROE优秀')
                elif roe > 10:
                    score += 6
                    signals.append('ROE良好')
                elif roe < 5:
                    score -= 8
                    signals.append('ROE偏低')
                
                details['roe'] = roe
            
            # 毛利率分析
            gross_margin = latest_indicators.get('gross_margin', None)
            if gross_margin:
                if gross_margin > 40:
                    score += 8
                    signals.append('毛利率优秀')
                elif gross_margin < 20:
                    score -= 5
                    signals.append('毛利率偏低')
                
                details['gross_margin'] = gross_margin
            
            # 净利率分析
            net_margin = latest_indicators.get('netprofit_margin', None)
            if net_margin:
                if net_margin > 15:
                    score += 8
                    signals.append('净利率优秀')
                elif net_margin < 5:
                    score -= 5
                    signals.append('净利率偏低')
                
                details['net_margin'] = net_margin
            
            # 资产负债率分析
            debt_ratio = latest_indicators.get('debt_to_assets', None)
            if debt_ratio:
                if debt_ratio < 30:
                    score += 5
                    signals.append('负债率健康')
                elif debt_ratio > 70:
                    score -= 8
                    signals.append('负债率偏高')
                
                details['debt_ratio'] = debt_ratio
            
            # 流动比率分析
            current_ratio = latest_indicators.get('current_ratio', None)
            if current_ratio:
                if current_ratio > 2:
                    score += 5
                    signals.append('流动性充足')
                elif current_ratio < 1:
                    score -= 8
                    signals.append('流动性不足')
                
                details['current_ratio'] = current_ratio
            
            # 确保分数在0-100范围内
            score = max(0, min(100, score))
            
            return {
                'score': score,
                'signals': signals,
                'details': details,
                'level': self._get_score_level(score)
            }
            
        except Exception as e:
            logger.error(f"基本面分析计算失败: {e}")
            return {'score': 50, 'signals': [], 'details': {}}
    
    def _get_consecutive_trend_days(self, prices):
        """计算连续上涨或下跌天数（正数表示连续上涨，负数表示连续下跌）"""
        if len(prices) < 2:
            return 0
        
        consecutive = 0
        current_trend = None  # True for up, False for down
        
        for i in range(len(prices) - 1, 0, -1):
            if prices[i] > prices[i-1]:  # 上涨
                if current_trend is None:
                    current_trend = True
                    consecutive = 1
                elif current_trend:
                    consecutive += 1
                else:
                    break
            elif prices[i] < prices[i-1]:  # 下跌
                if current_trend is None:
                    current_trend = False
                    consecutive = 1
                elif not current_trend:
                    consecutive += 1
                else:
                    break
            else:  # 平盘
                break
        
        return consecutive if current_trend else -consecutive

    def _calculate_sentiment_score(self, 
                                 stock_data: pd.DataFrame, 
                                 market_data: Dict = None) -> Dict[str, any]:
        """
        计算市场情绪评分
        
        Args:
            stock_data: 股票数据
            market_data: 市场数据
            
        Returns:
            情绪分析评分
        """
        try:
            score = 50
            signals = []
            details = {}
            
            if len(stock_data) < 10:
                return {'score': score, 'signals': signals, 'details': details}
            
            # 相对强度分析 - 增加敏感度
            if market_data and '上证指数' in market_data:
                index_data = market_data['上证指数']
                if not index_data.empty and len(index_data) >= len(stock_data):
                    # 计算多个时间窗口的相对表现
                    periods = [5, 10, 20]
                    relative_strengths = []
                    
                    for period in periods:
                        if len(stock_data) >= period and len(index_data) >= period:
                            stock_return = (stock_data['close'].iloc[-1] - stock_data['close'].iloc[-period]) / stock_data['close'].iloc[-period]
                            index_return = (index_data['close'].iloc[-1] - index_data['close'].iloc[-period]) / index_data['close'].iloc[-period]
                            
                            relative_strength = stock_return - index_return
                            relative_strengths.append(relative_strength)
                    
                    if relative_strengths:
                        avg_relative_strength = sum(relative_strengths) / len(relative_strengths)
                        
                        # 根据相对强度程度给分
                        if avg_relative_strength > 0.08:  # 强势跑赢
                            score += 20
                            signals.append('强势跑赢大盘')
                        elif avg_relative_strength > 0.03:  # 跑赢
                            score += 12
                            signals.append('跑赢大盘')
                        elif avg_relative_strength > -0.03:  # 同步
                            score += 3
                            signals.append('与大盘同步')
                        elif avg_relative_strength > -0.08:  # 跑输
                            score -= 12
                            signals.append('跑输大盘')
                        else:  # 明显跑输
                            score -= 20
                            signals.append('明显跑输大盘')
                        
                        details['relative_strength'] = avg_relative_strength
            
            # 成交量情绪 - 增加敏感度
            if 'vol' in stock_data.columns:
                recent_vol = stock_data['vol'].tail(5).mean()
                avg_vol = stock_data['vol'].mean()
                vol_ratio = recent_vol / avg_vol if avg_vol > 0 else 1
                
                # 更细致的成交量分析
                if vol_ratio > 3:  # 极度放量
                    score += 15
                    signals.append('极度放量')
                elif vol_ratio > 2:  # 明显放量
                    score += 10
                    signals.append('明显放量')
                elif vol_ratio > 1.5:  # 放量
                    score += 6
                    signals.append('成交活跃')
                elif vol_ratio < 0.3:  # 极度萎缩
                    score -= 15
                    signals.append('成交极度萎缩')
                elif vol_ratio < 0.5:  # 萎缩
                    score -= 8
                    signals.append('成交清淡')
                elif vol_ratio < 0.8:  # 偏淡
                    score -= 3
                    signals.append('成交偏淡')
                
                # 量价配合分析
                if len(stock_data) >= 2:
                    price_change = (stock_data['close'].iloc[-1] - stock_data['close'].iloc[-2]) / stock_data['close'].iloc[-2]
                    
                    if price_change > 0.02 and vol_ratio > 1.5:  # 放量上涨
                        score += 8
                        signals.append('量价配合上涨')
                    elif price_change < -0.02 and vol_ratio > 1.5:  # 放量下跌
                        score -= 12
                        signals.append('放量下跌')
                    elif price_change > 0.02 and vol_ratio < 0.8:  # 缩量上涨
                        score -= 5
                        signals.append('缩量上涨(动力不足)')
                    elif price_change < -0.02 and vol_ratio < 0.8:  # 缩量下跌
                        score += 3
                        signals.append('缩量下跌(抛压减轻)')
                
                details['volume_sentiment'] = vol_ratio
            
            # 价格波动情绪
            if len(stock_data) >= 20:
                recent_volatility = stock_data['close'].tail(10).pct_change().std()
                historical_volatility = stock_data['close'].pct_change().std()
                
                volatility_ratio = recent_volatility / historical_volatility if historical_volatility > 0 else 1
                
                if volatility_ratio > 1.5:
                    score -= 5
                    signals.append('波动加剧')
                elif volatility_ratio < 0.7:
                    score += 3
                    signals.append('波动收敛')
                
                details['volatility_sentiment'] = volatility_ratio
            
            # 连续涨跌情绪
            if len(stock_data) >= 5:
                recent_changes = stock_data['close'].tail(5).pct_change().dropna()
                
                consecutive_up = 0
                consecutive_down = 0
                
                for change in recent_changes:
                    if change > 0:
                        consecutive_up += 1
                        consecutive_down = 0
                    elif change < 0:
                        consecutive_down += 1
                        consecutive_up = 0
                
                if consecutive_up >= 3:
                    score += 5
                    signals.append('连续上涨')
                elif consecutive_down >= 3:
                    score -= 5
                    signals.append('连续下跌')
                
                details['consecutive_trend'] = {
                    'up_days': consecutive_up,
                    'down_days': consecutive_down
                }
            
            # 确保分数在0-100范围内
            score = max(0, min(100, score))
            
            return {
                'score': score,
                'signals': signals,
                'details': details,
                'level': self._get_score_level(score)
            }
            
        except Exception as e:
            logger.error(f"情绪分析计算失败: {e}")
            return {'score': 50, 'signals': [], 'details': {}}
    
    def _get_ml_prediction(self, features: pd.DataFrame) -> Dict[str, any]:
        """
        获取机器学习预测结果
        
        Args:
            features: 特征数据
            
        Returns:
            预测结果
        """
        try:
            if features.empty:
                return {'prediction': 0, 'confidence': 0, 'model': 'none'}
            
            # 使用机器学习模型进行预测
            prediction_result = self.ml_models.predict(features)
            
            return prediction_result
            
        except Exception as e:
            logger.error(f"机器学习预测失败: {e}")
            return {'prediction': 0, 'confidence': 0, 'model': 'none'}
    
    def _calculate_overall_score(self, 
                               technical_score: Dict, 
                               fundamental_score: Dict, 
                               sentiment_score: Dict, 
                               ml_prediction: Dict) -> Dict[str, any]:
        """
        计算综合评分
        
        Args:
            technical_score: 技术分析评分
            fundamental_score: 基本面评分
            sentiment_score: 情绪评分
            ml_prediction: 机器学习预测
            
        Returns:
            综合评分
        """
        try:
            # 权重配置 (确保总和为1.0)
            weights = {
                'technical': config.ai.technical_weight,
                'fundamental': config.ai.fundamental_weight,
                'sentiment': config.ai.sentiment_weight,
                'ml': config.ai.ml_weight
            }
            
            # 验证权重总和
            weight_sum = sum(weights.values())
            if abs(weight_sum - 1.0) > 0.01:  # 允许小的浮点误差
                logger.warning(f"权重总和不等于1: {weight_sum}, 正在自动调整")
                # 按比例调整权重
                for key in weights:
                    weights[key] = weights[key] / weight_sum
            
            # 获取各项分数
            tech_score = technical_score.get('score', 50)
            fund_score = fundamental_score.get('score', 50)
            sent_score = sentiment_score.get('score', 50)
            ml_score = ml_prediction.get('prediction', 0) * 50 + 50  # 将ML预测转换为0-100分
            
            # 计算加权平均分
            overall_score = (
                tech_score * weights['technical'] +
                fund_score * weights['fundamental'] +
                sent_score * weights['sentiment'] +
                ml_score * weights['ml']
            )
            
            # 确保分数在0-100范围内
            overall_score = max(0, min(100, overall_score))
            
            return {
                'score': overall_score,
                'level': self._get_score_level(overall_score),
                'weights': weights,
                'components': {
                    'technical': tech_score,
                    'fundamental': fund_score,
                    'sentiment': sent_score,
                    'ml': ml_score
                },
                'weight_sum': sum(weights.values())
            }
            
        except Exception as e:
            logger.error(f"综合评分计算失败: {e}")
            return {'score': 50, 'level': 'neutral'}
    
    def _generate_recommendation(self, 
                               overall_score: Dict, 
                               risk_assessment: Dict, 
                               stock_data: pd.DataFrame) -> Dict[str, any]:
        """
        生成投资建议
        
        Args:
            overall_score: 综合评分
            risk_assessment: 风险评估
            stock_data: 股票数据
            
        Returns:
            投资建议
        """
        try:
            score = overall_score['score']
            risk_level = risk_assessment.get('level', '中等风险')
            
            # 基础建议
            if score >= 80:
                action = 'strong_buy'
                action_text = '强烈买入'
            elif score >= 70:
                action = 'buy'
                action_text = '买入'
            elif score >= 60:
                action = 'weak_buy'
                action_text = '谨慎买入'
            elif score >= 40:
                action = 'hold'
                action_text = '持有'
            elif score >= 30:
                action = 'weak_sell'
                action_text = '谨慎卖出'
            else:
                action = 'sell'
                action_text = '卖出'
            
            # 风险调整
            if risk_level in ['高风险', '极高风险']:
                if action in ['strong_buy', 'buy']:
                    action = 'weak_buy'
                    action_text = '谨慎买入（高风险）'
                elif action == 'weak_buy':
                    action = 'hold'
                    action_text = '持有（高风险）'
            
            # 生成具体建议
            suggestions = []
            
            if not stock_data.empty:
                current_price = stock_data['close'].iloc[-1]
                
                # 买入建议
                if action in ['strong_buy', 'buy', 'weak_buy']:
                    if 'ma20' in stock_data.columns:
                        ma20 = stock_data['ma20'].iloc[-1]
                        if current_price > ma20:
                            suggestions.append(f"当前价格{current_price:.2f}元，建议在{ma20:.2f}元附近分批买入")
                        else:
                            suggestions.append(f"当前价格{current_price:.2f}元，可考虑当前价位买入")
                    
                    suggestions.append("建议分批建仓，控制仓位")
                    suggestions.append(f"止损位建议设在{current_price * (1 - config.trading.stop_loss_pct):.2f}元")
                    suggestions.append(f"止盈位建议设在{current_price * (1 + config.trading.take_profit_pct):.2f}元")
                
                # 卖出建议
                elif action in ['sell', 'weak_sell']:
                    suggestions.append("建议逐步减仓或清仓")
                    suggestions.append("注意控制风险，及时止损")
                
                # 持有建议
                else:
                    suggestions.append("建议继续持有，观察后续走势")
                    suggestions.append("注意关键技术位的突破情况")
            
            # 风险提示
            risk_warnings = []
            if risk_level in ['高风险', '极高风险']:
                risk_warnings.append("该股票风险较高，请谨慎投资")
            if risk_assessment.get('volatility', 0) > 0.3:
                risk_warnings.append("该股票波动较大，注意仓位控制")
            
            return {
                'action': action,
                'action_text': action_text,
                'confidence': min(100, abs(score - 50) * 2),  # 置信度
                'suggestions': suggestions,
                'risk_warnings': risk_warnings,
                'target_price': self._calculate_target_price(stock_data, overall_score),
                'time_horizon': '1-3个月'  # 建议持有期
            }
            
        except Exception as e:
            logger.error(f"生成投资建议失败: {e}")
            return {
                'action': 'hold',
                'action_text': '持有',
                'confidence': 0,
                'suggestions': ['数据不足，建议谨慎操作'],
                'risk_warnings': ['请注意投资风险']
            }
    
    def _calculate_target_price(self, stock_data: pd.DataFrame, overall_score: Dict) -> Optional[float]:
        """
        计算目标价格
        
        Args:
            stock_data: 股票数据
            overall_score: 综合评分
            
        Returns:
            目标价格
        """
        try:
            if stock_data.empty:
                return None
            
            current_price = stock_data['close'].iloc[-1]
            score = overall_score['score']
            
            # 基于评分计算目标价格
            if score >= 80:
                target_multiplier = 1.2  # 20%上涨空间
            elif score >= 70:
                target_multiplier = 1.15  # 15%上涨空间
            elif score >= 60:
                target_multiplier = 1.1   # 10%上涨空间
            elif score >= 40:
                target_multiplier = 1.0   # 持平
            else:
                target_multiplier = 0.9   # 10%下跌空间
            
            target_price = current_price * target_multiplier
            
            return round(target_price, 2)
            
        except Exception as e:
            logger.error(f"目标价格计算失败: {e}")
            return None
    
    def _get_score_level(self, score: float) -> str:
        """
        获取评分等级 - 优化分布，增加区分度
        
        Args:
            score: 评分
            
        Returns:
            评分等级（中文）
        """
        # 调整阈值，让分布更合理，增加敏感度
        if score >= 85:
            return '优秀'      # 85-100: 优秀 (约5-10%)
        elif score >= 75:
            return '良好'      # 75-85:  良好 (约15-20%) 
        elif score >= 65:
            return '一般'      # 65-75:  一般 (约25-30%)
        elif score >= 50:
            return '中性'      # 50-65:  中性 (约30-35%)
        elif score >= 35:
            return '较差'      # 35-50:  较差 (约15-20%)
        else:
            return '很差'      # 0-35:   很差 (约5-10%)
    
    def _empty_analysis(self) -> Dict[str, any]:
        """
        返回空分析结果
        
        Returns:
            空分析结果
        """
        return {
            'overall_score': {'score': 50, 'level': 'neutral'},
            'technical_score': {'score': 50, 'signals': [], 'details': {}},
            'fundamental_score': {'score': 50, 'signals': [], 'details': {}},
            'sentiment_score': {'score': 50, 'signals': [], 'details': {}},
            'ml_prediction': {'prediction': 0, 'confidence': 0},
            'risk_assessment': {'level': '中等风险'},
            'recommendation': {
                'action': 'hold',
                'action_text': '数据不足',
                'confidence': 0,
                'suggestions': ['数据不足，无法分析'],
                'risk_warnings': ['请注意投资风险']
            },
            'analysis_time': datetime.now().isoformat(),
            'features': {}
        }
    
    def batch_analyze(self, stocks_data: Dict[str, pd.DataFrame]) -> Dict[str, Dict]:
        """
        批量分析股票
        
        Args:
            stocks_data: 股票数据字典
            
        Returns:
            批量分析结果
        """
        try:
            results = {}
            
            for ts_code, stock_data in stocks_data.items():
                try:
                    analysis = self.analyze_stock(stock_data)
                    results[ts_code] = analysis
                except Exception as e:
                    logger.error(f"分析{ts_code}失败: {e}")
                    results[ts_code] = self._empty_analysis()
            
            return results
            
        except Exception as e:
            logger.error(f"批量分析失败: {e}")
            return {}
    
    def get_top_stocks(self, 
                      analysis_results: Dict[str, Dict], 
                      top_n: int = 10,
                      min_score: float = 60) -> List[Dict]:
        """
        获取评分最高的股票
        
        Args:
            analysis_results: 分析结果字典
            top_n: 返回数量
            min_score: 最低评分
            
        Returns:
            排序后的股票列表
        """
        try:
            stocks = []
            
            for ts_code, analysis in analysis_results.items():
                score = analysis.get('overall_score', {}).get('score', 0)
                if score >= min_score:
                    stocks.append({
                        'ts_code': ts_code,
                        'score': score,
                        'recommendation': analysis.get('recommendation', {}),
                        'analysis': analysis
                    })
            
            # 按评分排序
            stocks.sort(key=lambda x: x['score'], reverse=True)
            
            return stocks[:top_n]
            
        except Exception as e:
            logger.error(f"获取优质股票失败: {e}")
            return []
            
    def screen_stocks(self, stock_list: List[str], min_score: float = 70, 
                     risk_level: str = "中等风险", market_cap: str = "不限") -> List[Dict]:
        """
        智能股票筛选
        
        Args:
            stock_list: 股票代码列表
            min_score: 最低评分要求
            risk_level: 风险承受度
            market_cap: 市值偏好
            
        Returns:
            筛选结果列表
        """
        try:
            logger.info(f"开始筛选股票，最低评分: {min_score}, 风险级别: {risk_level}")
            
            results = []
            
            for ts_code in stock_list:
                try:
                    # 获取股票数据
                    stock_data = self.data_fetcher.get_stock_data(ts_code, period='6m')
                    if stock_data is None or stock_data.empty:
                        continue
                    
                    # 进行AI分析
                    analysis = self.analyze_stock(ts_code, stock_data)
                    if not analysis:
                        continue
                    
                    score = analysis.get('overall_score', {}).get('score', 0)
                    
                    # 评分筛选
                    if score < min_score:
                        continue
                    
                    # 风险筛选 - 修复逻辑，让不同风险偏好能找到合适的股票
                    risk_assessment = analysis.get('risk_assessment', {})
                    overall_risk = risk_assessment.get('overall_risk', {})
                    stock_risk_level = overall_risk.get('level', '中等风险')
                    
                    # 更灵活的风险匹配逻辑
                    risk_match = False
                    if risk_level == "低风险":
                        # 低风险偏好：接受低风险和部分中等风险股票
                        if stock_risk_level in ["极低风险", "低风险"]:
                            risk_match = True
                        elif stock_risk_level == "中等风险":
                            # 对于中等风险股票，查看具体评分
                            risk_score = overall_risk.get('score', 50)
                            if risk_score <= 45:  # 中等风险中的低分段
                                risk_match = True
                    elif risk_level == "中等风险":
                        # 中等风险偏好：接受低风险到高风险的广泛范围
                        if stock_risk_level in ["极低风险", "低风险", "中等风险", "高风险"]:
                            risk_match = True
                        elif stock_risk_level == "极高风险":
                            # 对于极高风险，查看具体评分
                            risk_score = overall_risk.get('score', 50)
                            if risk_score <= 85:  # 极高风险中的低分段
                                risk_match = True
                    elif risk_level == "高风险":
                        # 高风险偏好：接受所有风险级别
                        risk_match = True
                    
                    if not risk_match:
                        continue
                    
                    # 获取股票基本信息
                    latest_price = stock_data['close'].iloc[-1]
                    prev_price = stock_data['close'].iloc[-2] if len(stock_data) > 1 else latest_price
                    
                    # 计算目标价格
                    target_price = analysis.get('price_prediction', {}).get('target_price', latest_price * 1.1)
                    upside = ((target_price - latest_price) / latest_price) * 100 if latest_price > 0 else 0
                    
                    # 获取股票名称
                    stock_name = self._get_stock_name(ts_code)
                    
                    result = {
                        'symbol': ts_code,
                        'name': stock_name,
                        'score': round(score, 1),
                        'recommendation': analysis.get('recommendation', '持有'),
                        'risk_level': stock_risk_level,
                        'current_price': round(latest_price, 2),
                        'target_price': round(target_price, 2),
                        'upside': round(upside, 1),
                        'confidence': analysis.get('confidence', 0.5),
                        'reason': analysis.get('reason', ''),
                        'analysis_date': stock_data.index[-1].strftime('%Y-%m-%d') if hasattr(stock_data.index[-1], 'strftime') else str(stock_data.index[-1])
                    }
                    
                    results.append(result)
                    
                except Exception as e:
                    logger.error(f"分析股票 {ts_code} 时出错: {e}")
                    continue
            
            # 按评分排序
            results.sort(key=lambda x: x['score'], reverse=True)
            
            logger.info(f"筛选完成，找到 {len(results)} 只符合条件的股票")
            return results
            
        except Exception as e:
            logger.error(f"股票筛选失败: {e}")
            return []
    
    def _get_stock_name(self, ts_code: str) -> str:
        """获取股票名称"""
        try:
            # 简单的股票名称映射
            name_map = {
                '000001.SZ': '平安银行',
                '000002.SZ': '万科A',
                '600000.SH': '浦发银行',
                '600036.SH': '招商银行',
                '000858.SZ': '五粮液',
                '600519.SH': '贵州茅台',
                '000858.SZ': '五粮液',
                'AAPL': '苹果',
                'TSLA': '特斯拉',
                'MSFT': '微软',
                'GOOGL': '谷歌',
                'AMZN': '亚马逊'
            }
            
            return name_map.get(ts_code, ts_code.split('.')[0])
            
        except Exception:
            return ts_code
    
    def _generate_trading_signals(self, stock_data: pd.DataFrame, overall_score: float) -> Dict[str, str]:
        """生成交易信号"""
        signals = {}
        
        if stock_data.empty:
            return signals
        
        try:
            # 获取最新数据
            latest = stock_data.iloc[-1]
            prev = stock_data.iloc[-2] if len(stock_data) > 1 else latest
            
            # 价格信号
            price_change_pct = ((latest['close'] - prev['close']) / prev['close']) * 100
            if price_change_pct > 5:
                signals['price'] = "强势上涨"
            elif price_change_pct > 2:
                signals['price'] = "温和上涨"
            elif price_change_pct < -5:
                signals['price'] = "大幅下跌"
            elif price_change_pct < -2:
                signals['price'] = "温和下跌"
            else:
                signals['price'] = "震荡整理"
            
            # 成交量信号
            if 'volume' in stock_data.columns:
                vol_change_pct = ((latest['volume'] - prev['volume']) / prev['volume']) * 100
                if vol_change_pct > 50:
                    signals['volume'] = "放量"
                elif vol_change_pct < -30:
                    signals['volume'] = "缩量"
                else:
                    signals['volume'] = "温和"
            
            # 技术指标信号
            if 'ma5' in stock_data.columns and 'ma20' in stock_data.columns:
                if latest['close'] > latest['ma5'] > latest['ma20']:
                    signals['trend'] = "多头排列"
                elif latest['close'] < latest['ma5'] < latest['ma20']:
                    signals['trend'] = "空头排列"
                else:
                    signals['trend'] = "震荡趋势"
            
            # RSI信号
            if 'rsi' in stock_data.columns:
                rsi = latest['rsi']
                if rsi > 70:
                    signals['rsi'] = "超买"
                elif rsi < 30:
                    signals['rsi'] = "超卖"
                else:
                    signals['rsi'] = "正常"
            
            # 综合信号
            if overall_score >= 80:
                signals['overall'] = "强烈买入"
            elif overall_score >= 70:
                signals['overall'] = "买入"
            elif overall_score >= 50:
                signals['overall'] = "持有"
            elif overall_score >= 30:
                signals['overall'] = "观望"
            else:
                signals['overall'] = "卖出"
                
        except Exception as e:
            logger.warning(f"生成交易信号失败: {e}")
        
        return signals
    
    def _calculate_technical_indicators(self, stock_data: pd.DataFrame) -> Dict[str, float]:
        """计算技术指标"""
        indicators = {}
        
        if stock_data.empty:
            return indicators
        
        try:
            latest = stock_data.iloc[-1]
            
            # 基本价格信息
            indicators['current_price'] = latest['close']
            indicators['open_price'] = latest['open']
            indicators['high_price'] = latest['high']
            indicators['low_price'] = latest['low']
            
            # 涨跌幅
            if len(stock_data) > 1:
                prev_close = stock_data.iloc[-2]['close']
                indicators['price_change'] = latest['close'] - prev_close
                indicators['price_change_pct'] = (indicators['price_change'] / prev_close) * 100
            
            # 移动平均线
            if 'ma5' in stock_data.columns:
                indicators['ma5'] = latest['ma5']
            if 'ma20' in stock_data.columns:
                indicators['ma20'] = latest['ma20']
            if 'ma60' in stock_data.columns:
                indicators['ma60'] = latest['ma60']
            
            # 技术指标
            if 'rsi' in stock_data.columns:
                indicators['rsi'] = latest['rsi']
            if 'macd' in stock_data.columns:
                indicators['macd'] = latest['macd']
            if 'kdj_k' in stock_data.columns:
                indicators['kdj_k'] = latest['kdj_k']
            if 'kdj_d' in stock_data.columns:
                indicators['kdj_d'] = latest['kdj_d']
            
            # 成交量相关
            if 'volume' in stock_data.columns:
                indicators['volume'] = latest['volume']
                if len(stock_data) >= 20:
                    indicators['volume_ma20'] = stock_data['volume'].tail(20).mean()
                    indicators['volume_ratio'] = latest['volume'] / indicators['volume_ma20']
            
            # 波动率
            if len(stock_data) >= 20:
                returns = stock_data['close'].pct_change().dropna()
                indicators['volatility'] = returns.tail(20).std() * np.sqrt(252) * 100  # 年化波动率
            
        except Exception as e:
            logger.warning(f"计算技术指标失败: {e}")
        
        return indicators
    
    def _predict_price_target(self, stock_data: pd.DataFrame, ml_prediction: Dict) -> Dict[str, float]:
        """预测价格目标"""
        prediction = {}
        
        if stock_data.empty:
            return prediction
        
        try:
            current_price = stock_data['close'].iloc[-1]
            
            # 基于机器学习的预测
            ml_score = ml_prediction.get('probability', 0.5)
            
            # 技术分析预测
            if 'ma20' in stock_data.columns:
                ma20 = stock_data['ma20'].iloc[-1]
                if current_price > ma20:
                    technical_upside = 0.05  # 5% 上涨空间
                else:
                    technical_upside = -0.03  # 3% 下跌风险
            else:
                technical_upside = 0
            
            # 综合预测
            if ml_score > 0.7:
                expected_return = 0.1 + technical_upside  # 10% + 技术面调整
            elif ml_score > 0.6:
                expected_return = 0.05 + technical_upside  # 5% + 技术面调整
            elif ml_score > 0.4:
                expected_return = technical_upside  # 仅技术面调整
            else:
                expected_return = -0.05 + technical_upside  # -5% + 技术面调整
            
            prediction['target_price'] = current_price * (1 + expected_return)
            prediction['upside_potential'] = expected_return * 100
            prediction['stop_loss'] = current_price * 0.9  # 10% 止损
            prediction['confidence'] = abs(ml_score - 0.5) * 2  # 置信度
            
        except Exception as e:
            logger.warning(f"预测价格目标失败: {e}")
        
        return prediction
    
    def _generate_recommendation(self, overall_score: float, risk_assessment: Dict, stock_data: pd.DataFrame) -> Dict[str, any]:
        """生成投资建议"""
        recommendation = {
            'action': '持有',
            'confidence': 50,
            'reason': '中性评价，建议继续观察'
        }
        
        try:
            # 提取评分值
            score_value = overall_score.get('score', 50) if isinstance(overall_score, dict) else overall_score
            risk_level = risk_assessment.get('level', '中等风险')
            
            # 基于综合评分的建议
            if score_value >= 80:
                if risk_level in ['低风险', '中等风险']:
                    recommendation['action'] = '买入'
                    recommendation['confidence'] = min(95, score_value + 10)
                    recommendation['reason'] = f'综合评分{score_value:.1f}分，风险可控，建议买入'
                else:
                    recommendation['action'] = '谨慎买入'
                    recommendation['confidence'] = score_value - 10
                    recommendation['reason'] = f'综合评分{score_value:.1f}分，但风险较高，谨慎买入'
            
            elif score_value >= 70:
                recommendation['action'] = '买入'
                recommendation['confidence'] = score_value
                recommendation['reason'] = f'综合评分{score_value:.1f}分，具备投资价值'
            
            elif score_value >= 60:
                recommendation['action'] = '持有'
                recommendation['confidence'] = score_value
                recommendation['reason'] = f'综合评分{score_value:.1f}分，可适量持有'
            
            elif score_value >= 40:
                recommendation['action'] = '观望'
                recommendation['confidence'] = 100 - score_value
                recommendation['reason'] = f'综合评分{score_value:.1f}分，建议观望等待'
            
            else:
                recommendation['action'] = '卖出'
                recommendation['confidence'] = 100 - score_value
                recommendation['reason'] = f'综合评分{score_value:.1f}分，建议减仓或卖出'
            
            # 风险调整
            if risk_level == '高风险':
                if recommendation['action'] in ['买入', '谨慎买入']:
                    recommendation['confidence'] = max(50, recommendation['confidence'] - 20)
                    recommendation['reason'] += '，但需注意高风险'
            
        except Exception as e:
            logger.warning(f"生成投资建议失败: {e}")
        
        return recommendation