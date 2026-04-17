"""
惯性指标策略
结合相对活力指数和线性回归来识别趋势
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class InertiaIndicatorStrategy(BaseStrategy):
    """
    惯性指标策略
    结合相对活力指数和线性回归来识别趋势
    """
    
    def __init__(self, period=10, lr_period=14, transaction_cost=0.001, position_size=1.0):
        super().__init__("Inertia Indicator Strategy", transaction_cost, indicator_short_name="Inertia Indicator", position_size=position_size)
        self.period = period
        self.lr_period = lr_period
        
    def generate_signals(self):
        """
        生成惯性指标交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有open, high, low, close列
        required_columns = ['open', 'high', 'low', 'close']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算相对活力指数（简化版）
        co = self.data['close'] - self.data['open']
        hl = self.data['high'] - self.data['low']
        
        numerator = co.rolling(window=self.period).mean()
        denominator = hl.rolling(window=self.period).mean()
        rvi = numerator / denominator
        
        # 计算惯性指标（线性回归）
        inertia = pd.Series(0, index=self.data.index)
        
        for i in range(self.lr_period, len(rvi)):
            # 获取最近lr_period个RVI值
            rvi_values = rvi.iloc[i-self.lr_period:i]
            x = np.arange(len(rvi_values))
            
            # 计算线性回归斜率
            if len(rvi_values) > 1:
                slope, _ = np.polyfit(x, rvi_values, 1)
                inertia.iloc[i] = slope
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[inertia > 0] = 1   # 惯性为正时买入
        self.signals[inertia < 0] = -1  # 惯性为负时卖出