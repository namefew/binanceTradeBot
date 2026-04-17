"""
自回归策略
使用自回归模型预测价格走势
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy
from strategies.technical_indicators import TechnicalIndicators

class AutoRegressiveStrategy(BaseStrategy):
    """
    自回归策略
    使用自回归模型预测价格走势
    """
    
    def __init__(self, period=20, transaction_cost=0.001, position_size=1.0):
        super().__init__("AutoRegressive Strategy", transaction_cost, indicator_short_name="AutoRegressive", position_size=position_size)
        self.period = period
    
    def generate_signals(self):
        """
        生成交易信号
        """
        # 计算自回归预测 (简化版本)
        price = self.data['close']
        returns = price.pct_change()
        
        # 简单的自回归预测
        ar_pred = returns.rolling(window=self.period).mean()
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        
        # 当预测为正时买入
        buy_condition = ar_pred > 0
        # 当预测为负时卖出
        sell_condition = ar_pred < 0
        
        self.signals[buy_condition] = 1
        self.signals[sell_condition] = -1