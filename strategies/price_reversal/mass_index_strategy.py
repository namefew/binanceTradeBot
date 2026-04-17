"""
质量指数策略 (Mass Index)
用于预测趋势反转的指标
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class MassIndexStrategy(BaseStrategy):
    """
    质量指数策略 (Mass Index)
    用于预测趋势反转的指标
    """
    
    def __init__(self, period=9, threshold=27, transaction_cost=0.001, position_size=1.0):
        super().__init__("Mass Index Strategy", transaction_cost, indicator_short_name="Mass Index", position_size=position_size)
        self.period = period
        self.threshold = threshold
        
    def generate_signals(self):
        """
        生成质量指数交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有high, low列
        required_columns = ['high', 'low']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算价格范围
        range_series = self.data['high'] - self.data['low']
        
        # 计算双EMA比率
        ema1 = range_series.ewm(span=self.period).mean()
        ema2 = ema1.ewm(span=self.period).mean()
        ratio = ema1 / ema2
        
        # 计算质量指数
        mass_index = ratio.rolling(window=25).sum()
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # 当质量指数从低于27上升到高于27时买入
        self.signals[(mass_index > self.threshold) & (mass_index.shift(1) <= self.threshold)] = 1
        # 当质量指数从高于27下降到低于27时卖出
        self.signals[(mass_index < self.threshold) & (mass_index.shift(1) >= self.threshold)] = -1