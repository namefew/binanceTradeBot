"""
双重指数移动平均线策略 (Double Exponential Moving Average)
一种快速响应价格变化的移动平均线
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class DEMAStrategy(BaseStrategy):
    """
    双重指数移动平均线策略 (Double Exponential Moving Average)
    一种快速响应价格变化的移动平均线
    """
    
    def __init__(self, period=20, transaction_cost=0.001, position_size=1.0):
        super().__init__("DEMA Strategy", transaction_cost, indicator_short_name="DEMA", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成DEMA交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算DEMA
        ema1 = self.data['close'].ewm(span=self.period).mean()
        ema2 = ema1.ewm(span=self.period).mean()
        dema = 2 * ema1 - ema2
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[(self.data['close'] > dema) & (self.data['close'].shift(1) <= dema.shift(1))] = 1   # 价格上穿DEMA时买入
        self.signals[(self.data['close'] < dema) & (self.data['close'].shift(1) >= dema.shift(1))] = -1  # 价格下穿DEMA时卖出