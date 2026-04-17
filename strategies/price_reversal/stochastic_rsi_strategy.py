"""
随机RSI策略
将RSI指标再进行随机计算的指标
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class StochasticRSIStrategy(BaseStrategy):
    """
    随机RSI策略
    将RSI指标再进行随机计算的指标
    """
    
    def __init__(self, rsi_period=14, stoch_period=14, overbought=80, oversold=20, transaction_cost=0.001, position_size=1.0):
        super().__init__("Stochastic RSI Strategy", transaction_cost, indicator_short_name="Stochastic RSI", position_size=position_size)
        self.rsi_period = rsi_period
        self.stoch_period = stoch_period
        self.overbought = overbought
        self.oversold = oversold
        
    def generate_signals(self):
        """
        生成随机RSI交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算RSI
        delta = self.data['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=self.rsi_period).mean()
        avg_loss = loss.rolling(window=self.rsi_period).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        # 计算随机RSI
        rsi_min = rsi.rolling(window=self.stoch_period).min()
        rsi_max = rsi.rolling(window=self.stoch_period).max()
        stoch_rsi = 100 * (rsi - rsi_min) / (rsi_max - rsi_min)
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[stoch_rsi < self.oversold] = 1   # 超卖时买入
        self.signals[stoch_rsi > self.overbought] = -1  # 超买时卖出