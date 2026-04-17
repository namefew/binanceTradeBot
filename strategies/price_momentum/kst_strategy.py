"""
知道确定的事策略 (Know Sure Thing, KST)
基于多个ROC的复合动量指标
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class KSTStrategy(BaseStrategy):
    """
    知道确定的事策略 (Know Sure Thing, KST)
    基于多个ROC的复合动量指标
    """
    
    def __init__(self, r1=10, r2=15, r3=20, r4=30, 
                 s1=10, s2=10, s3=10, s4=15, 
                 sig=9, transaction_cost=0.001, position_size=1.0):
        super().__init__("Know Sure Thing Strategy", transaction_cost, indicator_short_name="KST", position_size=position_size)
        self.r1 = r1
        self.r2 = r2
        self.r3 = r3
        self.r4 = r4
        self.s1 = s1
        self.s2 = s2
        self.s3 = s3
        self.s4 = s4
        self.sig = sig
        
    def generate_signals(self):
        """
        生成KST交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算ROC
        roc1 = self.data['close'].pct_change(self.r1) * 100
        roc2 = self.data['close'].pct_change(self.r2) * 100
        roc3 = self.data['close'].pct_change(self.r3) * 100
        roc4 = self.data['close'].pct_change(self.r4) * 100
        
        # 计算RCMA
        rcma1 = roc1.rolling(window=self.s1).mean()
        rcma2 = roc2.rolling(window=self.s2).mean()
        rcma3 = roc3.rolling(window=self.s3).mean()
        rcma4 = roc4.rolling(window=self.s4).mean()
        
        # 计算KST
        kst = (rcma1 * 1) + (rcma2 * 2) + (rcma3 * 3) + (rcma4 * 4)
        
        # 计算信号线
        signal_line = kst.rolling(window=self.sig).mean()
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[(kst > signal_line) & (kst.shift(1) <= signal_line.shift(1))] = 1   # KST上穿信号线时买入
        self.signals[(kst < signal_line) & (kst.shift(1) >= signal_line.shift(1))] = -1  # KST下穿信号线时卖出