"""
傅里叶变换策略
使用傅里叶变换识别价格周期性
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy
from strategies.technical_indicators import TechnicalIndicators

class FourierTransformStrategy(BaseStrategy):
    """
    傅里叶变换策略
    使用傅里叶变换识别价格周期性
    """
    
    def __init__(self, period=20, transaction_cost=0.001, position_size=1.0):
        super().__init__("Fourier Transform Strategy", transaction_cost, indicator_short_name="Fourier Transform", position_size=position_size)
        self.period = period
    
    def generate_signals(self):
        """
        生成交易信号
        """
        # 傅里叶变换分析 (简化版本)
        price = self.data['close']
        
        # 计算价格变化
        price_diff = price.diff()
        
        # 使用移动窗口计算周期性强度
        cycle_strength = price_diff.rolling(window=self.period).apply(
            lambda x: np.abs(np.fft.fft(x))[1:10].mean() if len(x) == self.period and len(x.dropna()) == self.period else 0, 
            raw=False
        )
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        
        # 当周期强度增加时买入
        buy_condition = cycle_strength > cycle_strength.shift(1)
        # 当周期强度减少时卖出
        sell_condition = cycle_strength < cycle_strength.shift(1)
        
        self.signals[buy_condition] = 1
        self.signals[sell_condition] = -1