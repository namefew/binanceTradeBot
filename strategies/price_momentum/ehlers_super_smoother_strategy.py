"""
Ehlers超级平滑器策略
用于减少噪音和滞后性的滤波器
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class EhlersSuperSmootherStrategy(BaseStrategy):
    """
    Ehlers超级平滑器策略
    用于减少噪音和滞后性的滤波器
    """
    
    def __init__(self, period=20, transaction_cost=0.001, position_size=1.0):
        super().__init__("Ehlers Super Smoother Strategy", transaction_cost, indicator_short_name="Ehlers Super Smoother", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成超级平滑器交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算滤波参数
        a1 = np.exp(-1.414 * 3.14159 / self.period)
        b1 = 2 * a1 * np.cos(1.414 * 3.14159 / self.period)
        c2 = b1
        c3 = -a1 * a1
        c1 = 1 - c2 - c3
        
        # 计算超级平滑器
        ssf = pd.Series(0, index=self.data.index)
        
        for i in range(2, len(self.data)):
            ssf.iloc[i] = c1 * (self.data['close'].iloc[i] + self.data['close'].iloc[i-1]) / 2 + \
                          c2 * ssf.iloc[i-1] + c3 * ssf.iloc[i-2]
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[(ssf > ssf.shift(1)) & (ssf.shift(1) <= ssf.shift(2))] = 1   # 趋势向上时买入
        self.signals[(ssf < ssf.shift(1)) & (ssf.shift(1) >= ssf.shift(2))] = -1  # 趋势向下时卖出