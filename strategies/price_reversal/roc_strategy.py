"""
变化率指标策略 (Rate of Change)
测量价格变化的百分比
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class ROCStrategy(BaseStrategy):
    """
    变化率指标策略 (Rate of Change)
    测量价格变化的百分比
    """
    
    def __init__(self, period=12, threshold=0, transaction_cost=0.001, position_size=1.0):
        super().__init__("Rate of Change Strategy", transaction_cost, indicator_short_name="ROC", position_size=position_size)
        self.period = period
        self.threshold = threshold
        
    def generate_signals(self):
        """
        生成ROC交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算ROC
        roc = self.data['close'].pct_change(periods=self.period) * 100
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[roc > self.threshold] = 1   # ROC为正时买入
        self.signals[roc < self.threshold] = -1  # ROC为负时卖出