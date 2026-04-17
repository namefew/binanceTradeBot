"""
艾达透视策略
基于布林带和EMA的策略
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class ElderRayStrategy(BaseStrategy):
    """
    艾达透视策略
    基于布林带和EMA的策略
    """
    
    def __init__(self, period=13, transaction_cost=0.001, position_size=1.0):
        super().__init__("Elder-Ray Strategy", transaction_cost, indicator_short_name="Elder-Ray", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成艾达透视交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有high, low, close列
        required_columns = ['high', 'low', 'close']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算EMA
        ema = self.data['close'].ewm(span=self.period).mean()
        
        # 计算牛市力量和熊市力量
        bull_power = self.data['high'] - ema
        bear_power = self.data['low'] - ema
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[(bull_power > 0) & (bull_power > bear_power)] = 1   # 牛市力量强时买入
        self.signals[(bear_power < 0) & (bear_power < bull_power)] = -1  # 熊市力量强时卖出