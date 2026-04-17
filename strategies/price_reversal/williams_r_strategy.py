"""
Williams %R 策略
一种动量指标，用于测量超买和超卖水平
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class WilliamsRStrategy(BaseStrategy):
    """
    Williams %R 策略
    一种动量指标，用于测量超买和超卖水平
    """
    
    def __init__(self, period=14, overbought=-20, oversold=-80, transaction_cost=0.001, position_size=1.0):
        super().__init__("Williams %R Strategy", transaction_cost, indicator_short_name="Williams %R", position_size=position_size)
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
        
    def generate_signals(self):
        """
        生成Williams %R交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有必要的列
        required_columns = ['high', 'low', 'close']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算Williams %R
        highest_high = self.data['high'].rolling(window=self.period).max()
        lowest_low = self.data['low'].rolling(window=self.period).min()
        williams_r = (highest_high - self.data['close']) / (highest_high - lowest_low) * -100
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[williams_r < self.oversold] = 1    # 超卖时买入
        self.signals[williams_r > self.overbought] = -1 # 超买时卖出