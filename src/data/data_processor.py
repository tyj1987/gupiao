import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from loguru import logger

# 使用pandas-ta替代talib
try:
    import pandas_ta as ta
    PANDAS_TA_AVAILABLE = True
    logger.info("pandas-ta加载成功")
except ImportError:
    PANDAS_TA_AVAILABLE = False
    logger.warning("pandas-ta不可用，将使用简化的技术指标计算")

# 保持talib导入的尝试（如果未来安装成功）
try:
    import talib
    TALIB_AVAILABLE = True
    logger.info("TA-Lib加载成功")
except ImportError:
    TALIB_AVAILABLE = False
    logger.info("TA-Lib不可用，使用pandas-ta替代")

class DataProcessor:
    """数据处理器"""
    
    def __init__(self):
        """
        初始化数据处理器
        """
        logger.info("数据处理器初始化成功")
    
    def standardize_data_source(self, df: pd.DataFrame, source: str = 'unknown') -> pd.DataFrame:
        """
        标准化不同数据源的数据格式，减少差异
        
        Args:
            df: 原始数据DataFrame
            source: 数据源标识 ('tushare', 'akshare', 'yfinance')
            
        Returns:
            标准化后的DataFrame
        """
        if df.empty:
            return df
            
        try:
            standardized_df = df.copy()
            
            # 标准化日期列
            if 'trade_date' in standardized_df.columns:
                standardized_df.index = pd.to_datetime(standardized_df['trade_date'])
            elif 'date' in standardized_df.columns:
                standardized_df.index = pd.to_datetime(standardized_df['date'])
            
            # 确保索引是datetime类型
            if not isinstance(standardized_df.index, pd.DatetimeIndex):
                if standardized_df.index.name in ['trade_date', 'date']:
                    standardized_df.index = pd.to_datetime(standardized_df.index)
            
            # 标准化数值精度
            numeric_columns = ['open', 'high', 'low', 'close', 'pre_close']
            for col in numeric_columns:
                if col in standardized_df.columns:
                    standardized_df[col] = pd.to_numeric(standardized_df[col], errors='coerce').round(2)
            
            # 标准化成交量单位 (统一为手)
            vol_columns = ['vol', 'volume']
            for col in vol_columns:
                if col in standardized_df.columns:
                    # Tushare的成交量单位是万手，转换为手
                    if source.lower() == 'tushare' and col == 'vol':
                        standardized_df[col] = standardized_df[col] * 10000
                    standardized_df[col] = pd.to_numeric(standardized_df[col], errors='coerce').astype('Int64')
            
            # 标准化涨跌幅精度
            if 'pct_chg' in standardized_df.columns:
                standardized_df['pct_chg'] = pd.to_numeric(standardized_df['pct_chg'], errors='coerce').round(2)
            
            # 添加数据源标记
            standardized_df['data_source'] = source
            
            logger.debug(f"数据源{source}标准化完成，共{len(standardized_df)}条记录")
            return standardized_df
            
        except Exception as e:
            logger.warning(f"数据源标准化失败: {e}")
            return df
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        清洗数据
        
        Args:
            df: 原始数据DataFrame
            
        Returns:
            清洗后的DataFrame
        """
        if df.empty:
            return df
        
        try:
            # 复制数据避免修改原始数据
            cleaned_df = df.copy()
            
            # 删除重复行
            cleaned_df = cleaned_df.drop_duplicates()
            
            # 处理缺失值
            numeric_columns = cleaned_df.select_dtypes(include=[np.number]).columns
            
            # 对于价格相关字段，使用前向填充
            price_columns = ['open', 'high', 'low', 'close', 'pre_close', 'price']
            for col in price_columns:
                if col in cleaned_df.columns:
                    cleaned_df[col] = cleaned_df[col].fillna(method='ffill')
            
            # 对于成交量，使用0填充
            volume_columns = ['vol', 'volume', 'amount']
            for col in volume_columns:
                if col in cleaned_df.columns:
                    cleaned_df[col] = cleaned_df[col].fillna(0)
            
            # 处理异常值
            for col in numeric_columns:
                if col in cleaned_df.columns:
                    # 使用IQR方法检测异常值
                    Q1 = cleaned_df[col].quantile(0.25)
                    Q3 = cleaned_df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    
                    # 定义异常值边界
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    # 对于价格字段，不处理上边界异常值（可能是正常的价格上涨）
                    if col in price_columns:
                        cleaned_df.loc[cleaned_df[col] < lower_bound, col] = np.nan
                    else:
                        cleaned_df.loc[(cleaned_df[col] < lower_bound) | 
                                     (cleaned_df[col] > upper_bound), col] = np.nan
            
            # 再次填充处理后的缺失值
            cleaned_df = cleaned_df.fillna(method='ffill').fillna(method='bfill')
            
            # 确保日期列格式正确
            date_columns = ['trade_date', 'date', 'publish_time', 'update_time']
            for col in date_columns:
                if col in cleaned_df.columns:
                    cleaned_df[col] = pd.to_datetime(cleaned_df[col], errors='coerce')
            
            # 按日期排序
            if 'trade_date' in cleaned_df.columns:
                cleaned_df = cleaned_df.sort_values('trade_date').reset_index(drop=True)
            
            logger.info(f"数据清洗完成，处理了{len(df) - len(cleaned_df)}行重复数据")
            return cleaned_df
            
        except Exception as e:
            logger.error(f"数据清洗失败: {e}")
            return df
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        计算技术指标
        
        Args:
            df: 包含OHLCV数据的DataFrame
            
        Returns:
            包含技术指标的DataFrame
        """
        if df.empty or len(df) < 20:
            return df
        
        try:
            result_df = df.copy()
            
            # 确保有必要的列
            required_columns = ['open', 'high', 'low', 'close']
            vol_column = 'vol' if 'vol' in df.columns else 'volume'
            required_columns.append(vol_column)
            
            if not all(col in df.columns for col in required_columns):
                logger.warning("缺少必要的OHLCV列，跳过技术指标计算")
                return df
            
            # 标准化volume列名
            if vol_column == 'vol' and 'volume' not in result_df.columns:
                result_df['volume'] = result_df['vol']
            
            # 使用pandas-ta计算技术指标
            if PANDAS_TA_AVAILABLE:
                logger.debug("使用pandas-ta计算技术指标")
                
                # 重命名列以符合pandas-ta标准
                ta_df = result_df.copy()
                if vol_column != 'volume' and 'volume' not in ta_df.columns:
                    ta_df['volume'] = ta_df[vol_column]
                
                # 移动平均线
                ta_df['ma5'] = ta.sma(ta_df['close'], length=5)
                ta_df['ma10'] = ta.sma(ta_df['close'], length=10)
                ta_df['ma20'] = ta.sma(ta_df['close'], length=20)
                ta_df['ma60'] = ta.sma(ta_df['close'], length=60)
                
                # 指数移动平均线
                ta_df['ema12'] = ta.ema(ta_df['close'], length=12)
                ta_df['ema26'] = ta.ema(ta_df['close'], length=26)
                
                # MACD
                macd_data = ta.macd(ta_df['close'])
                if macd_data is not None and not macd_data.empty:
                    ta_df = ta_df.join(macd_data, rsuffix='_macd')
                    if 'MACD_12_26_9' in macd_data.columns:
                        ta_df['macd'] = macd_data['MACD_12_26_9']
                    if 'MACDs_12_26_9' in macd_data.columns:
                        ta_df['macd_signal'] = macd_data['MACDs_12_26_9']
                    if 'MACDh_12_26_9' in macd_data.columns:
                        ta_df['macd_hist'] = macd_data['MACDh_12_26_9']
                
                # RSI
                ta_df['rsi6'] = ta.rsi(ta_df['close'], length=6)
                ta_df['rsi12'] = ta.rsi(ta_df['close'], length=12)
                ta_df['rsi24'] = ta.rsi(ta_df['close'], length=24)
                
                # 布林带
                bb_data = ta.bbands(ta_df['close'], length=20)
                if bb_data is not None and not bb_data.empty:
                    ta_df = ta_df.join(bb_data, rsuffix='_bb')
                    if 'BBU_20_2.0' in bb_data.columns:
                        ta_df['bb_upper'] = bb_data['BBU_20_2.0']
                    if 'BBM_20_2.0' in bb_data.columns:
                        ta_df['bb_middle'] = bb_data['BBM_20_2.0']
                    if 'BBL_20_2.0' in bb_data.columns:
                        ta_df['bb_lower'] = bb_data['BBL_20_2.0']
                    if 'BBB_20_2.0' in bb_data.columns:
                        ta_df['bb_width'] = bb_data['BBB_20_2.0']
                    if 'BBP_20_2.0' in bb_data.columns:
                        ta_df['bb_position'] = bb_data['BBP_20_2.0']
                
                # KDJ (Stoch)
                stoch_data = ta.stoch(ta_df['high'], ta_df['low'], ta_df['close'])
                if stoch_data is not None and not stoch_data.empty:
                    ta_df = ta_df.join(stoch_data, rsuffix='_stoch')
                    if 'STOCHk_14_3_3' in stoch_data.columns:
                        ta_df['kdj_k'] = stoch_data['STOCHk_14_3_3']
                    if 'STOCHd_14_3_3' in stoch_data.columns:
                        ta_df['kdj_d'] = stoch_data['STOCHd_14_3_3']
                    # J线计算
                    if 'kdj_k' in ta_df.columns and 'kdj_d' in ta_df.columns:
                        ta_df['kdj_j'] = 3 * ta_df['kdj_k'] - 2 * ta_df['kdj_d']
                
                # CCI
                ta_df['cci'] = ta.cci(ta_df['high'], ta_df['low'], ta_df['close'])
                
                # Williams %R
                ta_df['wr10'] = ta.willr(ta_df['high'], ta_df['low'], ta_df['close'], length=10)
                ta_df['wr6'] = ta.willr(ta_df['high'], ta_df['low'], ta_df['close'], length=6)
                
                # ATR
                ta_df['atr'] = ta.atr(ta_df['high'], ta_df['low'], ta_df['close'])
                
                # OBV
                ta_df['obv'] = ta.obv(ta_df['close'], ta_df['volume'])
                
                # ROC
                ta_df['roc'] = ta.roc(ta_df['close'], length=10)
                
                # 成交量指标
                ta_df['vol_ma5'] = ta.sma(ta_df['volume'], length=5)
                ta_df['vol_ma10'] = ta.sma(ta_df['volume'], length=10)
                
                result_df = ta_df
                
            # 如果pandas-ta不可用，使用原生talib（如果可用）
            elif TALIB_AVAILABLE:
                logger.debug("使用TA-Lib计算技术指标")
                
                # 转换为numpy数组
                open_prices = df['open'].values.astype(float)
                high_prices = df['high'].values.astype(float)
                low_prices = df['low'].values.astype(float)
                close_prices = df['close'].values.astype(float)
                volumes = df[vol_column].values.astype(float)
                
                # 移动平均线
                result_df['ma5'] = talib.SMA(close_prices, timeperiod=5)
                result_df['ma10'] = talib.SMA(close_prices, timeperiod=10)
                result_df['ma20'] = talib.SMA(close_prices, timeperiod=20)
                result_df['ma60'] = talib.SMA(close_prices, timeperiod=60)
                
                # 指数移动平均线
                result_df['ema12'] = talib.EMA(close_prices, timeperiod=12)
                result_df['ema26'] = talib.EMA(close_prices, timeperiod=26)
                
                # MACD
                macd, macd_signal, macd_hist = talib.MACD(close_prices)
                result_df['macd'] = macd
                result_df['macd_signal'] = macd_signal
                result_df['macd_hist'] = macd_hist
                
                # RSI
                result_df['rsi6'] = talib.RSI(close_prices, timeperiod=6)
                result_df['rsi12'] = talib.RSI(close_prices, timeperiod=12)
                result_df['rsi24'] = talib.RSI(close_prices, timeperiod=24)
                
                # 布林带
                bb_upper, bb_middle, bb_lower = talib.BBANDS(close_prices, timeperiod=20)
                result_df['bb_upper'] = bb_upper
                result_df['bb_middle'] = bb_middle
                result_df['bb_lower'] = bb_lower
                result_df['bb_width'] = (bb_upper - bb_lower) / bb_middle
                result_df['bb_position'] = (close_prices - bb_lower) / (bb_upper - bb_lower)
                
                # KDJ (Stoch)
                k, d = talib.STOCH(high_prices, low_prices, close_prices)
                result_df['kdj_k'] = k
                result_df['kdj_d'] = d
                result_df['kdj_j'] = 3 * k - 2 * d
                
                # CCI
                result_df['cci'] = talib.CCI(high_prices, low_prices, close_prices)
                
                # Williams %R
                result_df['wr10'] = talib.WILLR(high_prices, low_prices, close_prices, timeperiod=10)
                result_df['wr6'] = talib.WILLR(high_prices, low_prices, close_prices, timeperiod=6)
                
                # ATR
                result_df['atr'] = talib.ATR(high_prices, low_prices, close_prices)
                
                # OBV
                result_df['obv'] = talib.OBV(close_prices, volumes)
                
                # ROC
                result_df['roc'] = talib.ROC(close_prices, timeperiod=10)
                
                # 成交量指标
                result_df['vol_ma5'] = talib.SMA(volumes, timeperiod=5)
                result_df['vol_ma10'] = talib.SMA(volumes, timeperiod=10)
                
            else:
                # 回退到简化计算（原来的方法）
                logger.debug("使用简化方法计算技术指标")
                result_df = self._calculate_simple_indicators(result_df, vol_column)
            
            # 计算一些额外的指标
            if vol_column in result_df.columns:
                # 成交量比率
                if 'vol_ma5' in result_df.columns:
                    result_df['vol_ratio'] = result_df[vol_column] / result_df['vol_ma5']
                
                # 动量指标
                result_df['momentum'] = result_df['close'] - result_df['close'].shift(10)
                
                # 乖离率
                if 'ma5' in result_df.columns:
                    result_df['bias5'] = (result_df['close'] - result_df['ma5']) / result_df['ma5'] * 100
                if 'ma10' in result_df.columns:
                    result_df['bias10'] = (result_df['close'] - result_df['ma10']) / result_df['ma10'] * 100
                if 'ma20' in result_df.columns:
                    result_df['bias20'] = (result_df['close'] - result_df['ma20']) / result_df['ma20'] * 100
                
                # 涨跌幅
                result_df['pct_change'] = result_df['close'].pct_change() * 100
            
            logger.debug(f"技术指标计算完成，新增{len(result_df.columns) - len(df.columns)}个指标")
            return result_df
            
        except Exception as e:
            logger.error(f"计算技术指标失败: {e}")
            return df
    
    def _calculate_simple_indicators(self, df: pd.DataFrame, vol_column: str) -> pd.DataFrame:
        """
        使用简化方法计算技术指标（回退方案）
        
        Args:
            df: 输入数据
            vol_column: 成交量列名
            
        Returns:
            包含技术指标的DataFrame
        """
        try:
            # 移动平均线
            df['ma5'] = df['close'].rolling(window=5, min_periods=1).mean()
            df['ma10'] = df['close'].rolling(window=10, min_periods=1).mean()
            df['ma20'] = df['close'].rolling(window=20, min_periods=1).mean()
            df['ma60'] = df['close'].rolling(window=60, min_periods=1).mean()
            
            # 指数移动平均线
            df['ema12'] = df['close'].ewm(span=12).mean()
            df['ema26'] = df['close'].ewm(span=26).mean()
            
            # MACD
            ema12 = df['close'].ewm(span=12).mean()
            ema26 = df['close'].ewm(span=26).mean()
            macd = ema12 - ema26
            macd_signal = macd.ewm(span=9).mean()
            macd_hist = macd - macd_signal
            df['macd'] = macd
            df['macd_signal'] = macd_signal
            df['macd_hist'] = macd_hist
            
            # RSI (简化计算)
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=6).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=6).mean()
            rs = gain / loss
            df['rsi6'] = 100 - (100 / (1 + rs))
            
            gain = (delta.where(delta > 0, 0)).rolling(window=12).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=12).mean()
            rs = gain / loss
            df['rsi12'] = 100 - (100 / (1 + rs))
            
            gain = (delta.where(delta > 0, 0)).rolling(window=24).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=24).mean()
            rs = gain / loss
            df['rsi24'] = 100 - (100 / (1 + rs))
            
            # 布林带
            ma20 = df['close'].rolling(window=20).mean()
            std20 = df['close'].rolling(window=20).std()
            bb_upper = ma20 + (std20 * 2)
            bb_middle = ma20
            bb_lower = ma20 - (std20 * 2)
            df['bb_upper'] = bb_upper
            df['bb_middle'] = bb_middle
            df['bb_lower'] = bb_lower
            df['bb_width'] = (bb_upper - bb_lower) / bb_middle
            df['bb_position'] = (df['close'] - bb_lower) / (bb_upper - bb_lower)
            
            # KDJ指标 (简化计算)
            low_min = df['low'].rolling(window=9).min()
            high_max = df['high'].rolling(window=9).max()
            rsv = (df['close'] - low_min) / (high_max - low_min) * 100
            k = rsv.ewm(alpha=1/3).mean()
            d = k.ewm(alpha=1/3).mean()
            df['kdj_k'] = k
            df['kdj_d'] = d
            df['kdj_j'] = 3 * k - 2 * d
            
            # CCI指标 (简化计算)
            tp = (df['high'] + df['low'] + df['close']) / 3
            ma_tp = tp.rolling(window=14).mean()
            md = tp.rolling(window=14).apply(lambda x: abs(x - x.mean()).mean())
            df['cci'] = (tp - ma_tp) / (0.015 * md)
            
            # 威廉指标
            high_max_10 = df['high'].rolling(window=10).max()
            low_min_10 = df['low'].rolling(window=10).min()
            df['wr10'] = (high_max_10 - df['close']) / (high_max_10 - low_min_10) * -100
            
            high_max_6 = df['high'].rolling(window=6).max()
            low_min_6 = df['low'].rolling(window=6).min()
            df['wr6'] = (high_max_6 - df['close']) / (high_max_6 - low_min_6) * -100
            
            # 成交量指标
            df['vol_ma5'] = df[vol_column].rolling(window=5, min_periods=1).mean()
            df['vol_ma10'] = df[vol_column].rolling(window=10, min_periods=1).mean()
            
            # OBV指标 (简化计算)
            obv = []
            obv_value = 0
            for i in range(len(df)):
                if i == 0:
                    obv_value = df[vol_column].iloc[i]
                else:
                    if df['close'].iloc[i] > df['close'].iloc[i-1]:
                        obv_value += df[vol_column].iloc[i]
                    elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                        obv_value -= df[vol_column].iloc[i]
                obv.append(obv_value)
            df['obv'] = obv
            
            # ATR指标 (简化计算)
            high_low = df['high'] - df['low']
            high_close_prev = abs(df['high'] - df['close'].shift(1))
            low_close_prev = abs(df['low'] - df['close'].shift(1))
            tr = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
            df['atr'] = tr.rolling(window=14).mean()
            
            # 价格变化率
            df['roc'] = df['close'].pct_change(periods=10) * 100
            
            return df
            
        except Exception as e:
            logger.error(f"简化技术指标计算失败: {e}")
            return df
    
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        创建特征工程数据
        
        Args:
            df: 包含基础数据和技术指标的DataFrame
            
        Returns:
            包含特征的DataFrame
        """
        if df.empty or len(df) < 20:
            logger.warning(f"数据长度{len(df)}小于窗口大小20，跳过特征创建")
            return df
        
        try:
            result_df = df.copy()
            
            # 价格特征
            if all(col in df.columns for col in ['open', 'high', 'low', 'close']):
                # 振幅
                result_df['amplitude'] = (result_df['high'] - result_df['low']) / result_df['close'] * 100
                
                # 上下影线
                result_df['upper_shadow'] = (result_df['high'] - result_df[['open', 'close']].max(axis=1)) / result_df['close'] * 100
                result_df['lower_shadow'] = (result_df[['open', 'close']].min(axis=1) - result_df['low']) / result_df['close'] * 100
                
                # 实体大小
                result_df['body_size'] = abs(result_df['close'] - result_df['open']) / result_df['close'] * 100
                
                # 收盘价位置
                result_df['close_position'] = (result_df['close'] - result_df['low']) / (result_df['high'] - result_df['low'])
            
            # 趋势特征
            if 'ma5' in df.columns and 'ma20' in df.columns:
                result_df['trend_short'] = (result_df['ma5'] / result_df['ma20'] - 1) * 100
            
            if 'ma20' in df.columns and 'ma60' in df.columns:
                result_df['trend_long'] = (result_df['ma20'] / result_df['ma60'] - 1) * 100
            
            # 波动率特征
            result_df['volatility_5'] = result_df['close'].rolling(5).std() / result_df['close'].rolling(5).mean()
            result_df['volatility_20'] = result_df['close'].rolling(20).std() / result_df['close'].rolling(20).mean()
            
            # 成交量特征
            vol_col = 'vol' if 'vol' in df.columns else 'volume'
            if vol_col in df.columns:
                result_df['vol_price_trend'] = result_df[vol_col] / result_df['close']
                result_df['vol_change'] = result_df[vol_col].pct_change()
            
            logger.debug(f"特征工程完成，新增{len(result_df.columns) - len(df.columns)}个特征")
            return result_df
            
        except Exception as e:
            logger.error(f"特征工程失败: {e}")
            return df
    
    def detect_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        检测K线形态
        
        Args:
            df: 包含OHLC数据的DataFrame
            
        Returns:
            包含形态识别结果的DataFrame
        """
        if df.empty or len(df) < 3:
            return df
        
        try:
            result_df = df.copy()
            
            if not all(col in df.columns for col in ['open', 'high', 'low', 'close']):
                return df
            
            # 计算实体和影线
            body = abs(result_df['close'] - result_df['open'])
            upper_shadow = result_df['high'] - result_df[['open', 'close']].max(axis=1)
            lower_shadow = result_df[['open', 'close']].min(axis=1) - result_df['low']
            
            # 十字星
            result_df['doji'] = (body / result_df['close'] < 0.003).astype(int)
            
            # 锤子线
            hammer_condition = (
                (lower_shadow > 2 * body) & 
                (upper_shadow < 0.1 * body) &
                (body > 0)
            )
            result_df['hammer'] = hammer_condition.astype(int)
            
            # 倒锤子线
            inverted_hammer_condition = (
                (upper_shadow > 2 * body) & 
                (lower_shadow < 0.1 * body) &
                (body > 0)
            )
            result_df['inverted_hammer'] = inverted_hammer_condition.astype(int)
            
            # 长阳线
            long_green = (
                (result_df['close'] > result_df['open']) &
                (body / result_df['close'] > 0.05)
            )
            result_df['long_green'] = long_green.astype(int)
            
            # 长阴线
            long_red = (
                (result_df['close'] < result_df['open']) &
                (body / result_df['close'] > 0.05)
            )
            result_df['long_red'] = long_red.astype(int)
            
            # 连续上涨/下跌
            result_df['consecutive_up'] = 0
            result_df['consecutive_down'] = 0
            
            for i in range(1, len(result_df)):
                if result_df['close'].iloc[i] > result_df['close'].iloc[i-1]:
                    if i > 0 and result_df['consecutive_up'].iloc[i-1] > 0:
                        result_df.loc[result_df.index[i], 'consecutive_up'] = result_df['consecutive_up'].iloc[i-1] + 1
                    else:
                        result_df.loc[result_df.index[i], 'consecutive_up'] = 1
                elif result_df['close'].iloc[i] < result_df['close'].iloc[i-1]:
                    if i > 0 and result_df['consecutive_down'].iloc[i-1] > 0:
                        result_df.loc[result_df.index[i], 'consecutive_down'] = result_df['consecutive_down'].iloc[i-1] + 1
                    else:
                        result_df.loc[result_df.index[i], 'consecutive_down'] = 1
            
            logger.debug("K线形态识别完成")
            return result_df
            
        except Exception as e:
            logger.error(f"K线形态识别失败: {e}")
            return df
