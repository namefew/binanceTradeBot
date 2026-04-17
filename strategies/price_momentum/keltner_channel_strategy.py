"""
肯特纳通道策略
基于平均真实波幅的通道策略
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class KeltnerChannelStrategy(BaseStrategy):
    """
    肯特纳通道策略
    基于平均真实波幅的通道策略
    """
    
    def __init__(self, period=20, multiplier=2, transaction_cost=0.001, position_size=1.0):
        super().__init__("Keltner Channel Strategy", transaction_cost, indicator_short_name="Keltner Channel", position_size=position_size)
        self.period = period
        self.multiplier = multiplier
        
    def generate_signals(self):
        """
        生成肯特纳通道交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有high, low, close列
        required_columns = ['high', 'low', 'close']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算典型价格
        tp = (self.data['high'] + self.data['low'] + self.data['close']) / 3
        
        # 计算EMA
        ema = tp.ewm(span=self.period).mean()
        
        # 计算真实波幅
        high_low = self.data['high'] - self.data['low']
        high_close = abs(self.data['high'] - self.data['close'].shift(1))
        low_close = abs(self.data['low'] - self.data['close'].shift(1))
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        
        # 计算ATR
        atr = tr.rolling(window=self.period).mean()
        
        # 计算上下轨
        upper_channel = ema + (atr * self.multiplier)
        lower_channel = ema - (atr * self.multiplier)
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[self.data['close'] > upper_channel] = 1   # 价格突破上轨时买入
        self.signals[self.data['close'] < lower_channel] = -1  # 价格跌破下轨时卖出