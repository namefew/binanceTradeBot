"""
蔡金波动率策略 (Chaikin Volatility)
根据研报：衡量价格波动幅度的变化
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class ChaikinVolatilityStrategy(BaseStrategy):
    """
    蔡金波动率策略 (Chaikin Volatility)
    根据研报：衡量价格波动幅度的变化
    """
    
    def __init__(self, period=10, roc_period=10, transaction_cost=0.001, position_size=1.0):
        super().__init__("Chaikin Volatility Strategy", transaction_cost, indicator_short_name="Chaikin Volatility", position_size=position_size)
        self.period = period
        self.roc_period = roc_period
        
    def generate_signals(self):
        """
        生成Chaikin Volatility交易信号
        当波动率下降后上升时买入，波动率上升后下降时卖出
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有必要的列
        required_columns = ['high', 'low']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算价格范围
        price_range = self.data['high'] - self.data['low']
        
        # 计算EMA
        ema_range = price_range.ewm(span=self.period).mean()
        
        # 计算ROC
        roc = (ema_range / ema_range.shift(self.roc_period) - 1) * 100
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # 波动率下降后上升时买入
        self.signals[(roc > 0) & (roc.shift(1) <= 0)] = 1
        # 波动率上升后下降时卖出
        self.signals[(roc < 0) & (roc.shift(1) >= 0)] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)