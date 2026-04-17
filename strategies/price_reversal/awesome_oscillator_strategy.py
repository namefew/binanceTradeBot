"""
AO策略 (Awesome Oscillator)
用于识别市场动量的变化
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class AwesomeOscillatorStrategy(BaseStrategy):
    """
    AO策略 (Awesome Oscillator)
    用于识别市场动量的变化
    """
    
    def __init__(self, fast_period=5, slow_period=34, transaction_cost=0.001, position_size=1.0):
        super().__init__("Awesome Oscillator Strategy", transaction_cost, indicator_short_name="AO", position_size=position_size)
        self.fast_period = fast_period
        self.slow_period = slow_period
        
    def generate_signals(self):
        """
        生成AO交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有high, low列
        required_columns = ['high', 'low']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算中点
        midpoint = (self.data['high'] + self.data['low']) / 2
        
        # 计算快速和慢速移动平均线
        fast_sma = midpoint.rolling(window=self.fast_period).mean()
        slow_sma = midpoint.rolling(window=self.slow_period).mean()
        
        # 计算AO
        ao = fast_sma - slow_sma
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[(ao > 0) & (ao.shift(1) <= 0)] = 1   # AO由负转正时买入
        self.signals[(ao < 0) & (ao.shift(1) >= 0)] = -1  # AO由正转负时卖出