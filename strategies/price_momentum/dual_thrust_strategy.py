"""
Dual Thrust策略
一种开盘区间突破策略，根据前N日的价格范围来确定当日的买卖信号
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class DualThrustStrategy(BaseStrategy):
    """
    Dual Thrust策略
    一种开盘区间突破策略，根据前N日的价格范围来确定当日的买卖信号
    """
    
    def __init__(self, period=2, k1=0.7, k2=0.7, transaction_cost=0.001, position_size=1.0):
        super().__init__("Dual Thrust Strategy", transaction_cost, indicator_short_name="Dual Thrust", position_size=position_size)
        self.period = period
        self.k1 = k1
        self.k2 = k2
        
    def generate_signals(self):
        """
        生成Dual Thrust交易信号
        根据开盘区间突破来生成信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有open, high, low, close列
        required_columns = ['open', 'high', 'low', 'close']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算前N日的最高价、最低价和收盘价
        hh = self.data['high'].rolling(window=self.period).max()
        ll = self.data['low'].rolling(window=self.period).min()
        hc = self.data['close'].rolling(window=self.period).max()
        lc = self.data['close'].rolling(window=self.period).min()
        
        # 计算范围
        range1 = hh - ll
        range2 = hc - lc
        range_value = pd.concat([range1, range2], axis=1).max(axis=1)
        
        # 计算上下轨
        upper_track = self.data['open'] + self.k1 * range_value
        lower_track = self.data['open'] - self.k2 * range_value
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # 当价格突破上轨时买入
        self.signals[self.data['close'] > upper_track] = 1
        # 当价格跌破下轨时卖出
        self.signals[self.data['close'] < lower_track] = -1