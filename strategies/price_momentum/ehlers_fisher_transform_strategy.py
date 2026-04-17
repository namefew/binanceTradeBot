"""
Ehlers Fisher变换策略
用于将价格数据转换为高斯分布
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class EhlersFisherTransformStrategy(BaseStrategy):
    """
    Ehlers Fisher变换策略
    用于将价格数据转换为高斯分布
    """
    
    def __init__(self, period=10, transaction_cost=0.001, position_size=1.0):
        super().__init__("Ehlers Fisher Transform Strategy", transaction_cost, indicator_short_name="Ehlers Fisher Transform", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成Fisher变换交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有high, low列
        required_columns = ['high', 'low']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算中间值
        median_price = (self.data['high'] + self.data['low']) / 2
        max_high = median_price.rolling(window=self.period).max()
        min_low = median_price.rolling(window=self.period).min()
        
        # 计算值域
        value = 2 * ((median_price - min_low) / (max_high - min_low) - 0.5)
        value = value.clip(-0.999, 0.999)  # 限制范围以避免无穷大
        
        # 计算Fisher变换
        fisher = pd.Series(0, index=self.data.index)
        for i in range(1, len(value)):
            fisher.iloc[i] = 0.5 * np.log((1 + value.iloc[i]) / (1 - value.iloc[i]))
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[(fisher > fisher.shift(1)) & (fisher.shift(1) <= fisher.shift(2))] = 1   # Fisher变换趋势向上时买入
        self.signals[(fisher < fisher.shift(1)) & (fisher.shift(1) >= fisher.shift(2))] = -1  # Fisher变换趋势向下时卖出