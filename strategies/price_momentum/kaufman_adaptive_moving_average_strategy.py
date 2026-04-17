"""
卡夫曼自适应移动平均线策略 (KAMA)
根据市场波动性调整的移动平均线
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class KaufmanAdaptiveMovingAverageStrategy(BaseStrategy):
    """
    卡夫曼自适应移动平均线策略 (KAMA)
    根据市场波动性调整的移动平均线
    """
    
    def __init__(self, period=10, fast_period=2, slow_period=30, transaction_cost=0.001, position_size=1.0):
        super().__init__("KAMA Strategy", transaction_cost, indicator_short_name="KAMA", position_size=position_size)
        self.period = period
        self.fast_period = fast_period
        self.slow_period = slow_period
        
    def generate_signals(self):
        """
        生成KAMA交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算价格变化
        price_change = abs(self.data['close'] - self.data['close'].shift(self.period))
        
        # 计算波动性
        volatility = abs(self.data['close'] - self.data['close'].shift(1)).rolling(window=self.period).sum()
        
        # 计算效率比率 (ER)
        er = price_change / volatility
        er = er.fillna(0)
        
        # 计算平滑常数 (SC)
        fast_sc = 2 / (self.fast_period + 1)
        slow_sc = 2 / (self.slow_period + 1)
        sc = (er * (fast_sc - slow_sc) + slow_sc) ** 2
        
        # 计算KAMA
        kama = pd.Series(0, index=self.data.index)
        kama.iloc[self.period] = self.data['close'].iloc[self.period]
        
        for i in range(self.period + 1, len(self.data)):
            kama.iloc[i] = kama.iloc[i-1] + sc.iloc[i] * (self.data['close'].iloc[i] - kama.iloc[i-1])
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[self.data['close'] > kama] = 1   # 价格高于KAMA时买入
        self.signals[self.data['close'] < kama] = -1  # 价格低于KAMA时卖出