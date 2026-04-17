"""
Ehlers屋顶滤波器策略
用于消除高频噪音和超低频趋势
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class EhlersRoofingFilterStrategy(BaseStrategy):
    """
    Ehlers屋顶滤波器策略
    用于消除高频噪音和超低频趋势
    """
    
    def __init__(self, period=20, transaction_cost=0.001, position_size=1.0):
        super().__init__("Ehlers Roofing Filter Strategy", transaction_cost, indicator_short_name="Ehlers Roofing Filter", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成屋顶滤波器交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算HP（高通滤波器）参数
        hp_period = 48
        alpha_hp = (np.cos(0.707 * 3.14159 * 2 / hp_period) + np.sin(0.707 * 3.14159 * 2 / hp_period) - 1) / np.cos(0.707 * 3.14159 * 2 / hp_period)
        
        # 计算高通滤波器
        hp = pd.Series(0, index=self.data.index)
        for i in range(2, len(self.data)):
            hp.iloc[i] = (1 - alpha_hp / 2) ** 2 * (self.data['close'].iloc[i] - 2 * self.data['close'].iloc[i-1] + self.data['close'].iloc[i-2]) + \
                         2 * (1 - alpha_hp) * hp.iloc[i-1] - (1 - alpha_hp) ** 2 * hp.iloc[i-2]
        
        # 计算LP（低通滤波器）参数
        alpha_lp = 2 / (self.period + 1)
        
        # 计算低通滤波器（超级平滑器）
        a1 = np.exp(-1.414 * 3.14159 / self.period)
        b1 = 2 * a1 * np.cos(1.414 * 3.14159 / self.period)
        c2 = b1
        c3 = -a1 * a1
        c1 = 1 - c2 - c3
        
        rf = pd.Series(0, index=self.data.index)
        for i in range(2, len(hp)):
            rf.iloc[i] = c1 * (hp.iloc[i] + hp.iloc[i-1]) / 2 + c2 * rf.iloc[i-1] + c3 * rf.iloc[i-2]
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[(rf > rf.shift(1)) & (rf.shift(1) <= rf.shift(2))] = 1   # 趋势向上时买入
        self.signals[(rf < rf.shift(1)) & (rf.shift(1) >= rf.shift(2))] = -1  # 趋势向下时卖出