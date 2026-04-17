"""
KDJD策略 (KDJ变形)
根据研报计算方法实现
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy

class KDJDStrategy(BaseStrategy):
    """
    KDJD策略 (KDJ变形)
    根据研报计算方法实现
    """
    
    def __init__(self, n=20, m=60, overbought=70, oversold=30, transaction_cost=0.001, position_size=1.0):
        super().__init__("KDJD Strategy", transaction_cost, indicator_short_name="KDJD", position_size=position_size)
        self.n = n
        self.m = m
        self.overbought = overbought
        self.oversold = oversold
        
    def generate_signals(self):
        """
        生成KDJD交易信号
        当D值上穿30/下穿70时产生买入/卖出信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有必要的列
        required_columns = ['close', 'high', 'low']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算最低价和最高价
        low_n = self.data['low'].rolling(window=self.n).min()
        high_n = self.data['high'].rolling(window=self.n).max()
        
        # 计算Stochastics
        stochastics = (self.data['close'] - low_n) / (high_n - low_n) * 100
        
        # 计算Stochastics的最低值和最高值
        stochastics_low = stochastics.rolling(window=self.m).min()
        stochastics_high = stochastics.rolling(window=self.m).max()
        
        # 计算Stochastics_DOUBLE
        stochastics_double = (stochastics - stochastics_low) / (stochastics_high - stochastics_low) * 100
        
        # 计算K值和D值
        k = stochastics_double.ewm(alpha=1/3).mean()
        d = k.ewm(alpha=1/3).mean()
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # D值上穿30时买入
        self.signals[(d > self.oversold) & (d.shift(1) <= self.oversold)] = 1
        # D值下穿70时卖出
        self.signals[(d < self.overbought) & (d.shift(1) >= self.overbought)] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)