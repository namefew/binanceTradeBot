"""
零滞后指数移动平均线策略 (ZLEMA)
减少传统EMA滞后性的改进版本
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class ZeroLagExponentialMovingAverageStrategy(BaseStrategy):
    """
    零滞后指数移动平均线策略 (ZLEMA)
    减少传统EMA滞后性的改进版本
    """
    
    def __init__(self, period=20, transaction_cost=0.001, position_size=1.0):
        super().__init__("ZLEMA Strategy", transaction_cost, indicator_short_name="ZLEMA", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成ZLEMA交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算滞后值
        lag = (self.period - 1) // 2
        
        # 计算修正的价格序列
        price_adjusted = 2 * self.data['close'] - self.data['close'].shift(lag)
        
        # 计算ZLEMA
        zlema = price_adjusted.ewm(span=self.period).mean()
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[self.data['close'] > zlema] = 1   # 价格高于ZLEMA时买入
        self.signals[self.data['close'] < zlema] = -1  # 价格低于ZLEMA时卖出