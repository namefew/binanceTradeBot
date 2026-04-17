"""
Ehlers带通滤波器策略
用于识别特定周期的周期性波动
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class EhlersBandPassFilterStrategy(BaseStrategy):
    """
    Ehlers带通滤波器策略
    用于识别特定周期的周期性波动
    """
    
    def __init__(self, period=20, delta=0.1, transaction_cost=0.001, position_size=1.0):
        super().__init__("Ehlers Band Pass Filter Strategy", transaction_cost, indicator_short_name="Ehlers Band Pass Filter", position_size=position_size)
        self.period = period
        self.delta = delta
        
    def generate_signals(self):
        """
        生成带通滤波器交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算滤波参数
        beta = np.cos(2 * 3.14159 / self.period)
        gamma = 1 / np.cos(2 * 3.14159 * self.delta / self.period)
        alpha = gamma - np.sqrt(gamma * gamma - 1)
        
        # 计算带通滤波器
        bp = pd.Series(0, index=self.data.index)
        peak = pd.Series(0, index=self.data.index)
        
        for i in range(2, len(self.data)):
            bp.iloc[i] = 0.5 * (1 - alpha) * (self.data['close'].iloc[i] - self.data['close'].iloc[i-2]) + \
                         beta * (1 + alpha) * bp.iloc[i-1] - alpha * bp.iloc[i-2]
            peak.iloc[i] = 0.991 * peak.iloc[i-1] + 0.009 * abs(bp.iloc[i])
        
        # 计算归一化带通滤波器
        bp_normalized = bp / peak
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[(bp_normalized > 0) & (bp_normalized.shift(1) <= 0)] = 1   # 带通滤波器上穿零轴时买入
        self.signals[(bp_normalized < 0) & (bp_normalized.shift(1) >= 0)] = -1  # 带通滤波器下穿零轴时卖出