"""
阿隆指标策略 (Aroon)
识别趋势的开始和结束
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class AroonStrategy(BaseStrategy):
    """
    阿隆指标策略 (Aroon)
    识别趋势的开始和结束
    """
    
    def __init__(self, period=25, transaction_cost=0.001, position_size=1.0):
        super().__init__("Aroon Strategy", transaction_cost, indicator_short_name="Aroon", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成阿隆指标交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有high, low列
        required_columns = ['high', 'low']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算Aroon Up和Aroon Down
        aroon_up = pd.Series(0, index=self.data.index)
        aroon_down = pd.Series(0, index=self.data.index)
        
        for i in range(self.period, len(self.data)):
            high_window = self.data['high'].iloc[i-self.period:i+1]
            low_window = self.data['low'].iloc[i-self.period:i+1]
            
            aroon_up.iloc[i] = ((self.period - high_window.argmax()) / self.period) * 100
            aroon_down.iloc[i] = ((self.period - low_window.argmin()) / self.period) * 100
            
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[(aroon_up > aroon_down) & (aroon_up.shift(1) <= aroon_down.shift(1))] = 1   # 阿隆上涨破阿隆下时买入
        self.signals[(aroon_up < aroon_down) & (aroon_up.shift(1) >= aroon_down.shift(1))] = -1  # 阿隆涨下破阿隆上时卖出