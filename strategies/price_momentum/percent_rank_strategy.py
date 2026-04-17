"""
百分比排名策略 (Percent Rank)
根据研报：衡量当前价格在历史价格中的相对位置
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class PercentRankStrategy(BaseStrategy):
    """
    百分比排名策略 (Percent Rank)
    根据研报：衡量当前价格在历史价格中的相对位置
    """
    
    def __init__(self, period=50, overbought=80, oversold=20, transaction_cost=0.001, position_size=1.0):
        super().__init__("Percent Rank Strategy", transaction_cost, indicator_short_name="Percent Rank", position_size=position_size)
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
        
    def generate_signals(self):
        """
        生成Percent Rank交易信号
        当指标处于极端位置时产生交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算Percent Rank
        percent_rank = pd.Series(index=self.data.index)
        for i in range(self.period, len(self.data)):
            current_price = self.data['close'].iloc[i]
            historical_prices = self.data['close'].iloc[i-self.period:i]
            rank = (historical_prices < current_price).sum()
            percent_rank.iloc[i] = 100 * rank / self.period
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # Percent Rank低于20时买入
        self.signals[(percent_rank < self.oversold) & (percent_rank.shift(1) >= self.oversold)] = 1
        # Percent Rank高于80时卖出
        self.signals[(percent_rank > self.overbought) & (percent_rank.shift(1) <= self.overbought)] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)