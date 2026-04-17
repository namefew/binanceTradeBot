"""
三重指数移动平均线策略 (Triple Exponential Moving Average)
比DEMA更加平滑的移动平均线
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class TEMAStrategy(BaseStrategy):
    """
    三重指数移动平均线策略 (Triple Exponential Moving Average)
    比DEMA更加平滑的移动平均线
    """
    
    def __init__(self, period=20, transaction_cost=0.001, position_size=1.0):
        super().__init__("TEMA Strategy", transaction_cost, indicator_short_name="TEMA", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成TEMA交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算TEMA
        ema1 = self.data['close'].ewm(span=self.period).mean()
        ema2 = ema1.ewm(span=self.period).mean()
        ema3 = ema2.ewm(span=self.period).mean()
        tema = 3 * ema1 - 3 * ema2 + ema3
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[(self.data['close'] > tema) & (self.data['close'].shift(1) <= tema.shift(1))] = 1   # 价格上穿TEMA时买入
        self.signals[(self.data['close'] < tema) & (self.data['close'].shift(1) >= tema.shift(1))] = -1  # 价格下穿TEMA时卖出