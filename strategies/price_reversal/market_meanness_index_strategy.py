"""
市场平均指数策略 (Market Meanness Index, MMI)
根据研报：衡量市场趋势性的反向指标
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class MarketMeannessIndexStrategy(BaseStrategy):
    """
    市场平均指数策略 (Market Meanness Index, MMI)
    根据研报：衡量市场趋势性的反向指标
    """
    
    def __init__(self, period=200, threshold=75, transaction_cost=0.001, position_size=1.0):
        super().__init__("Market Meanness Index Strategy", transaction_cost, indicator_short_name="MMI", position_size=position_size)
        self.period = period
        self.threshold = threshold
        
    def generate_signals(self):
        """
        生成MMI交易信号
        当指标高于阈值时认为市场处于均值回归状态，低于阈值时认为处于趋势状态
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算中位数
        median_price = self.data['close'].rolling(window=self.period).median()
        
        # 计算高于和低于中位数的天数
        above_median = (self.data['close'] > median_price).rolling(window=self.period).sum()
        below_median = (self.data['close'] < median_price).rolling(window=self.period).sum()
        
        # 计算MMI
        mmi = 100 * (above_median + below_median) / self.period
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # MMI高于阈值时买入（均值回归市场）
        self.signals[(mmi > self.threshold) & (mmi.shift(1) <= self.threshold)] = 1
        # MMI低于阈值时卖出（趋势市场）
        self.signals[(mmi < self.threshold) & (mmi.shift(1) >= self.threshold)] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)