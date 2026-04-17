"""
简易波动指标策略 (Ease of Movement)
衡量价格移动的容易程度
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class EaseOfMovementStrategy(BaseStrategy):
    """
    简易波动指标策略 (Ease of Movement)
    衡量价格移动的容易程度
    """
    
    def __init__(self, period=14, transaction_cost=0.001, position_size=1.0):
        super().__init__("Ease of Movement Strategy", transaction_cost, indicator_short_name="EMV", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成简易波动指标交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有high, low, volume列
        required_columns = ['high', 'low', 'volume']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算距离移动
        distance_moved = ((self.data['high'] + self.data['low']) / 2) - ((self.data['high'].shift(1) + self.data['low'].shift(1)) / 2)
        
        # 计算箱体比率
        box_ratio = (self.data['volume'] / 1000000) / (self.data['high'] - self.data['low'])
        
        # 计算EMV
        emv = distance_moved / box_ratio
        emv_ma = emv.rolling(window=self.period).mean()
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[emv_ma > 0] = 1   # EMV为正时买入
        self.signals[emv_ma < 0] = -1  # EMV为负时卖出