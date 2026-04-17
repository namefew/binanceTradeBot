"""
TRIX策略
三重指数移动平均线振荡器
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class TRIXStrategy(BaseStrategy):
    """
    TRIX策略
    三重指数移动平均线振荡器
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
            
        # 计算TRIX
        ex1 = self.data['close'].ewm(span=self.period).mean()
        ex2 = ex1.ewm(span=self.period).mean()
        ex3 = ex2.ewm(span=self.period).mean()
        trix = ex3.pct_change() * 100
        
        # 计算信号线
        signal = trix.ewm(span=self.signal_period).mean()
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[(trix > signal) & (trix.shift(1) <= signal.shift(1))] = 1   # TRIX上穿信号线时买入
        self.signals[(trix < signal) & (trix.shift(1) >= signal.shift(1))] = -1  # TRIX下穿信号线时卖出