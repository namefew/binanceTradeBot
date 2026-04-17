"""
三重指数平滑平均线策略 (TRIX)
三重平滑的动量指标
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class TrixStrategy(BaseStrategy):
    """
    三重指数平滑平均线策略 (TRIX)
    三重平滑的动量指标
    """
    
    def __init__(self, period=15, signal_period=9, transaction_cost=0.001, position_size=1.0):
        super().__init__("TRIX Strategy", transaction_cost, indicator_short_name="TRIX", position_size=position_size)
        self.period = period
        self.signal_period = signal_period
        
    def generate_signals(self):
        """
        生成TRIX交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算三重EMA
        ema1 = self.data['close'].ewm(span=self.period).mean()
        ema2 = ema1.ewm(span=self.period).mean()
        ema3 = ema2.ewm(span=self.period).mean()
        
        # 计算TRIX
        trix = ema3.pct_change() * 100
        
        # 计算信号线
        signal_line = trix.rolling(window=self.signal_period).mean()
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[(trix > signal_line) & (trix.shift(1) <= signal_line.shift(1))] = 1   # TRIX上穿信号线时买入
        self.signals[(trix < signal_line) & (trix.shift(1) >= signal_line.shift(1))] = -1  # TRIX下穿信号线时卖出