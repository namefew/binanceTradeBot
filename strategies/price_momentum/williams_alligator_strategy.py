"""
威廉鳄鱼指标策略
由三条不同周期和偏移的SMMA组成
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class WilliamsAlligatorStrategy(BaseStrategy):
    """
    威廉鳄鱼指标策略
    由三条不同周期和偏移的SMMA组成
    """
    
    def __init__(self, jaw_period=13, teeth_period=8, lips_period=5, transaction_cost=0.001, position_size=1.0):
        super().__init__("Williams Alligator Strategy", transaction_cost, indicator_short_name="Williams Alligator", position_size=position_size)
        self.jaw_period = jaw_period
        self.teeth_period = teeth_period
        self.lips_period = lips_period
        
    def generate_signals(self):
        """
        生成威廉鳄鱼指标交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算SMMA（平滑移动平均线）
        def smma(series, period):
            smma_values = pd.Series(0, index=series.index)
            smma_values.iloc[period-1] = series.iloc[:period].mean()
            for i in range(period, len(series)):
                smma_values.iloc[i] = (smma_values.iloc[i-1] * (period - 1) + series.iloc[i]) / period
            return smma_values
        
        # 计算鳄鱼的颚、牙齿和嘴唇
        jaw = smma((self.data['high'] + self.data['low']) / 2, self.jaw_period).shift(8)
        teeth = smma((self.data['high'] + self.data['low']) / 2, self.teeth_period).shift(5)
        lips = smma((self.data['high'] + self.data['low']) / 2, self.lips_period).shift(3)
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # 当嘴唇上穿牙齿和颚时买入
        self.signals[(lips > teeth) & (lips > jaw) & (lips.shift(1) <= teeth.shift(1))] = 1
        # 当嘴唇下穿牙齿和颚时卖出
        self.signals[(lips < teeth) & (lips < jaw) & (lips.shift(1) >= teeth.shift(1))] = -1