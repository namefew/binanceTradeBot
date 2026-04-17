"""
CCI策略的替代实现
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class CCIAlternativeStrategy(BaseStrategy):
    """
    CCI策略的替代实现
    """
    
    def __init__(self, period=20, overbought=100, oversold=-100, transaction_cost=0.001, position_size=1.0):
        super().__init__("CCI Alternative Strategy", transaction_cost, indicator_short_name="CCI", position_size=position_size)
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
        
    def generate_signals(self):
        """
        生成CCI交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有high, low, close列
        required_columns = ['high', 'low', 'close']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算典型价格
        tp = (self.data['high'] + self.data['low'] + self.data['close']) / 3
        
        # 计算移动平均
        sma = tp.rolling(window=self.period).mean()
        
        # 计算平均绝对偏差
        mean_dev = tp.rolling(window=self.period).apply(lambda x: np.abs(x - x.mean()).mean())
        
        # 计算CCI
        cci = (tp - sma) / (0.015 * mean_dev)
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[cci < self.oversold] = 1    # 超卖时买入
        self.signals[cci > self.overbought] = -1 # 超买时卖出