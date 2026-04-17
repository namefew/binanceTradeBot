"""
简单移动平均线策略 (VMA - Volume Moving Average)
根据研报：PRICE=(HIGH+LOW+OPEN+CLOSE)/4，VMA=MA(PRICE,N)
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy

class VMAStrategy(BaseStrategy):
    """
    简单移动平均线策略 (VMA - Volume Moving Average)
    根据研报：PRICE=(HIGH+LOW+OPEN+CLOSE)/4，VMA=MA(PRICE,N)
    """
    
    def __init__(self, n=20, transaction_cost=0.001, position_size=1.0):
        super().__init__("VMA Strategy", transaction_cost, indicator_short_name="VMA", position_size=position_size)
        self.n = n
        
    def generate_signals(self):
        """
        生成VMA交易信号
        当PRICE上穿/下穿VMA时产生买入/卖出信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有必要的列
        required_columns = ['close', 'high', 'low', 'open']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算价格
        price = (self.data['high'] + self.data['low'] + self.data['open'] + self.data['close']) / 4
        
        # 计算VMA
        vma = price.rolling(window=self.n).mean()
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # PRICE上穿VMA时买入
        self.signals[(price > vma) & (price.shift(1) <= vma.shift(1))] = 1
        # PRICE下穿VMA时卖出
        self.signals[(price < vma) & (price.shift(1) >= vma.shift(1))] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)