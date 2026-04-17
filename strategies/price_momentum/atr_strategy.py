"""
ATR策略（平均真实波幅策略）
基于平均真实波幅来设置止损和止盈点
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class ATRStrategy(BaseStrategy):
    """
    ATR策略（平均真实波幅策略）
    基于平均真实波幅来设置止损和止盈点
    """
    
    def __init__(self, period=14, multiplier=2.0, transaction_cost=0.001, position_size=1.0):
        super().__init__("ATR Strategy", transaction_cost, indicator_short_name="ATR", position_size=position_size)
        self.period = period
        self.multiplier = multiplier
        self.position = 0  # 当前持仓状态
        
    def generate_signals(self):
        """
        生成ATR交易信号
        基于ATR突破生成信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有high, low, close列
        required_columns = ['high', 'low', 'close']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算真实波幅（TR）
        high_low = self.data['high'] - self.data['low']
        high_close = abs(self.data['high'] - self.data['close'].shift(1))
        low_close = abs(self.data['low'] - self.data['close'].shift(1))
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        
        # 计算ATR
        atr = tr.rolling(window=self.period).mean()
        
        # 计算上下轨
        upper_band = self.data['close'] + (atr * self.multiplier)
        lower_band = self.data['close'] - (atr * self.multiplier)
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # 当价格突破上轨时买入
        self.signals[self.data['close'] > upper_band] = 1
        # 当价格跌破下轨时卖出
        self.signals[self.data['close'] < lower_band] = -1