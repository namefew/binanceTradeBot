"""
江恩高低点策略
基于威廉·江恩理论的趋势跟踪策略
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class GannHiLoStrategy(BaseStrategy):
    """
    江恩高低点策略
    基于威廉·江恩理论的趋势跟踪策略
    """
    
    def __init__(self, period=3, transaction_cost=0.001, position_size=1.0):
        super().__init__("Gann HiLo Strategy", transaction_cost, indicator_short_name="Gann HiLo", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成江恩高低点交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有high, low列
        required_columns = ['high', 'low']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算HiLo指标
        hilo_high = self.data['high'].rolling(window=self.period).max()
        hilo_low = self.data['low'].rolling(window=self.period).min()
        
        # 计算信号线（简单移动平均）
        signal_line = ((hilo_high + hilo_low) / 2).rolling(window=self.period).mean()
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[(hilo_high > signal_line) & (hilo_high.shift(1) <= signal_line.shift(1))] = 1   # 上穿时买入
        self.signals[(hilo_low < signal_line) & (hilo_low.shift(1) >= signal_line.shift(1))] = -1   # 下穿时卖出