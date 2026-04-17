"""
线性回归策略
基于线性回归分析的趋势策略
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class LinearRegressionStrategy(BaseStrategy):
    """
    线性回归策略
    基于线性回归分析的趋势策略
    """
    
    def __init__(self, period=20, transaction_cost=0.001, position_size=1.0):
        super().__init__("Linear Regression Strategy", transaction_cost, indicator_short_name="Linear Regression", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成线性回归交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算线性回归值
        lr_values = pd.Series(0, index=self.data.index)
        
        for i in range(self.period, len(self.data)):
            # 获取最近period个收盘价
            prices = self.data['close'].iloc[i-self.period:i]
            x = np.arange(len(prices))
            
            # 计算线性回归
            slope, intercept = np.polyfit(x, prices, 1)
            lr_values.iloc[i] = intercept + slope * (len(prices) - 1)
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[self.data['close'] > lr_values] = 1   # 价格高于线性回归线时买入
        self.signals[self.data['close'] < lr_values] = -1  # 价格低于线性回归线时卖出