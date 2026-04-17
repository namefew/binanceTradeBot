"""
成交量加权平均价格策略 (VWAP)
衡量交易日平均价格的指标
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class VolumeWeightedAveragePriceStrategy(BaseStrategy):
    """
    成交量加权平均价格策略 (VWAP)
    衡量交易日平均价格的指标
    """
    
    def __init__(self, period=20, transaction_cost=0.001, position_size=1.0):
        super().__init__("VWAP Strategy", transaction_cost, indicator_short_name="VWAP", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成VWAP交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有high, low, close, volume列
        required_columns = ['high', 'low', 'close', 'volume']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算典型价格
        typical_price = (self.data['high'] + self.data['low'] + self.data['close']) / 3
        
        # 计算VWAP
        vwap = (typical_price * self.data['volume']).rolling(window=self.period).sum() / self.data['volume'].rolling(window=self.period).sum()
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[self.data['close'] > vwap] = 1   # 价格高于VWAP时买入
        self.signals[self.data['close'] < vwap] = -1  # 价格低于VWAP时卖出