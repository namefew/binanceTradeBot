"""
赫斯特指数策略
用于判断时间序列的长期依赖性
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class HurstExponentStrategy(BaseStrategy):
    """
    赫斯特指数策略
    用于判断时间序列的长期依赖性
    """
    
    def __init__(self, period=20, transaction_cost=0.001, position_size=1.0):
        super().__init__("Hurst Exponent Strategy", transaction_cost, indicator_short_name="Hurst Exponent", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成赫斯特指数交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 简化的赫斯特指数计算（实际应用中需要更复杂的计算）
        # 这里使用简化的方法来估计趋势性
        returns = self.data['close'].pct_change()
        volatility = returns.rolling(window=self.period).std()
        long_volatility = returns.rolling(window=self.period*2).std()
        
        # 生成信号（简化版）
        hurst_ratio = long_volatility / volatility
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[hurst_ratio > 1] = 1   # 高赫斯特指数时买入（趋势性较强）
        self.signals[hurst_ratio < 1] = -1  # 低赫斯特指数时卖出（均值回归性较强）