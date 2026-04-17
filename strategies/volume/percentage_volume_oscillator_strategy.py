"""
成交量震荡指标策略 (PVO)
衡量成交量变化的指标
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class PercentageVolumeOscillatorStrategy(BaseStrategy):
    """
    成交量震荡指标策略 (PVO)
    衡量成交量变化的指标
    """
    
    def __init__(self, fast_period=12, slow_period=26, signal_period=9, transaction_cost=0.001, position_size=1.0):
        super().__init__("Percentage Volume Oscillator Strategy", transaction_cost, indicator_short_name="PVO", position_size=position_size)
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        
    def generate_signals(self):
        """
        生成成交量震荡指标交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有volume列
        if 'volume' not in self.data.columns:
            raise ValueError("数据中缺少volume列")
            
        # 计算PVO线
        fast_ema = self.data['volume'].ewm(span=self.fast_period).mean()
        slow_ema = self.data['volume'].ewm(span=self.slow_period).mean()
        pvo = ((fast_ema - slow_ema) / slow_ema) * 100
        
        # 计算信号线
        signal = pvo.ewm(span=self.signal_period).mean()
        
        # 计算柱状图
        histogram = pvo - signal
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[histogram > 0] = 1   # 柱状图为正时买入
        self.signals[histogram < 0] = -1  # 柱状图为负时卖出