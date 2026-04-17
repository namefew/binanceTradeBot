"""
海里相对指数策略 (Kairi Relative Index)
根据研报：衡量价格与移动平均线偏离程度的指标
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class KairiRelativeIndexStrategy(BaseStrategy):
    """
    海里相对指数策略 (Kairi Relative Index)
    根据研报：衡量价格与移动平均线偏离程度的指标
    """
    
    def __init__(self, period=14, transaction_cost=0.001, position_size=1.0):
        super().__init__("Kairi Relative Index Strategy", transaction_cost, indicator_short_name="KRI", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成Kairi Relative Index交易信号
        当指标上穿/下穿阈值时产生交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算SMA
        sma = self.data['close'].rolling(window=self.period).mean()
        
        # 计算KRI
        kri = (self.data['close'] - sma) / sma * 100
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # KRI下穿-3时买入
        self.signals[(kri < -3) & (kri.shift(1) >= -3)] = 1
        # KRI上穿3时卖出
        self.signals[(kri > 3) & (kri.shift(1) <= 3)] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)