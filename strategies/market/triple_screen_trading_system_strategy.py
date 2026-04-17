"""
三重屏幕交易系统策略
结合多个时间框架的交易系统
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class TripleScreenTradingSystemStrategy(BaseStrategy):
    """
    三重屏幕交易系统策略
    结合多个时间框架的交易系统
    """
    
    def __init__(self, period=20, transaction_cost=0.001, position_size=1.0):
        super().__init__("Triple Screen Trading System Strategy", transaction_cost, indicator_short_name="TSTS", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成三重屏幕交易系统交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 检查是否有足够数据进行重采样
        try:
            # 第一屏幕：长期趋势（使用月线数据，这里用周线近似）
            if isinstance(self.data.index, pd.DatetimeIndex):
                weekly_close = self.data['close'].resample('W').last()
                long_term_ma = weekly_close.rolling(window=self.period).mean()
                long_term_trend = (weekly_close > long_term_ma).astype(int).replace(0, -1)
                # 将周线数据重新索引到日线数据
                long_term_trend = long_term_trend.reindex(self.data.index, method='ffill')
            else:
                # 如果没有日期索引，使用简单移动平均作为长期趋势
                long_term_ma = self.data['close'].rolling(window=self.period*5).mean()  # 近似5周
                long_term_trend = pd.Series((self.data['close'] > long_term_ma).astype(int).replace(0, -1), index=self.data.index)
        except Exception as e:
            # 如果重采样失败，使用简单移动平均作为长期趋势
            long_term_ma = self.data['close'].rolling(window=self.period*5).mean()  # 近似5周
            long_term_trend = pd.Series((self.data['close'] > long_term_ma).astype(int).replace(0, -1), index=self.data.index)
        
        # 第二屏幕：中期趋势（使用日线数据）
        medium_term_ma = self.data['close'].rolling(window=self.period).mean()
        medium_term_trend = (self.data['close'] > medium_term_ma).astype(int).replace(0, -1)
        
        # 第三屏幕：短期信号（使用震荡指标，这里用RSI）
        delta = self.data['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # 当长期趋势向上，中期趋势向上，且RSI超卖时买入
        self.signals[(long_term_trend > 0) & (medium_term_trend > 0) & (rsi < 30)] = 1
        # 当长期趋势向下，中期趋势向下，且RSI超买时卖出
        self.signals[(long_term_trend < 0) & (medium_term_trend < 0) & (rsi > 70)] = -1