"""
相对活力指数策略 (Relative Vigor Index)
衡量价格变化活力的振荡器指标
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class RVIStrategy(BaseStrategy):
    """
    相对活力指数策略 (Relative Vigor Index)
    衡量价格变化活力的振荡器指标
    """
    
    def __init__(self, period=10, transaction_cost=0.001, position_size=1.0):
        super().__init__("Relative Vigor Index Strategy", transaction_cost, indicator_short_name="RVI", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成RVI交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有open, high, low, close列
        required_columns = ['open', 'high', 'low', 'close']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算CO值（收盘价减去开盘价）
        co = self.data['close'] - self.data['open']
        
        # 计算HL值（最高价减去最低价）
        hl = self.data['high'] - self.data['low']
        
        # 计算RVI的分子和分母
        numerator = co.rolling(window=self.period).apply(
            lambda x: (x[0] + 2*x[-self.period//2] + 2*x[-self.period//2] + x[-1]) / 6, raw=True)
        denominator = hl.rolling(window=self.period).apply(
            lambda x: (x[0] + 2*x[-self.period//2] + 2*x[-self.period//2] + x[-1]) / 6, raw=True)
        
        # 计算RVI
        rvi = numerator / denominator
        
        # 计算信号线
        rvi_signal = (rvi + 2*rvi.shift(1) + 2*rvi.shift(2) + rvi.shift(3)) / 6
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[(rvi > rvi_signal) & (rvi.shift(1) <= rvi_signal.shift(1))] = 1   # RVI上穿信号线时买入
        self.signals[(rvi < rvi_signal) & (rvi.shift(1) >= rvi_signal.shift(1))] = -1  # RVI下穿信号线时卖出