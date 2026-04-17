"""
动量策略
当股票价格表现出持续上涨或下跌趋势时，认为这种趋势会继续
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class MomentumStrategy(BaseStrategy):
    """
    动量策略
    当股票价格表现出持续上涨或下跌趋势时，认为这种趋势会继续
    """
    
    def __init__(self, window=90, threshold=0.05, transaction_cost=0.001, position_size=1.0):
        super().__init__("Momentum Strategy", transaction_cost, indicator_short_name="Momentum", position_size=position_size)
        self.window = window
        self.threshold = threshold
        
    def generate_signals(self):
        """
        生成动量交易信号
        当价格涨幅超过阈值时买入，跌幅超过阈值时卖出
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算动量（相对于window天前的价格变化）
        momentum = self.data['close'] / self.data['close'].shift(self.window) - 1
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[momentum > self.threshold] = 1     # 动量为正且超过阈值时买入
        self.signals[momentum < -self.threshold] = -1   # 动量为负且超过阈值时卖出