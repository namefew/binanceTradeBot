"""
相对动量指数策略 (Relative Momentum Index, RMI)
根据研报：基于动量的相对强度指标
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class RelativeMomentumIndexStrategy(BaseStrategy):
    """
    相对动量指数策略 (Relative Momentum Index, RMI)
    根据研报：基于动量的相对强度指标
    """
    
    def __init__(self, period=20, momentum=4, overbought=70, oversold=30, transaction_cost=0.001, position_size=1.0):
        super().__init__("Relative Momentum Index Strategy", transaction_cost, indicator_short_name="RMI", position_size=position_size)
        self.period = period
        self.momentum = momentum
        self.overbought = overbought
        self.oversold = oversold
        
    def generate_signals(self):
        """
        生成Relative Momentum Index交易信号
        当指标上穿/下穿阈值时产生交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算动量
        close_diff = self.data['close'].diff(self.momentum)
        momentum_up = close_diff.where(close_diff > 0, 0)
        momentum_down = (-close_diff).where(close_diff < 0, 0)
        
        # 计算平均动量
        avg_up = momentum_up.rolling(window=self.period).mean()
        avg_down = momentum_down.rolling(window=self.period).mean()
        
        # 计算RMI
        rmi = 100 * avg_up / (avg_up + avg_down)
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # RMI上穿30时买入
        self.signals[(rmi > self.oversold) & (rmi.shift(1) <= self.oversold)] = 1
        # RMI下穿70时卖出
        self.signals[(rmi < self.overbought) & (rmi.shift(1) >= self.overbought)] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)