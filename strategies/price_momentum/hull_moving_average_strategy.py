"""
Hull移动平均线策略
具有最小滞后性的移动平均线
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class HullMovingAverageStrategy(BaseStrategy):
    """
    Hull移动平均线策略
    具有最小滞后性的移动平均线
    """
    
    def __init__(self, period=9, transaction_cost=0.001, position_size=1.0):
        super().__init__("Hull Moving Average Strategy", transaction_cost, indicator_short_name="Hull Moving Average", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成Hull MA交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算权重移动平均线
        def wma(series, period):
            weights = np.arange(1, period + 1)
            return series.rolling(period).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)
        
        # 计算Hull MA
        half_period = self.period // 2
        sqrt_period = int(np.sqrt(self.period))
        
        wma1 = wma(self.data['close'], half_period)
        wma2 = wma(self.data['close'], self.period)
        diff_series = 2 * wma1 - wma2
        hull_ma = wma(diff_series, sqrt_period)
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[self.data['close'] > hull_ma] = 1   # 价格高于Hull MA时买入
        self.signals[self.data['close'] < hull_ma] = -1  # 价格低于Hull MA时卖出