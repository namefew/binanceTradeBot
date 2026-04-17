"""
Hull移动平均线策略 (Hull Moving Average)
一种快速且平滑的移动平均线
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class HullMAStrategy(BaseStrategy):
    """
    Hull移动平均线策略 (Hull Moving Average)
    一种快速且平滑的移动平均线
    """
    
    def __init__(self, period=9, transaction_cost=0.001, position_size=1.0):
        super().__init__("Hull MA Strategy", transaction_cost, indicator_short_name="Hull MA", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成Hull MA交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算Hull MA
        half_period = int(self.period / 2)
        sqrt_period = int(np.sqrt(self.period))
        
        # 计算WMA
        wma_half = self.data['close'].rolling(window=half_period).apply(
            lambda x: (x * np.arange(1, half_period + 1)).sum() / np.arange(1, half_period + 1).sum(), raw=True)
        wma_full = self.data['close'].rolling(window=self.period).apply(
            lambda x: (x * np.arange(1, self.period + 1)).sum() / np.arange(1, self.period + 1).sum(), raw=True)
        
        # 计算差值
        diff = 2 * wma_half - wma_full
        
        # 计算Hull MA
        hull_ma = diff.rolling(window=sqrt_period).apply(
            lambda x: (x * np.arange(1, sqrt_period + 1)).sum() / np.arange(1, sqrt_period + 1).sum(), raw=True)
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[self.data['close'] > hull_ma] = 1   # 价格高于Hull MA时买入
        self.signals[self.data['close'] < hull_ma] = -1  # 价格低于Hull MA时卖出