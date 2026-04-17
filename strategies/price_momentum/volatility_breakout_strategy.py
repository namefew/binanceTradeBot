"""
波动率突破策略
当价格突破近期价格区间的一定比例时进行交易
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class VolatilityBreakoutStrategy(BaseStrategy):
    """
    波动率突破策略
    当价格突破近期价格区间的一定比例时进行交易
    """
    
    def __init__(self, window=20, multiplier=1.5, transaction_cost=0.001, position_size=1.0):
        super().__init__("Volatility Breakout Strategy", transaction_cost, indicator_short_name="Volatility Breakout", position_size=position_size)
        self.window = window
        self.multiplier = multiplier
        
    def generate_signals(self):
        """
        生成波动率突破交易信号
        当价格上涨突破近期最高价时买入，下跌突破近期最低价时卖出
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有high, low, close列
        required_columns = ['high', 'low', 'close']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算近期最高价和最低价
        recent_high = self.data['high'].rolling(window=self.window).max()
        recent_low = self.data['low'].rolling(window=self.window).min()
        
        # 计算价格区间的一定比例
        price_range = recent_high - recent_low
        breakout_range = price_range * self.multiplier / 100
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # 当收盘价突破近期最高价加上突破范围时买入
        self.signals[self.data['close'] > (recent_high + breakout_range)] = 1
        # 当收盘价跌破近期最低价减去突破范围时卖出
        self.signals[self.data['close'] < (recent_low - breakout_range)] = -1