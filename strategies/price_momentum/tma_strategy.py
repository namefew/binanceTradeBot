"""
三重移动平均线策略 (Triple Moving Average)
根据研报：TMA=MA(CLOSE_MA,N)，其中CLOSE_MA=MA(CLOSE,N)
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy

class TMAStrategy(BaseStrategy):
    """
    三重移动平均线策略 (Triple Moving Average)
    根据研报：TMA=MA(CLOSE_MA,N)，其中CLOSE_MA=MA(CLOSE,N)
    """
    
    def __init__(self, n=20, transaction_cost=0.001, position_size=1.0):
        super().__init__("TMA Strategy", transaction_cost, indicator_short_name="TMA", position_size=position_size)
        self.n = n
        
    def generate_signals(self):
        """
        生成TMA交易信号
        当收盘价上穿/下穿TMA时产生买入/卖出信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算双重移动平均线
        close_ma = self.data['close'].rolling(window=self.n).mean()
        tma = close_ma.rolling(window=self.n).mean()
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # 收盘价上穿TMA时买入
        self.signals[(self.data['close'] > tma) & (self.data['close'].shift(1) <= tma.shift(1))] = 1
        # 收盘价下穿TMA时卖出
        self.signals[(self.data['close'] < tma) & (self.data['close'].shift(1) >= tma.shift(1))] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)