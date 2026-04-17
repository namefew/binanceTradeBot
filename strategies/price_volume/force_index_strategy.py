"""
力量指数策略 (Force Index)
衡量买卖力量的指标
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class ForceIndexStrategy(BaseStrategy):
    """
    力量指数策略 (Force Index)
    衡量买卖力量的指标
    """
    
    def __init__(self, period=13, transaction_cost=0.001, position_size=1.0):
        super().__init__("Force Index Strategy", transaction_cost, indicator_short_name="Force Index", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成力量指数交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close, volume列
        required_columns = ['close', 'volume']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算力量指数
        force_index = (self.data['close'] - self.data['close'].shift(1)) * self.data['volume']
        force_index_ema = force_index.ewm(span=self.period).mean()
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[force_index_ema > 0] = 1   # 力量指数为正时买入
        self.signals[force_index_ema < 0] = -1  # 力量指数为负时卖出