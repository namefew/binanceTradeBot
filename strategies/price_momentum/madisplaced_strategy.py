"""
位移移动平均线(MADisplaced)策略
根据研报：MADisplaced=REF(MA_CLOSE,M)
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class MADisplacedStrategy(BaseStrategy):
    """
    位移移动平均线(MADisplaced)策略
    根据研报：MADisplaced=REF(MA_CLOSE,M)
    """
    
    def __init__(self, n=20, m=10, transaction_cost=0.001, position_size=1.0):
        super().__init__("MADisplaced Strategy", transaction_cost, indicator_short_name="MADisplaced", position_size=position_size)
        self.n = n
        self.m = m
        
    def generate_signals(self):
        """
        生成MADisplaced交易信号
        当收盘价上穿/下穿MADisplaced时产生买入/卖出信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算移动平均线
        ma_close = self.data['close'].rolling(window=self.n).mean()
        
        # 计算位移移动平均线
        madisplaced = ma_close.shift(self.m)
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # 收盘价上穿MADisplaced时买入
        self.signals[(self.data['close'] > madisplaced) & (self.data['close'].shift(1) <= madisplaced.shift(1))] = 1
        # 收盘价下穿MADisplaced时卖出
        self.signals[(self.data['close'] < madisplaced) & (self.data['close'].shift(1) >= madisplaced.shift(1))] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)