"""
最小二乘移动平均线策略 (LSMA)
使用线性回归来计算移动平均线
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class LeastSquaresMovingAverageStrategy(BaseStrategy):
    """
    最小二乘移动平均线策略 (LSMA)
    使用线性回归来计算移动平均线
    """
    
    def __init__(self, period=20, transaction_cost=0.001, position_size=1.0):
        super().__init__("LSMA Strategy", transaction_cost, indicator_short_name="LSMA", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成LSMA交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算LSMA
        lsma = pd.Series(0, index=self.data.index)
        
        for i in range(self.period, len(self.data)):
            # 获取最近period个收盘价
            prices = self.data['close'].iloc[i-self.period:i].values
            x = np.arange(len(prices))
            
            # 使用最小二乘法计算线性回归
            slope, intercept = np.polyfit(x, prices, 1)
            
            # 计算预测值（最后一个点）
            lsma.iloc[i] = intercept + slope * (len(prices) - 1)
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[self.data['close'] > lsma] = 1   # 价格高于LSMA时买入
        self.signals[self.data['close'] < lsma] = -1  # 价格低于LSMA时卖出