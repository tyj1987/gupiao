import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from loguru import logger
# import talib  # 暂时注释，替换为pandas计算
# from scipy import stats  # 暂时注释
# from sklearn.preprocessing import StandardScaler, MinMaxScaler  # 暂时注释

from config.config import config

class FeatureEngineer:
    """特征工程器"""
    
    def __init__(self):
        """
        初始化特征工程器
        """
        logger.warning("特征工程模块部分功能禁用 - 等待依赖安装")
        self.feature_cache = {}
        self.disabled_talib = True  # 标记talib功能禁用
        logger.info("特征工程器初始化完成")
    
    def create_features(self, 
                       stock_data: pd.DataFrame,
                       financial_data: Dict = None,
                       market_data: Dict = None) -> pd.DataFrame:
        """
        创建机器学习特征
        
        Args:
            stock_data: 股票价格数据
            financial_data: 财务数据
            market_data: 市场数据
            
        Returns:
            特征数据框
        """
        try:
            if stock_data.empty:
                return pd.DataFrame()
            
            # 确保数据按日期排序
            if 'trade_date' in stock_data.columns:
                stock_data = stock_data.sort_values('trade_date')
            elif stock_data.index.name == 'trade_date' or 'date' in str(stock_data.index.name).lower():
                stock_data = stock_data.sort_index()
            
            features = pd.DataFrame(index=stock_data.index)
            
            # 基础价格特征
            features = self._add_price_features(features, stock_data)
            
            # 技术指标特征
            features = self._add_technical_features(features, stock_data)
            
            # 统计特征
            features = self._add_statistical_features(features, stock_data)
            
            # 成交量特征
            features = self._add_volume_features(features, stock_data)
            
            # 趋势特征
            features = self._add_trend_features(features, stock_data)
            
            # 波动率特征
            features = self._add_volatility_features(features, stock_data)
            
            # 相对位置特征
            features = self._add_relative_position_features(features, stock_data)
            
            # 时间特征
            features = self._add_time_features(features, stock_data)
            
            # 财务特征
            if financial_data:
                features = self._add_financial_features(features, financial_data)
            
            # 市场特征
            if market_data:
                features = self._add_market_features(features, market_data, stock_data)
            
            # 交互特征
            features = self._add_interaction_features(features)
            
            # 滞后特征
            features = self._add_lag_features(features, stock_data)
            
            # 清理特征
            features = self._clean_features(features)
            
            logger.debug(f"生成特征数量: {len(features.columns)}")
            return features
            
        except Exception as e:
            logger.error(f"特征工程失败: {e}")
            return pd.DataFrame()
    
    def _add_price_features(self, features: pd.DataFrame, stock_data: pd.DataFrame) -> pd.DataFrame:
        """
        添加价格相关特征
        
        Args:
            features: 特征数据框
            stock_data: 股票数据
            
        Returns:
            更新后的特征数据框
        """
        try:
            # 基础价格
            if 'close' in stock_data.columns:
                features['close'] = stock_data['close']
                features['open'] = stock_data.get('open', stock_data['close'])
                features['high'] = stock_data.get('high', stock_data['close'])
                features['low'] = stock_data.get('low', stock_data['close'])
            
            # 价格变化
            if 'close' in features.columns:
                features['price_change'] = features['close'].pct_change()
                features['price_change_2d'] = features['close'].pct_change(2)
                features['price_change_5d'] = features['close'].pct_change(5)
                features['price_change_10d'] = features['close'].pct_change(10)
                features['price_change_20d'] = features['close'].pct_change(20)
            
            # 价格比率
            if all(col in features.columns for col in ['open', 'high', 'low', 'close']):
                features['hl_ratio'] = (features['high'] - features['low']) / features['close']
                features['oc_ratio'] = (features['close'] - features['open']) / features['open']
                features['ho_ratio'] = (features['high'] - features['open']) / features['open']
                features['lo_ratio'] = (features['low'] - features['open']) / features['open']
            
            # 价格位置
            if all(col in features.columns for col in ['high', 'low', 'close']):
                features['price_position'] = (features['close'] - features['low']) / (features['high'] - features['low'])
                features['price_position'] = features['price_position'].fillna(0.5)
            
            return features
            
        except Exception as e:
            logger.error(f"添加价格特征失败: {e}")
            return features
    
    def _add_technical_features(self, features: pd.DataFrame, stock_data: pd.DataFrame) -> pd.DataFrame:
        """
        添加技术指标特征
        
        Args:
            features: 特征数据框
            stock_data: 股票数据
            
        Returns:
            更新后的特征数据框
        """
        try:
            if 'close' not in stock_data.columns:
                return features
            
            close = stock_data['close'].values
            high = stock_data.get('high', stock_data['close']).values
            low = stock_data.get('low', stock_data['close']).values
            volume = stock_data.get('vol', pd.Series(index=stock_data.index, data=1)).values
            
            # 检查talib是否可用
            # 使用pandas实现技术指标
            logger.debug("使用pandas计算技术指标")
            
            # 移动平均线
            for period in [5, 10, 20, 30, 60]:
                if len(close) >= period:
                    ma = close.rolling(window=period).mean()
                    features[f'ma_{period}'] = ma
                    features[f'ma_{period}_ratio'] = close / ma
            
            # 指数移动平均线
            for period in [12, 26]:
                if len(close) >= period:
                    ema = close.ewm(span=period).mean()
                    features[f'ema_{period}'] = ema
                    features[f'ema_{period}_ratio'] = close / ema
            
            # MACD
            if len(close) >= 34:
                ema12 = close.ewm(span=12).mean()
                ema26 = close.ewm(span=26).mean()
                macd = ema12 - ema26
                macd_signal = macd.ewm(span=9).mean()
                macd_hist = macd - macd_signal
                features['macd'] = macd
                features['macd_signal'] = macd_signal
                features['macd_hist'] = macd_hist
                # 避免除以零
                features['macd_ratio'] = np.where(macd_signal != 0, macd / macd_signal, 0)
            
            # RSI
            for period in [6, 14, 24]:
                if len(close) >= period + 1:
                    delta = close.diff()
                    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
                    loss = (-delta).where(delta < 0, 0).rolling(window=period).mean()
                    rs = gain / loss
                    rsi = 100 - (100 / (1 + rs))
                    features[f'rsi_{period}'] = rsi
                    features[f'rsi_{period}_norm'] = (rsi - 50) / 50
            
            # 布林带
            if len(close) >= 20:
                bb_middle = close.rolling(window=20).mean()
                bb_std = close.rolling(window=20).std()
                bb_upper = bb_middle + (bb_std * 2)
                bb_lower = bb_middle - (bb_std * 2)
                features['bb_upper'] = bb_upper
                features['bb_middle'] = bb_middle
                features['bb_lower'] = bb_lower
                features['bb_width'] = (bb_upper - bb_lower) / bb_middle
                features['bb_position'] = (close - bb_lower) / (bb_upper - bb_lower)
            
            # KDJ (简化版本)
            if len(close) >= 9:
                low_min = low.rolling(window=9).min()
                high_max = high.rolling(window=9).max()
                k = 100 * (close - low_min) / (high_max - low_min)
                d = k.rolling(window=3).mean()
                features['kdj_k'] = k
                features['kdj_d'] = d
                features['kdj_j'] = 3 * k - 2 * d
            
            # CCI
            if len(close) >= 14:
                tp = (high + low + close) / 3
                cci = (tp - tp.rolling(window=14).mean()) / (0.015 * tp.rolling(window=14).std())
                features['cci'] = cci
                features['cci_norm'] = np.tanh(cci / 100)
            
            # Williams %R
            if len(close) >= 14:
                high_max = high.rolling(window=14).max()
                low_min = low.rolling(window=14).min()
                willr = -100 * (high_max - close) / (high_max - low_min)
                features['willr'] = willr
                features['willr_norm'] = (willr + 50) / 50
            
            # ATR
            if len(close) >= 14:
                tr1 = high - low
                tr2 = abs(high - close.shift(1))
                tr3 = abs(low - close.shift(1))
                tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
                atr = tr.rolling(window=14).mean()
                features['atr'] = atr
                features['atr_ratio'] = atr / close
            
            # OBV
            if len(close) >= 1:
                obv = (volume * np.where(close.diff() > 0, 1, np.where(close.diff() < 0, -1, 0))).cumsum()
                features['obv'] = obv
                features['obv_ma'] = obv.rolling(window=10).mean() if len(obv) >= 10 else obv
            
            # ADX (简化版本)
            if len(close) >= 14:
                tr1 = high - low
                tr2 = abs(high - close.shift(1))
                tr3 = abs(low - close.shift(1))
                tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
                atr = tr.rolling(window=14).mean()
                adx = atr / close * 100  # 简化版本
                features['adx'] = adx
            
            # Momentum
            for period in [5, 10, 20]:
                if len(close) >= period:
                    mom = close - close.shift(period)
                    features[f'momentum_{period}'] = mom
                    features[f'momentum_{period}_norm'] = mom / close
            
            # ROC
            for period in [5, 10, 20]:
                if len(close) >= period:
                    roc = (close - close.shift(period)) / close.shift(period) * 100
                    features[f'roc_{period}'] = roc
            
            return features
            
        except Exception as e:
            logger.error(f"添加技术指标特征失败: {e}")
            return features
    
    def _add_statistical_features(self, features: pd.DataFrame, stock_data: pd.DataFrame) -> pd.DataFrame:
        """
        添加统计特征
        
        Args:
            features: 特征数据框
            stock_data: 股票数据
            
        Returns:
            更新后的特征数据框
        """
        try:
            if 'close' not in stock_data.columns:
                return features
            
            close = stock_data['close']
            
            # 滚动统计
            for window in [5, 10, 20, 30]:
                if len(close) >= window:
                    # 均值
                    features[f'mean_{window}'] = close.rolling(window).mean()
                    
                    # 标准差
                    features[f'std_{window}'] = close.rolling(window).std()
                    
                    # 变异系数
                    features[f'cv_{window}'] = features[f'std_{window}'] / features[f'mean_{window}']
                    
                    # 偏度
                    features[f'skew_{window}'] = close.rolling(window).skew()
                    
                    # 峰度
                    features[f'kurt_{window}'] = close.rolling(window).kurt()
                    
                    # 最大值和最小值
                    features[f'max_{window}'] = close.rolling(window).max()
                    features[f'min_{window}'] = close.rolling(window).min()
                    
                    # 当前价格相对于窗口期的位置
                    features[f'rank_{window}'] = close.rolling(window).rank(pct=True)
                    
                    # Z-score
                    features[f'zscore_{window}'] = (close - features[f'mean_{window}']) / features[f'std_{window}']
            
            # 价格变化的统计特征
            if 'price_change' in features.columns:
                price_change = features['price_change']
                
                for window in [5, 10, 20]:
                    if len(price_change) >= window:
                        # 收益率的滚动统计
                        features[f'return_mean_{window}'] = price_change.rolling(window).mean()
                        features[f'return_std_{window}'] = price_change.rolling(window).std()
                        features[f'return_skew_{window}'] = price_change.rolling(window).skew()
                        features[f'return_kurt_{window}'] = price_change.rolling(window).kurt()
                        
                        # 正收益率比例
                        features[f'positive_return_ratio_{window}'] = (price_change > 0).rolling(window).mean()
                        
                        # 连续上涨/下跌天数
                        up_streak = (price_change > 0).astype(int)
                        down_streak = (price_change < 0).astype(int)
                        
                        features[f'up_streak_{window}'] = up_streak.rolling(window).sum()
                        features[f'down_streak_{window}'] = down_streak.rolling(window).sum()
            
            return features
            
        except Exception as e:
            logger.error(f"添加统计特征失败: {e}")
            return features
    
    def _add_volume_features(self, features: pd.DataFrame, stock_data: pd.DataFrame) -> pd.DataFrame:
        """
        添加成交量特征
        
        Args:
            features: 特征数据框
            stock_data: 股票数据
            
        Returns:
            更新后的特征数据框
        """
        try:
            if 'vol' not in stock_data.columns:
                return features
            
            volume = stock_data['vol']
            
            # 基础成交量特征
            features['volume'] = volume
            features['volume_change'] = volume.pct_change()
            
            # 成交量移动平均
            for window in [5, 10, 20, 30]:
                if len(volume) >= window:
                    features[f'volume_ma_{window}'] = volume.rolling(window).mean()
                    features[f'volume_ratio_{window}'] = volume / features[f'volume_ma_{window}']
            
            # 成交量相对强度
            if len(volume) >= 20:
                volume_std = volume.rolling(20).std()
                volume_mean = volume.rolling(20).mean()
                features['volume_rsi'] = (volume - volume_mean) / volume_std
            
            # 价量关系
            if 'price_change' in features.columns:
                price_change = features['price_change']
                
                # 价量相关性
                for window in [5, 10, 20]:
                    if len(price_change) >= window:
                        features[f'price_volume_corr_{window}'] = price_change.rolling(window).corr(volume.pct_change())
                
                # 放量上涨/下跌
                volume_above_avg = volume > volume.rolling(20).mean()
                features['volume_up_trend'] = (price_change > 0) & volume_above_avg
                features['volume_down_trend'] = (price_change < 0) & volume_above_avg
            
            # 成交量分布
            if len(volume) >= 20:
                features['volume_percentile'] = volume.rolling(20).rank(pct=True)
            
            return features
            
        except Exception as e:
            logger.error(f"添加成交量特征失败: {e}")
            return features
    
    def _add_trend_features(self, features: pd.DataFrame, stock_data: pd.DataFrame) -> pd.DataFrame:
        """
        添加趋势特征
        
        Args:
            features: 特征数据框
            stock_data: 股票数据
            
        Returns:
            更新后的特征数据框
        """
        try:
            if 'close' not in stock_data.columns:
                return features
            
            close = stock_data['close']
            
            # 线性回归趋势
            for window in [5, 10, 20, 30]:
                if len(close) >= window:
                    # 计算线性回归斜率 - 使用numpy替代scipy
                    def calc_slope(series):
                        if len(series) < 2:
                            return 0
                        try:
                            x = np.arange(len(series))
                            slope = np.polyfit(x, series, 1)[0]
                            return slope
                        except:
                            return 0
                    
                    features[f'trend_slope_{window}'] = close.rolling(window).apply(calc_slope, raw=False)
                    
                    # 趋势强度（简化计算）
                    def calc_r_squared(series):
                        if len(series) < 2:
                            return 0
                        try:
                            x = np.arange(len(series))
                            coeffs = np.polyfit(x, series, 1)
                            predicted = np.polyval(coeffs, x)
                            ss_res = np.sum((series - predicted) ** 2)
                            ss_tot = np.sum((series - np.mean(series)) ** 2)
                            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
                            return r_squared
                        except:
                            return 0
                    
                    features[f'trend_strength_{window}'] = close.rolling(window).apply(calc_r_squared, raw=False)
            
            # 移动平均趋势
            if 'ma_5' in features.columns and 'ma_20' in features.columns:
                features['ma_trend'] = (features['ma_5'] > features['ma_20']).astype(int)
                features['ma_divergence'] = (features['ma_5'] - features['ma_20']) / features['ma_20']
            
            # 价格相对于移动平均线的位置
            for ma_period in [5, 10, 20, 60]:
                if f'ma_{ma_period}' in features.columns:
                    features[f'price_above_ma_{ma_period}'] = (close > features[f'ma_{ma_period}']).astype(int)
                    features[f'price_distance_ma_{ma_period}'] = (close - features[f'ma_{ma_period}']) / features[f'ma_{ma_period}']
            
            # 突破特征
            if len(close) >= 20:
                # 突破20日高点
                high_20 = close.rolling(20).max()
                features['breakout_high_20'] = (close > high_20.shift(1)).astype(int)
                
                # 跌破20日低点
                low_20 = close.rolling(20).min()
                features['breakdown_low_20'] = (close < low_20.shift(1)).astype(int)
            
            # 趋势持续性
            if 'price_change' in features.columns:
                price_change = features['price_change']
                
                # 连续上涨/下跌天数
                def count_consecutive(series, condition):
                    result = pd.Series(index=series.index, dtype=int)
                    count = 0
                    for i, val in enumerate(series):
                        if condition(val):
                            count += 1
                        else:
                            count = 0
                        result.iloc[i] = count
                    return result
                
                features['consecutive_up'] = count_consecutive(price_change, lambda x: x > 0)
                features['consecutive_down'] = count_consecutive(price_change, lambda x: x < 0)
            
            return features
            
        except Exception as e:
            logger.error(f"添加趋势特征失败: {e}")
            return features
    
    def _add_volatility_features(self, features: pd.DataFrame, stock_data: pd.DataFrame) -> pd.DataFrame:
        """
        添加波动率特征
        
        Args:
            features: 特征数据框
            stock_data: 股票数据
            
        Returns:
            更新后的特征数据框
        """
        try:
            if 'close' not in stock_data.columns:
                return features
            
            close = stock_data['close']
            high = stock_data.get('high', close)
            low = stock_data.get('low', close)
            
            # 收益率波动率
            if 'price_change' in features.columns:
                returns = features['price_change']
                
                for window in [5, 10, 20, 30]:
                    if len(returns) >= window:
                        features[f'volatility_{window}'] = returns.rolling(window).std()
                        features[f'volatility_{window}_annualized'] = features[f'volatility_{window}'] * np.sqrt(252)
            
            # True Range和ATR
            if all(col in stock_data.columns for col in ['high', 'low', 'close']):
                # True Range
                tr1 = high - low
                tr2 = np.abs(high - close.shift(1))
                tr3 = np.abs(low - close.shift(1))
                true_range = np.maximum(tr1, np.maximum(tr2, tr3))
                features['true_range'] = true_range
                
                # ATR
                for window in [14, 20]:
                    if len(true_range) >= window:
                        features[f'atr_{window}'] = true_range.rolling(window).mean()
                        features[f'atr_ratio_{window}'] = features[f'atr_{window}'] / close
            
            # Garman-Klass波动率估计
            if all(col in stock_data.columns for col in ['open', 'high', 'low', 'close']):
                open_price = stock_data['open']
                
                # Garman-Klass估计器
                gk_vol = 0.5 * np.log(high / low) ** 2 - (2 * np.log(2) - 1) * np.log(close / open_price) ** 2
                features['gk_volatility'] = gk_vol
                
                for window in [5, 10, 20]:
                    if len(gk_vol) >= window:
                        features[f'gk_volatility_{window}'] = gk_vol.rolling(window).mean()
            
            # 波动率聚类
            if 'volatility_20' in features.columns:
                vol_20 = features['volatility_20']
                features['volatility_regime'] = (vol_20 > vol_20.rolling(60).quantile(0.7)).astype(int)
            
            # 相对波动率
            for short_window, long_window in [(5, 20), (10, 30)]:
                if f'volatility_{short_window}' in features.columns and f'volatility_{long_window}' in features.columns:
                    features[f'relative_volatility_{short_window}_{long_window}'] = (
                        features[f'volatility_{short_window}'] / features[f'volatility_{long_window}']
                    )
            
            return features
            
        except Exception as e:
            logger.error(f"添加波动率特征失败: {e}")
            return features
    
    def _add_relative_position_features(self, features: pd.DataFrame, stock_data: pd.DataFrame) -> pd.DataFrame:
        """
        添加相对位置特征
        
        Args:
            features: 特征数据框
            stock_data: 股票数据
            
        Returns:
            更新后的特征数据框
        """
        try:
            if 'close' not in stock_data.columns:
                return features
            
            close = stock_data['close']
            
            # 相对于历史高低点的位置
            for window in [20, 60, 120, 252]:
                if len(close) >= window:
                    rolling_max = close.rolling(window).max()
                    rolling_min = close.rolling(window).min()
                    
                    # 相对位置 (0-1)
                    features[f'relative_position_{window}'] = (
                        (close - rolling_min) / (rolling_max - rolling_min)
                    ).fillna(0.5)
                    
                    # 距离高点的百分比
                    features[f'distance_from_high_{window}'] = (rolling_max - close) / rolling_max
                    
                    # 距离低点的百分比
                    features[f'distance_from_low_{window}'] = (close - rolling_min) / rolling_min
            
            # 分位数排名
            for window in [20, 60, 120]:
                if len(close) >= window:
                    features[f'percentile_rank_{window}'] = close.rolling(window).rank(pct=True)
            
            return features
            
        except Exception as e:
            logger.error(f"添加相对位置特征失败: {e}")
            return features
    
    def _add_time_features(self, features: pd.DataFrame, stock_data: pd.DataFrame) -> pd.DataFrame:
        """
        添加时间特征
        
        Args:
            features: 特征数据框
            stock_data: 股票数据
            
        Returns:
            更新后的特征数据框
        """
        try:
            # 获取日期索引
            if 'trade_date' in stock_data.columns:
                dates = pd.to_datetime(stock_data['trade_date'])
            elif stock_data.index.name == 'trade_date' or 'date' in str(stock_data.index.name).lower():
                dates = pd.to_datetime(stock_data.index)
            else:
                return features
            
            # 星期几
            features['day_of_week'] = dates.dt.dayofweek
            features['is_monday'] = (dates.dt.dayofweek == 0).astype(int)
            features['is_friday'] = (dates.dt.dayofweek == 4).astype(int)
            
            # 月份
            features['month'] = dates.dt.month
            features['quarter'] = dates.dt.quarter
            
            # 是否月初/月末
            features['is_month_start'] = dates.dt.is_month_start.astype(int)
            features['is_month_end'] = dates.dt.is_month_end.astype(int)
            
            # 是否季度开始/结束
            features['is_quarter_start'] = dates.dt.is_quarter_start.astype(int)
            features['is_quarter_end'] = dates.dt.is_quarter_end.astype(int)
            
            # 是否年初/年末
            features['is_year_start'] = dates.dt.is_year_start.astype(int)
            features['is_year_end'] = dates.dt.is_year_end.astype(int)
            
            # 距离年初的天数
            year_start = dates - pd.to_datetime(dates.dt.year.astype(str) + '-01-01')
            features['days_from_year_start'] = year_start.dt.days
            
            return features
            
        except Exception as e:
            logger.error(f"添加时间特征失败: {e}")
            return features
    
    def _add_financial_features(self, features: pd.DataFrame, financial_data: Dict) -> pd.DataFrame:
        """
        添加财务特征
        
        Args:
            features: 特征数据框
            financial_data: 财务数据
            
        Returns:
            更新后的特征数据框
        """
        try:
            if not financial_data or 'indicators' not in financial_data:
                return features
            
            indicators = financial_data['indicators']
            if indicators.empty:
                return features
            
            # 使用最新的财务数据
            latest_indicators = indicators.iloc[0]
            
            # 估值指标
            for metric in ['pe', 'pb', 'ps', 'pcf']:
                if metric in latest_indicators:
                    features[f'financial_{metric}'] = latest_indicators[metric]
            
            # 盈利能力指标
            for metric in ['roe', 'roa', 'gross_margin', 'netprofit_margin']:
                if metric in latest_indicators:
                    features[f'financial_{metric}'] = latest_indicators[metric]
            
            # 财务健康指标
            for metric in ['debt_to_assets', 'current_ratio', 'quick_ratio']:
                if metric in latest_indicators:
                    features[f'financial_{metric}'] = latest_indicators[metric]
            
            # 成长性指标
            for metric in ['revenue_yoy', 'profit_yoy']:
                if metric in latest_indicators:
                    features[f'financial_{metric}'] = latest_indicators[metric]
            
            # 财务评分
            financial_score = 0
            score_count = 0
            
            # ROE评分
            if 'roe' in latest_indicators and pd.notna(latest_indicators['roe']):
                roe = latest_indicators['roe']
                if roe > 15:
                    financial_score += 2
                elif roe > 10:
                    financial_score += 1
                elif roe < 5:
                    financial_score -= 1
                score_count += 1
            
            # PE评分
            if 'pe' in latest_indicators and pd.notna(latest_indicators['pe']):
                pe = latest_indicators['pe']
                if 0 < pe < 15:
                    financial_score += 1
                elif pe > 50:
                    financial_score -= 1
                score_count += 1
            
            # 负债率评分
            if 'debt_to_assets' in latest_indicators and pd.notna(latest_indicators['debt_to_assets']):
                debt_ratio = latest_indicators['debt_to_assets']
                if debt_ratio < 30:
                    financial_score += 1
                elif debt_ratio > 70:
                    financial_score -= 1
                score_count += 1
            
            if score_count > 0:
                features['financial_score'] = financial_score / score_count
            else:
                features['financial_score'] = 0
            
            return features
            
        except Exception as e:
            logger.error(f"添加财务特征失败: {e}")
            return features
    
    def _add_market_features(self, features: pd.DataFrame, market_data: Dict, stock_data: pd.DataFrame) -> pd.DataFrame:
        """
        添加市场特征
        
        Args:
            features: 特征数据框
            market_data: 市场数据
            stock_data: 股票数据
            
        Returns:
            更新后的特征数据框
        """
        try:
            if not market_data or 'close' not in stock_data.columns:
                return features
            
            stock_returns = stock_data['close'].pct_change()
            
            # 相对于市场指数的表现
            for index_name, index_data in market_data.items():
                if index_data.empty or 'close' not in index_data.columns:
                    continue
                
                index_returns = index_data['close'].pct_change()
                
                # 对齐数据
                common_index = stock_returns.index.intersection(index_returns.index)
                if len(common_index) < 10:
                    continue
                
                stock_aligned = stock_returns.loc[common_index]
                index_aligned = index_returns.loc[common_index]
                
                # Beta系数
                for window in [20, 60, 120]:
                    if len(common_index) >= window:
                        rolling_cov = stock_aligned.rolling(window).cov(index_aligned)
                        rolling_var = index_aligned.rolling(window).var()
                        beta = rolling_cov / rolling_var
                        features[f'beta_{index_name}_{window}'] = beta.reindex(features.index)
                
                # 相对强度
                relative_strength = stock_aligned - index_aligned
                for window in [5, 10, 20]:
                    if len(relative_strength) >= window:
                        rs_ma = relative_strength.rolling(window).mean()
                        features[f'relative_strength_{index_name}_{window}'] = rs_ma.reindex(features.index)
                
                # 相关系数
                for window in [20, 60]:
                    if len(common_index) >= window:
                        correlation = stock_aligned.rolling(window).corr(index_aligned)
                        features[f'correlation_{index_name}_{window}'] = correlation.reindex(features.index)
            
            return features
            
        except Exception as e:
            logger.error(f"添加市场特征失败: {e}")
            return features
    
    def _add_interaction_features(self, features: pd.DataFrame) -> pd.DataFrame:
        """
        添加交互特征
        
        Args:
            features: 特征数据框
            
        Returns:
            更新后的特征数据框
        """
        try:
            # 价格和成交量的交互
            if 'price_change' in features.columns and 'volume_change' in features.columns:
                features['price_volume_interaction'] = features['price_change'] * features['volume_change']
            
            # RSI和价格位置的交互
            if 'rsi_14' in features.columns and 'relative_position_20' in features.columns:
                features['rsi_position_interaction'] = features['rsi_14'] * features['relative_position_20']
            
            # MACD和趋势的交互
            if 'macd' in features.columns and 'trend_slope_20' in features.columns:
                features['macd_trend_interaction'] = features['macd'] * features['trend_slope_20']
            
            # 波动率和成交量的交互
            if 'volatility_20' in features.columns and 'volume_ratio_20' in features.columns:
                features['volatility_volume_interaction'] = features['volatility_20'] * features['volume_ratio_20']
            
            return features
            
        except Exception as e:
            logger.error(f"添加交互特征失败: {e}")
            return features
    
    def _add_lag_features(self, features: pd.DataFrame, stock_data: pd.DataFrame) -> pd.DataFrame:
        """
        添加滞后特征
        
        Args:
            features: 特征数据框
            stock_data: 股票数据
            
        Returns:
            更新后的特征数据框
        """
        try:
            # 重要特征的滞后版本
            lag_features = ['price_change', 'volume_change', 'rsi_14', 'macd']
            
            for feature in lag_features:
                if feature in features.columns:
                    for lag in [1, 2, 3, 5]:
                        features[f'{feature}_lag_{lag}'] = features[feature].shift(lag)
            
            # 移动平均的滞后
            ma_features = [col for col in features.columns if col.startswith('ma_')]
            for feature in ma_features[:3]:  # 限制数量
                for lag in [1, 2]:
                    features[f'{feature}_lag_{lag}'] = features[feature].shift(lag)
            
            return features
            
        except Exception as e:
            logger.error(f"添加滞后特征失败: {e}")
            return features
    
    def _clean_features(self, features: pd.DataFrame) -> pd.DataFrame:
        """
        清理特征数据
        
        Args:
            features: 特征数据框
            
        Returns:
            清理后的特征数据框
        """
        try:
            # 移除无穷大值
            features = features.replace([np.inf, -np.inf], np.nan)
            
            # 移除全为NaN的列
            features = features.dropna(axis=1, how='all')
            
            # 移除常数列
            constant_cols = features.columns[features.nunique() <= 1]
            if len(constant_cols) > 0:
                features = features.drop(columns=constant_cols)
                logger.debug(f"移除常数列: {list(constant_cols)}")
            
            # 填充缺失值
            features = features.fillna(method='ffill').fillna(0)
            
            return features
            
        except Exception as e:
            logger.error(f"清理特征失败: {e}")
            return features
    
    def get_feature_importance_ranking(self, features: pd.DataFrame, target: pd.Series) -> Dict[str, float]:
        """
        获取特征重要性排名
        
        Args:
            features: 特征数据
            target: 目标变量
            
        Returns:
            特征重要性字典
        """
        try:
            from sklearn.feature_selection import mutual_info_regression
            from sklearn.ensemble import RandomForestRegressor
            
            # 清理数据
            features_clean = self._clean_features(features)
            
            # 对齐索引
            common_index = features_clean.index.intersection(target.index)
            if len(common_index) < 10:
                return {}
            
            X = features_clean.loc[common_index]
            y = target.loc[common_index].dropna()
            
            # 再次对齐
            common_index = X.index.intersection(y.index)
            X = X.loc[common_index]
            y = y.loc[common_index]
            
            if X.empty or len(y) < 10:
                return {}
            
            # 使用随机森林计算特征重要性
            rf = RandomForestRegressor(n_estimators=50, random_state=42)
            rf.fit(X, y)
            
            importance_dict = dict(zip(X.columns, rf.feature_importances_))
            
            # 按重要性排序
            sorted_importance = dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
            
            return sorted_importance
            
        except Exception as e:
            logger.error(f"计算特征重要性失败: {e}")
            return {}
    
    def _calculate_indicators_pandas(self, stock_data: pd.DataFrame, features: pd.DataFrame) -> pd.DataFrame:
        """
        使用pandas计算技术指标替代talib
        """
        try:
            close = stock_data['close']
            high = stock_data.get('high', stock_data['close'])
            low = stock_data.get('low', stock_data['close'])
            volume = stock_data.get('vol', pd.Series(index=stock_data.index, data=1))
            
            # 移动平均线
            for period in [5, 10, 20, 30, 60]:
                if len(close) >= period:
                    ma = close.rolling(window=period, min_periods=1).mean()
                    features[f'ma_{period}'] = ma
                    features[f'ma_{period}_ratio'] = close / ma
            
            # 指数移动平均线
            for period in [12, 26]:
                if len(close) >= period:
                    ema = close.ewm(span=period).mean()
                    features[f'ema_{period}'] = ema
                    features[f'ema_{period}_ratio'] = close / ema
            
            # MACD
            if len(close) >= 26:
                ema12 = close.ewm(span=12).mean()
                ema26 = close.ewm(span=26).mean()
                macd = ema12 - ema26
                macd_signal = macd.ewm(span=9).mean()
                macd_hist = macd - macd_signal
                features['macd'] = macd
                features['macd_signal'] = macd_signal
                features['macd_hist'] = macd_hist
            
            # RSI
            for period in [6, 14, 24]:
                if len(close) >= period:
                    delta = close.diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
                    rs = gain / loss
                    rsi = 100 - (100 / (1 + rs))
                    features[f'rsi_{period}'] = rsi
            
            # 布林带
            if len(close) >= 20:
                ma20 = close.rolling(window=20).mean()
                std20 = close.rolling(window=20).std()
                bb_upper = ma20 + (std20 * 2)
                bb_lower = ma20 - (std20 * 2)
                features['bb_upper'] = bb_upper
                features['bb_middle'] = ma20
                features['bb_lower'] = bb_lower
                features['bb_width'] = (bb_upper - bb_lower) / ma20
                features['bb_position'] = (close - bb_lower) / (bb_upper - bb_lower)
            
            # 威廉指标
            if len(close) >= 14:
                high_max = high.rolling(window=14).max()
                low_min = low.rolling(window=14).min()
                willr = (high_max - close) / (high_max - low_min) * -100
                features['willr'] = willr
            
            # ATR
            if len(close) >= 14:
                high_low = high - low
                high_close_prev = abs(high - close.shift(1))
                low_close_prev = abs(low - close.shift(1))
                tr = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
                atr = tr.rolling(window=14).mean()
                features['atr'] = atr
            
            # 成交量指标
            if len(volume) >= 10:
                vol_ma = volume.rolling(window=10).mean()
                features['vol_ma'] = vol_ma
                features['vol_ratio'] = volume / vol_ma
            
            logger.debug("pandas技术指标计算完成")
            return features
            
        except Exception as e:
            logger.error(f"pandas技术指标计算失败: {e}")
            return features