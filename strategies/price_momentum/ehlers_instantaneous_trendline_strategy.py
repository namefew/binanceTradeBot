"""
Ehlers瞬时趋势线策略
使用正弦波和余弦波来识别趋势
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class EhlersInstantaneousTrendlineStrategy(BaseStrategy):
    """
    Ehlers瞬时趋势线策略
    使用正弦波和余弦波来识别趋势
    """
    
    def __init__(self, period=20, transaction_cost=0.001, position_size=1.0):
        super().__init__("Ehlers Instantaneous Trendline Strategy", transaction_cost, indicator_short_name="Ehlers Instantaneous Trendline", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成Ehlers瞬时趋势线交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算瞬时趋势线
        it = pd.Series(0, index=self.data.index)
        alpha = 2 / (self.period + 1)
        
        for i in range(2, len(self.data)):
            # 计算瞬时趋势线
            it.iloc[i] = (alpha - alpha**2/4) * self.data['close'].iloc[i] + \
                         alpha**2/2 * self.data['close'].iloc[i-1] - \
                         (alpha - alpha**2*3/4) * self.data['close'].iloc[i-2] + \
                         2 * (1 - alpha) * it.iloc[i-1] - (1 - alpha)**2 * it.iloc[i-2]
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[self.data['close'] > it] = 1   # 价格高于瞬时趋势线时买入
        self.signals[self.data['close'] < it] = -1  # 价格低于瞬时趋势线时卖出