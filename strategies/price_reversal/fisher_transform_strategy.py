"""
Fisher变换策略
用于识别价格趋势的极值点
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class FisherTransformStrategy(BaseStrategy):
    """
    Fisher变换策略
    用于识别价格趋势的极值点
    """
    
    def __init__(self, period=10, transaction_cost=0.001, position_size=1.0):
        super().__init__("Fisher Transform Strategy", transaction_cost, indicator_short_name="Fisher", position_size=position_size)
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
            
        # 计算价格范围
        price_range = self.data['high'] - self.data['low']
        mid_point = (self.data['high'] + self.data['low']) / 2
        
        # 计算最大值和最小值
        max_high = self.data['high'].rolling(window=self.period).max()
        min_low = self.data['low'].rolling(window=self.period).min()
        
        # 计算值域
        value = 2 * ((mid_point - min_low) / (max_high - min_low) - 0.5)
        value = value.clip(-0.9999, 0.9999)  # 限制范围以避免无穷大
        
        # 计算Fisher变换
        fisher = 0.5 * np.log((1 + value) / (1 - value))
        fisher_signal = fisher.shift(1)
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[(fisher > fisher_signal)] = 1   # Fisher上穿时买入
        self.signals[(fisher < fisher_signal)] = -1  # Fisher下穿时卖出