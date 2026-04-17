"""
加速度/减速度指标策略 (AC)
衡量动量的二阶导数
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class AccelerationDecelerationStrategy(BaseStrategy):
    """
    加速度/减速度指标策略 (AC)
    衡量动量的二阶导数
    """
    
    def __init__(self, transaction_cost=0.001, position_size=1.0):
        super().__init__("Acceleration/Deceleration Strategy", transaction_cost, indicator_short_name="AC", position_size=position_size)
        
    def generate_signals(self):
        """
        生成加速度/减速度指标交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有high, low列
        required_columns = ['high', 'low']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算中点
        midpoint = (self.data['high'] + self.data['low']) / 2
        
        # 计算AO (Awesome Oscillator)
        fast_sma = midpoint.rolling(window=5).mean()
        slow_sma = midpoint.rolling(window=34).mean()
        ao = fast_sma - slow_sma
        
        # 计算AC (Acceleration/Deceleration)
        ao_sma = ao.rolling(window=5).mean()
        ac = ao - ao_sma
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[(ac > 0) & (ac.shift(1) <= 0)] = 1   # AC由负转正时买入
        self.signals[(ac < 0) & (ac.shift(1) >= 0)] = -1  # AC由正转负时卖出