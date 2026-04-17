"""
典型价格策略 (Typical Price)
根据研报：TYP=(CLOSE+HIGH+LOW)/3
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy

class TYPStrategy(BaseStrategy):
    """
    典型价格策略 (Typical Price)
    根据研报：TYP=(CLOSE+HIGH+LOW)/3
    """
    
    def __init__(self, n1=10, n2=30, transaction_cost=0.001, position_size=1.0):
        super().__init__("TYP Strategy", transaction_cost, indicator_short_name="TYP", position_size=position_size)
        self.n1 = n1
        self.n2 = n2
        
    def generate_signals(self):
        """
        生成TYP交易信号
        当TYPMA1上穿/下穿TYPMA2时产生买入/卖出信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有必要的列
        required_columns = ['close', 'high', 'low']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算典型价格
        typ = (self.data['close'] + self.data['high'] + self.data['low']) / 3
        
        # 计算两个EMA
        typma1 = typ.ewm(span=self.n1).mean()
        typma2 = typ.ewm(span=self.n2).mean()
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # TYPMA1上穿TYPMA2时买入
        self.signals[(typma1 > typma2) & (typma1.shift(1) <= typma2.shift(1))] = 1
        # TYPMA1下穿TYPMA2时卖出
        self.signals[(typma1 < typma2) & (typma1.shift(1) >= typma2.shift(1))] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)