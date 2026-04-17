"""
斐波那契回撤策略
基于斐波那契比率的支撑位和阻力位策略
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class FibonacciRetracementStrategy(BaseStrategy):
    """
    斐波那契回撤策略
    基于斐波那契比率的支撑位和阻力位策略
    """
    
    def __init__(self, period=20, transaction_cost=0.001, position_size=1.0):
        super().__init__("Fibonacci Retracement Strategy", transaction_cost, indicator_short_name="Fibonacci", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成斐波那契回撤交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有high, low, close列
        required_columns = ['high', 'low', 'close']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算最近的最高价和最低价
        recent_high = self.data['high'].rolling(window=self.period).max()
        recent_low = self.data['low'].rolling(window=self.period).min()
        
        # 计算斐波那契回撤位 (23.6%, 38.2%, 50%, 61.8%)
        diff = recent_high - recent_low
        fib_236 = recent_low + diff * 0.236
        fib_382 = recent_low + diff * 0.382
        fib_50 = recent_low + diff * 0.5
        fib_618 = recent_low + diff * 0.618
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # 价格上穿斐波那契支撑位时买入
        self.signals[(self.data['close'] > fib_382) & (self.data['close'].shift(1) <= fib_382.shift(1))] = 1
        # 价格下穿斐波那契阻力位时卖出
        self.signals[(self.data['close'] < fib_618) & (self.data['close'].shift(1) >= fib_618.shift(1))] = -1