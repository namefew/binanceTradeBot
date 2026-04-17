"""
均值回归策略
当价格偏离其均值一定程度时，预期价格会回归均值
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class MeanReversionStrategy(BaseStrategy):
    """
    均值回归策略
    当价格偏离其均值一定程度时，预期价格会回归均值
    """
    
    def __init__(self, window=20, z_score_threshold=1.5, transaction_cost=0.001, position_size=1.0):
        super().__init__("Mean Reversion Strategy", transaction_cost, indicator_short_name="Mean Reversion", position_size=position_size)
        self.window = window
        self.z_score_threshold = z_score_threshold
        
    def generate_signals(self):
        """
        生成均值回归交易信号
        当z-score大于阈值时卖出，小于负阈值时买入
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算移动平均和标准差
        rolling_mean = self.data['close'].rolling(window=self.window).mean()
        rolling_std = self.data['close'].rolling(window=self.window).std()
        
        # 计算z-score
        z_score = (self.data['close'] - rolling_mean) / rolling_std
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[z_score < -self.z_score_threshold] = 1   # 价格低于均值时买入
        self.signals[z_score > self.z_score_threshold] = -1   # 价格高于均值时卖出