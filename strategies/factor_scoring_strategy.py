"""
因子打分择时策略
根据多个技术指标因子进行打分，综合判断市场趋势
"""

import pandas as pd
import numpy as np
from strategies.enhanced_base_strategy import EnhancedBaseStrategy


class FactorScoringStrategy(EnhancedBaseStrategy):
    """
    因子打分择时策略
    根据多个技术指标因子进行打分，综合判断市场趋势
    """
    
    def __init__(self, 
                 ma_period=20, 
                 rsi_period=14, 
                 macd_fast=12, 
                 macd_slow=26, 
                 macd_signal=9,
                 bb_period=20,
                 bb_std=2,
                 williams_period=14,
                 scoring_threshold=0, 
                 transaction_cost=0.001):
        """
        初始化因子打分择时策略
        
        Parameters:
        ma_period: 移动平均线周期
        rsi_period: RSI周期
        macd_fast: MACD快线周期
        macd_slow: MACD慢线周期
        macd_signal: MACD信号线周期
        bb_period: 布林带周期
        bb_std: 布林带标准差倍数
        williams_period: 威廉指标周期
        scoring_threshold: 信号阈值，超过该值产生买入信号，低于负值产生卖出信号
        transaction_cost: 交易成本
        """
        super().__init__("Factor Scoring Strategy", transaction_cost, indicator_short_name="Factor Scoring")
        self.ma_period = ma_period
        self.rsi_period = rsi_period
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.williams_period = williams_period
        self.scoring_threshold = scoring_threshold
        
    def calculate_rsi(self, prices, period=14):
        """
        计算RSI指标
        
        Parameters:
        prices: 价格序列
        period: 计算周期
        
        Returns:
        RSI值
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices, fast_period=12, slow_period=26, signal_period=9):
        """
        计算MACD指标
        
        Parameters:
        prices: 价格序列
        fast_period: 快线周期
        slow_period: 慢线周期
        signal_period: 信号线周期
        
        Returns:
        MACD线、信号线和柱状图
        """
        ema_fast = prices.ewm(span=fast_period).mean()
        ema_slow = prices.ewm(span=slow_period).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal_period).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
    
    def calculate_bollinger_bands(self, prices, period=20, std_multiplier=2):
        """
        计算布林带指标
        
        Parameters:
        prices: 价格序列
        period: 计算周期
        std_multiplier: 标准差倍数
        
        Returns:
        布林带上轨、中轨和下轨
        """
        middle_band = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper_band = middle_band + (std * std_multiplier)
        lower_band = middle_band - (std * std_multiplier)
        return upper_band, middle_band, lower_band
    
    def calculate_williams_r(self, high, low, close, period=14):
        """
        计算威廉指标
        
        Parameters:
        high: 最高价序列
        low: 最低价序列
        close: 收盘价序列
        period: 计算周期
        
        Returns:
        威廉指标值
        """
        highest_high = high.rolling(window=period).max()
        lowest_low = low.rolling(window=period).min()
        williams_r = (highest_high - close) / (highest_high - lowest_low) * -100
        return williams_r
    
    def calculate_volume_ratio(self, volume, period=10):
        """
        计算成交量比率
        
        Parameters:
        volume: 成交量序列
        period: 计算周期
        
        Returns:
        成交量比率
        """
        volume_ma = volume.rolling(window=period).mean()
        volume_ratio = volume / volume_ma
        return volume_ratio
    
    def generate_signals(self):
        """
        生成因子打分交易信号
        使用移动平均线、RSI、MACD、布林带、威廉指标和成交量六个因子进行打分
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有必要的列
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 初始化因子得分
        ma_score = pd.Series(0, index=self.data.index)
        rsi_score = pd.Series(0, index=self.data.index)
        macd_score = pd.Series(0, index=self.data.index)
        bb_score = pd.Series(0, index=self.data.index)
        williams_score = pd.Series(0, index=self.data.index)
        volume_score = pd.Series(0, index=self.data.index)
        
        # 1. 移动平均线因子
        # 当价格上穿移动平均线时得1分，下穿时得-1分，否则得0分
        ma = self.data['close'].rolling(window=self.ma_period).mean()
        ma_score[(self.data['close'] > ma) & (self.data['close'].shift(1) <= ma.shift(1))] = 1
        ma_score[(self.data['close'] < ma) & (self.data['close'].shift(1) >= ma.shift(1))] = -1
        
        # 2. RSI因子
        # 当RSI从超卖区上穿50时得1分，从超买区下穿50时得-1分，否则得0分
        rsi = self.calculate_rsi(self.data['close'], self.rsi_period)
        rsi_score[(rsi > 50) & (rsi.shift(1) <= 50) & (rsi.shift(2) <= 30)] = 1
        rsi_score[(rsi < 50) & (rsi.shift(1) >= 50) & (rsi.shift(2) >= 70)] = -1
        
        # 3. MACD因子
        # 当MACD柱状图由负转正时得1分，由正转负时得-1分，否则得0分
        _, _, macd_histogram = self.calculate_macd(self.data['close'], 
                                                  self.macd_fast, 
                                                  self.macd_slow, 
                                                  self.macd_signal)
        macd_score[(macd_histogram > 0) & (macd_histogram.shift(1) <= 0)] = 1
        macd_score[(macd_histogram < 0) & (macd_histogram.shift(1) >= 0)] = -1
        
        # 4. 布林带因子
        # 当价格下穿下轨时得1分，上穿上轨时得-1分，否则得0分
        upper_band, middle_band, lower_band = self.calculate_bollinger_bands(self.data['close'], 
                                                                            self.bb_period, 
                                                                            self.bb_std)
        bb_score[(self.data['close'] < lower_band) & (self.data['close'].shift(1) >= lower_band.shift(1))] = 1
        bb_score[(self.data['close'] > upper_band) & (self.data['close'].shift(1) <= upper_band.shift(1))] = -1
        
        # 5. 威廉指标因子
        # 当威廉指标从超卖区上穿-50时得1分，从超买区下穿-50时得-1分，否则得0分
        williams_r = self.calculate_williams_r(self.data['high'], 
                                               self.data['low'], 
                                               self.data['close'], 
                                               self.williams_period)
        williams_score[(williams_r > -50) & (williams_r.shift(1) <= -50) & (williams_r.shift(2) <= -80)] = 1
        williams_score[(williams_r < -50) & (williams_r.shift(1) >= -50) & (williams_r.shift(2) >= -20)] = -1
        
        # 6. 成交量因子
        # 当成交量放大时得1分，缩小时得-1分，否则得0分
        volume_ratio = self.calculate_volume_ratio(self.data['volume'])
        volume_score[volume_ratio > 1.5] = 1
        volume_score[volume_ratio < 0.5] = -1
        
        # 计算总得分
        total_score = ma_score + rsi_score + macd_score + bb_score + williams_score + volume_score
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[total_score > self.scoring_threshold] = 1   # 总得分超过阈值时买入
        self.signals[total_score < -self.scoring_threshold] = -1 # 总得分低于负阈值时卖出