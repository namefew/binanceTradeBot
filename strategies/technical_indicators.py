"""
技术指标策略实现
实现研究报告中的各种技术指标择时策略
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy

class TechnicalIndicators:
    """
    技术指标计算类
    提供各种技术指标的计算方法
    """
    
    @staticmethod
    def atr(data, period):
        """
        计算ATR指标
        """
        high_low = data['high'] - data['low']
        high_close = abs(data['high'] - data['close'].shift())
        low_close = abs(data['low'] - data['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        return true_range.rolling(window=period).mean()
    
    @staticmethod
    def cmf(data, period):
        """
        计算CMF指标
        """
        money_flow_volume = ((data['close'] - data['low']) - (data['high'] - data['close'])) / (data['high'] - data['low']) * data['volume']
        cmf = money_flow_volume.rolling(window=period).sum() / data['volume'].rolling(window=period).sum()
        return cmf
    
    @staticmethod
    def stochastic(fast_k, slow_k, period):
        """
        计算随机指标
        """
        # 处理空值和异常值
        if fast_k.empty or slow_k.empty:
            return pd.Series(0, index=fast_k.index)
            
        lowest_fast_k = fast_k.rolling(window=period).min()
        highest_fast_k = fast_k.rolling(window=period).max()
        
        # 避免除以零
        range_k = highest_fast_k - lowest_fast_k
        range_k = range_k.replace(0, np.nan)
        
        stc = 100 * (fast_k - lowest_fast_k) / range_k
        
        # 处理NaN值并计算移动平均
        result = stc.rolling(window=period).mean()
        return result.fillna(50)  # 用中性值填充NaN
    
    @staticmethod
    def vortex(data, period):
        """
        计算涡流指标
        """
        high_low = data['high'] - data['low']
        high_prev_close = abs(data['high'] - data['close'].shift())
        low_prev_close = abs(data['low'] - data['close'].shift())
        
        tr = pd.concat([high_low, high_prev_close, low_prev_close], axis=1).max(axis=1)
        vi_plus = abs(data['high'] - data['low'].shift())
        vi_minus = abs(data['low'] - data['high'].shift())
        
        vi_plus_smooth = vi_plus.rolling(window=period).sum()
        vi_minus_smooth = vi_minus.rolling(window=period).sum()
        tr_smooth = tr.rolling(window=period).sum()
        
        vi_plus_indicator = vi_plus_smooth / tr_smooth
        vi_minus_indicator = vi_minus_smooth / tr_smooth
        
        return pd.DataFrame({'VI+': vi_plus_indicator, 'VI-': vi_minus_indicator})
    
    @staticmethod
    def wma(series, period):
        """
        计算加权移动平均
        """
        weights = np.arange(1, period + 1)
        return series.rolling(window=period).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)
    
    @staticmethod
    def rsi(series, period):
        """
        计算RSI指标
        """
        delta = series.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def macd(series, fast_period=12, slow_period=26, signal_period=9):
        """
        计算MACD指标
        """
        exp1 = series.ewm(span=fast_period).mean()
        exp2 = series.ewm(span=slow_period).mean()
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=signal_period).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram

class MovingAverageStrategy(BaseStrategy):
    """
    移动平均线策略
    """
    
    def __init__(self, short_window=5, long_window=20, transaction_cost=0.001, position_size=1.0):
        super().__init__("Moving Average Strategy", transaction_cost, indicator_short_name="MA", position_size=position_size)
        self.short_window = short_window
        self.long_window = long_window
        
    def generate_signals(self):
        """
        生成移动平均线交易信号
        当短期均线向上穿越长期均线时买入，向下穿越时卖出
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算移动平均线
        short_ma = self.data['close'].rolling(window=self.short_window).mean()
        long_ma = self.data['close'].rolling(window=self.long_window).mean()
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[short_ma > long_ma] = 1   # 买入信号
        self.signals[short_ma < long_ma] = -1  # 卖出信号
        
        # 处理信号变化点 - 将0替换为NaN，然后前向填充，最后剩余的NaN填0
        self.signals = self.signals.replace(0, pd.NA).ffill().fillna(0)

class RSIStategy(BaseStrategy):
    """
    RSI相对强弱指数策略
    """
    
    def __init__(self, period=14, overbought=70, oversold=30, transaction_cost=0.001, position_size=1.0):
        super().__init__("RSI Strategy", transaction_cost, indicator_short_name="RSI", position_size=position_size)
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
        
    def generate_signals(self):
        """
        生成RSI交易信号
        当RSI低于超卖区时买入，高于超买区时卖出
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算价格变化
        delta = self.data['close'].diff()
        
        # 分离上涨和下跌
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # 计算平均上涨和下跌
        avg_gain = gain.rolling(window=self.period).mean()
        avg_loss = loss.rolling(window=self.period).mean()
        
        # 计算RS
        rs = avg_gain / avg_loss
        
        # 计算RSI
        rsi = 100 - (100 / (1 + rs))
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[rsi < self.oversold] = 1    # 超卖时买入
        self.signals[rsi > self.overbought] = -1 # 超买时卖出

class MACDStrategy(BaseStrategy):
    """
    MACD策略
    """
    
    def __init__(self, fast_period=12, slow_period=26, signal_period=9, transaction_cost=0.001, position_size=1.0):
        super().__init__("MACD Strategy", transaction_cost, indicator_short_name="MACD", position_size=position_size)
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        
    def generate_signals(self):
        """
        生成MACD交易信号
        当MACD线上穿信号线时买入，下穿时卖出
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算MACD
        exp1 = self.data['close'].ewm(span=self.fast_period).mean()
        exp2 = self.data['close'].ewm(span=self.slow_period).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=self.signal_period).mean()
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[macd > signal] = 1   # MACD线上穿信号线时买入
        self.signals[macd < signal] = -1  # MACD线下穿信号线时卖出

