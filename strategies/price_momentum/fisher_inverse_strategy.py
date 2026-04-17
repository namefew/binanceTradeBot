"""
费舍尔逆变换策略 (Fisher Inverse)
根据研报：对价格进行费舍尔逆变换以识别转折点
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class FisherInverseStrategy(BaseStrategy):
    """
    费舍尔逆变换策略 (Fisher Inverse)
    根据研报：对价格进行费舍尔逆变换以识别转折点
    """
    
    def __init__(self, period=10, transaction_cost=0.001, position_size=1.0):
        super().__init__("Fisher Inverse Strategy", transaction_cost, indicator_short_name="Fisher Inverse", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成Fisher Inverse交易信号
        当指标发生转折时产生交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有必要的列
        required_columns = ['high', 'low']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算价格中点
        midpoint = (self.data['high'] + self.data['low']) / 2
        
        # 计算最高价和最低价的滚动最大值和最小值
        max_midpoint = midpoint.rolling(window=self.period).max()
        min_midpoint = midpoint.rolling(window=self.period).min()
        
        # 计算归一化值
        range_val = max_midpoint - min_midpoint
        normalized = pd.Series(np.where(range_val != 0, 
                                      (midpoint - min_midpoint) / range_val * 0.999, 
                                      0), index=self.data.index)
        normalized = np.clip(normalized, -0.999, 0.999)
        
        # 计算Fisher逆变换
        fisher_inverse = 0.5 * np.log((1 + normalized) / (1 - normalized))
        fisher_signal = fisher_inverse.shift(1)
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # Fisher逆变换上穿信号线时买入
        self.signals[(fisher_inverse > fisher_signal) & (fisher_inverse.shift(1) <= fisher_signal.shift(1))] = 1
        # Fisher逆变换下穿信号线时卖出
        self.signals[(fisher_inverse < fisher_signal) & (fisher_inverse.shift(1) >= fisher_signal.shift(1))] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)