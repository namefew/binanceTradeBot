"""
价格震荡指标(Price Oscillator, PO)策略
根据研报：PO=(EMA_SHORT-EMA_LONG)/EMA_LONG*100
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class POStrategy(BaseStrategy):
    """
    价格震荡指标(Price Oscillator, PO)策略
    根据研报：PO=(EMA_SHORT-EMA_LONG)/EMA_LONG*100
    """
    
    def __init__(self, short_period=9, long_period=26, transaction_cost=0.001, position_size=1.0):
        super().__init__("PO Strategy", transaction_cost, indicator_short_name="PO", position_size=position_size)
        self.short_period = short_period
        self.long_period = long_period
        
    def generate_signals(self):
        """
        生成PO交易信号
        当PO上穿0时买入，下穿0时卖出
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算短期和长期EMA
        ema_short = self.data['close'].ewm(span=self.short_period).mean()
        ema_long = self.data['close'].ewm(span=self.long_period).mean()
        
        # 计算PO
        po = (ema_short - ema_long) / ema_long * 100
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # PO上穿0时买入
        self.signals[(po > 0) & (po.shift(1) <= 0)] = 1
        # PO下穿0时卖出
        self.signals[(po < 0) & (po.shift(1) >= 0)] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)