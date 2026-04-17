"""
三重指数移动平均线(T3)策略
根据研报：三重EMA计算
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class T3Strategy(BaseStrategy):
    """
    三重指数移动平均线(T3)策略
    根据研报：三重EMA计算
    """
    
    def __init__(self, n=20, va=0.5, transaction_cost=0.001, position_size=1.0):
        super().__init__("T3 Strategy", transaction_cost, indicator_short_name="T3", position_size=position_size)
        self.n = n
        self.va = va
        
    def generate_signals(self):
        """
        生成T3交易信号
        当收盘价上穿/下穿T3时产生买入/卖出信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算T3指标
        ema1 = self.data['close'].ewm(span=self.n).mean()
        ema2 = ema1.ewm(span=self.n).mean()
        ema3 = ema2.ewm(span=self.n).mean()
        
        t1 = ema1 * (1 + self.va) - ema2 * self.va
        t2 = t1.ewm(span=self.n).mean() * (1 + self.va) - t1.ewm(span=self.n).mean() * self.va
        t3 = t2.ewm(span=self.n).mean() * (1 + self.va) - t2.ewm(span=self.n).mean() * self.va
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # 收盘价上穿T3时买入
        self.signals[(self.data['close'] > t3) & (self.data['close'].shift(1) <= t3.shift(1))] = 1
        # 收盘价下穿T3时卖出
        self.signals[(self.data['close'] < t3) & (self.data['close'].shift(1) >= t3.shift(1))] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)