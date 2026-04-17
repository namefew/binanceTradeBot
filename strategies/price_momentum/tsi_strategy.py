"""
趋势强度策略 (Trend Strength Index)
衡量趋势强度的指标
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class TSIStrategy(BaseStrategy):
    """
    趋势强度策略 (Trend Strength Index)
    衡量趋势强度的指标
    """
    
    def __init__(self, period=20, transaction_cost=0.001, position_size=1.0):
        super().__init__("Trend Strength Index Strategy", transaction_cost, indicator_short_name="TSI", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成趋势强度指数交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算趋势强度指数
        price_change = self.data['close'] - self.data['close'].shift(self.period)
        abs_price_change = abs(self.data['close'] - self.data['close'].shift(1)).rolling(window=self.period).sum()
        
        # 避免除零
        abs_price_change = abs_price_change.replace(0, np.nan)
        
        tsi = (price_change / abs_price_change) * 100
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[tsi > 0] = 1   # 指数为正时买入
        self.signals[tsi < 0] = -1  # 指数为负时卖出