"""
Schaff趋势周期策略
结合了MACD和随机指标的策略
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class SchaffTrendCycleStrategy(BaseStrategy):
    """
    Schaff趋势周期策略
    结合了MACD和随机指标的策略
    """
    
    def __init__(self, period=10, fast_period=23, slow_period=50, transaction_cost=0.001, position_size=1.0):
        super().__init__("Schaff Trend Cycle Strategy", transaction_cost, indicator_short_name="STC", position_size=position_size)
        self.period = period
        self.fast_period = fast_period
        self.slow_period = slow_period
        
    def generate_signals(self):
        """
        生成STC交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算EMA
        ema_fast = self.data['close'].ewm(span=self.fast_period).mean()
        ema_slow = self.data['close'].ewm(span=self.slow_period).mean()
        
        # 计算MACD
        macd = ema_fast - ema_slow
        
        # 计算MACD的最高值和最低值
        macd_min = macd.rolling(window=self.period).min()
        macd_max = macd.rolling(window=self.period).max()
        
        # 计算%K值
        stok = 100 * (macd - macd_min) / (macd_max - macd_min)
        
        # 计算%D值
        stod = stok.rolling(window=self.period).mean()
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[stod > stod.shift(1)] = 1   # %D上升时买入
        self.signals[stod < stod.shift(1)] = -1  # %D下降时卖出