class BollingerBandsStrategy(BaseStrategy):
    """
    布林带策略
    """
    
    def __init__(self, window=20, num_std=2, transaction_cost=0.001, position_size=1.0):
        super().__init__("Bollinger Bands Strategy", transaction_cost, indicator_short_name="BB", position_size=position_size)
        self.window = window
        self.num_std = num_std
        
    def generate_signals(self):
        """
        生成布林带交易信号
        当价格突破上轨时卖出，突破下轨时买入
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算布林带
        rolling_mean = self.data['close'].rolling(window=self.window).mean()
        rolling_std = self.data['close'].rolling(window=self.window).std()
        
        upper_band = rolling_mean + (rolling_std * self.num_std)
        lower_band = rolling_mean - (rolling_std * self.num_std)
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[self.data['close'] < lower_band] = 1   # 价格低于下轨时买入
        self.signals[self.data['close'] > upper_band] = -1  # 价格高于上轨时卖出

class KDStrategy(BaseStrategy):
    """
    KD指标策略（随机指标）
    """
    
    def __init__(self, k_period=14, d_period=3, overbought=80, oversold=20, transaction_cost=0.001, position_size=1.0):
        super().__init__("KD Strategy", transaction_cost, indicator_short_name="KD", position_size=position_size)
        self.k_period = k_period
        self.d_period = d_period
        self.overbought = overbought
        self.oversold = oversold
        
    def generate_signals(self):
        """
        生成KD交易信号
        当K线上穿D线且在超卖区时买入，K线下穿D线且在超买区时卖出
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有必要的列
        required_columns = ['high', 'low', 'close']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算KD指标
        low_min = self.data['low'].rolling(window=self.k_period).min()
        high_max = self.data['high'].rolling(window=self.k_period).max()
        
        # 计算K值
        k = 100 * ((self.data['close'] - low_min) / (high_max - low_min))
        # 计算D值（K的移动平均）
        d = k.rolling(window=self.d_period).mean()
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # K线上穿D线且在超卖区时买入
        self.signals[(k > d) & (k.shift(1) <= d.shift(1)) & (k < self.oversold)] = 1
        # K线下穿D线且在超买区时卖出
        self.signals[(k < d) & (k.shift(1) >= d.shift(1)) & (k > self.overbought)] = -1


class BuyAndHoldStrategy(BaseStrategy):
    """
    买入并持有策略
    最简单的策略，在第一天买入并一直持有
    """
    
    def __init__(self, transaction_cost=0.001, position_size=1.0):
        super().__init__("Buy and Hold Strategy", transaction_cost, indicator_short_name="BuyHold", position_size=position_size)
        
    def generate_signals(self):
        """
        生成买入并持有交易信号
        第一天买入并一直持有
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 生成信号：第一天买入(1)，之后一直持有(1)
        self.signals = pd.Series(1, index=self.data.index)
        # 第一天设置为0，然后第二天买入
        self.signals.iloc[0] = 0


def calculate_technical_indicators(data):
    """
    计算多种技术指标
    
    Parameters:
    data (DataFrame): 股票数据
    
    Returns:
    DataFrame: 包含各种技术指标的数据
    """
    # 检查数据中是否有必要的列
    required_columns = ['open', 'high', 'low', 'close', 'volume']
    if not all(col in data.columns for col in required_columns):
        raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
    
    df = data.copy()
    
    # 移动平均线
    df['MA5'] = df['close'].rolling(window=5).mean()
    df['MA10'] = df['close'].rolling(window=10).mean()
    df['MA20'] = df['close'].rolling(window=20).mean()
    df['MA60'] = df['close'].rolling(window=60).mean()
    
    # RSI
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    exp1 = df['close'].ewm(span=12).mean()
    exp2 = df['close'].ewm(span=26).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_signal'] = df['MACD'].ewm(span=9).mean()
    df['MACD_histogram'] = df['MACD'] - df['MACD_signal']
    
    # 布林带
    df['BB_middle'] = df['close'].rolling(window=20).mean()
    bb_std = df['close'].rolling(window=20).std()
    df['BB_upper'] = df['BB_middle'] + (bb_std * 2)
    df['BB_lower'] = df['BB_middle'] - (bb_std * 2)
    
    # KD指标
    low_min = df['low'].rolling(window=14).min()
    high_max = df['high'].rolling(window=14).max()
    df['K'] = 100 * ((df['close'] - low_min) / (high_max - low_min))
    df['D'] = df['K'].rolling(window=3).mean()
    
    return df