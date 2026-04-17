"""
鳄鱼振荡器策略
基于鳄鱼指标的振荡器
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class GatorOscillatorStrategy(BaseStrategy):
    """
    鳄鱼振荡器策略
    基于鳄鱼指标的振荡器
    """
    
    def __init__(self, transaction_cost=0.001, position_size=1.0):
        super().__init__("Gator Oscillator Strategy", transaction_cost, indicator_short_name="Gator Oscillator", position_size=position_size)
        
    def generate_signals(self):
        """
        生成鳄鱼振荡器交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有high, low列
        required_columns = ['high', 'low']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算SMMA（平滑移动平均线）
        def smma(series, period):
            smma_values = pd.Series(0, index=series.index)
            smma_values.iloc[period-1] = series.iloc[:period].mean()
            for i in range(period, len(series)):
                smma_values.iloc[i] = (smma_values.iloc[i-1] * (period - 1) + series.iloc[i]) / period
            return smma_values
        
        # 计算鳄鱼的颚、牙齿和嘴唇
        jaw = smma((self.data['high'] + self.data['low']) / 2, 13).shift(8)
        teeth = smma((self.data['high'] + self.data['low']) / 2, 8).shift(5)
        lips = smma((self.data['high'] + self.data['low']) / 2, 5).shift(3)
        
        # 计算Gator Oscillator
        upper_gator = abs(jaw - teeth)
        lower_gator = -abs(teeth - lips)
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[(upper_gator > upper_gator.shift(1)) & (lower_gator < lower_gator.shift(1))] = 1   # 上颚张开且下颚闭合时买入
        self.signals[(upper_gator < upper_gator.shift(1)) & (lower_gator > lower_gator.shift(1))] = -1  # 上颚闭合且下颚张开时卖出