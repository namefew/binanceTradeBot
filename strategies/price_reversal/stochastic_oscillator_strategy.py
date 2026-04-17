"""
随机振荡器策略
通过比较收盘价与一定时期内的价格范围来衡量动量
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class StochasticOscillatorStrategy(BaseStrategy):
    """
    随机振荡器策略
    通过比较收盘价与一定时期内的价格范围来衡量动量
    """
    
    def __init__(self, k_period=14, d_period=3, overbought=80, oversold=20, transaction_cost=0.001, position_size=1.0):
        super().__init__("Stochastic Oscillator Strategy", transaction_cost, indicator_short_name="Stochastic", position_size=position_size)
        self.k_period = k_period
        self.d_period = d_period
        self.overbought = overbought
        self.oversold = oversold
        
    def generate_signals(self):
        """
        生成随机振荡器交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有必要的列
        required_columns = ['high', 'low', 'close']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算%K值
        low_min = self.data['low'].rolling(window=self.k_period).min()
        high_max = self.data['high'].rolling(window=self.k_period).max()
        k = 100 * ((self.data['close'] - low_min) / (high_max - low_min))
        
        # 计算%D值（%K的移动平均）
        d = k.rolling(window=self.d_period).mean()
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # %K线上穿%D线且在超卖区时买入
        self.signals[(k > d) & (k.shift(1) <= d.shift(1)) & (k < self.oversold)] = 1
        # %K线下穿%D线且在超买区时卖出
        self.signals[(k < d) & (k.shift(1) >= d.shift(1)) & (k > self.overbought)] = -1