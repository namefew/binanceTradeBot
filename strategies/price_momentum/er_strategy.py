"""
Elder Ray Index(ER)策略
根据研报，BullPower=HIGH-EMA(CLOSE,N)，BearPower=LOW-EMA(CLOSE,N)，N=20
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class ERStrategy(BaseStrategy):
    """
    Elder Ray Index(ER)策略
    根据研报，BullPower=HIGH-EMA(CLOSE,N)，BearPower=LOW-EMA(CLOSE,N)，N=20
    """
    
    def __init__(self, n=20, transaction_cost=0.001, position_size=1.0):
        super().__init__("ER Strategy", transaction_cost, indicator_short_name="ER", position_size=position_size)
        self.n = n
        
    def generate_signals(self):
        """
        生成ER交易信号
        当BearPower上穿0时买入，当BullPower下穿0时卖出
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有必要的列
        required_columns = ['high', 'low', 'close']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算EMA
        ema = self.data['close'].ewm(span=self.n).mean()
        
        # 计算BullPower和BearPower
        bull_power = self.data['high'] - ema  # 牛力 = 最高价 - EMA
        bear_power = self.data['low'] - ema   # 熊力 = 最低价 - EMA
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # BearPower上穿0时买入
        self.signals[(bear_power > 0) & (bear_power.shift(1) <= 0)] = 1
        # BullPower下穿0时卖出
        self.signals[(bull_power < 0) & (bull_power.shift(1) >= 0)] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)