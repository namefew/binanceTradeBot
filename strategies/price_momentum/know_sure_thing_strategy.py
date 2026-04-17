"""
知道确信指标策略 (KST)
基于多个动量指标的综合趋势指标
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class KnowSureThingStrategy(BaseStrategy):
    """
    知道确信指标策略 (KST)
    基于多个动量指标的综合趋势指标
    """
    
    def __init__(self, roc1=10, roc2=15, roc3=20, roc4=30, 
                 sma1=10, sma2=10, sma3=10, sma4=15, signal_period=9, transaction_cost=0.001, position_size=1.0):
        super().__init__("Know Sure Thing Strategy", transaction_cost, indicator_short_name="KST", position_size=position_size)
        self.roc1 = roc1
        self.roc2 = roc2
        self.roc3 = roc3
        self.roc4 = roc4
        self.sma1 = sma1
        self.sma2 = sma2
        self.sma3 = sma3
        self.sma4 = sma4
        self.signal_period = signal_period
        
    def generate_signals(self):
        """
        生成知道确信指标交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算四个ROC
        roc1 = self.data['close'].pct_change(periods=self.roc1) * 100
        roc2 = self.data['close'].pct_change(periods=self.roc2) * 100
        roc3 = self.data['close'].pct_change(periods=self.roc3) * 100
        roc4 = self.data['close'].pct_change(periods=self.roc4) * 100
        
        # 计算平滑ROC
        sma1 = roc1.rolling(window=self.sma1).mean()
        sma2 = roc2.rolling(window=self.sma2).mean()
        sma3 = roc3.rolling(window=self.sma3).mean()
        sma4 = roc4.rolling(window=self.sma4).mean()
        
        # 计算KST
        kst = (sma1 * 1) + (sma2 * 2) + (sma3 * 3) + (sma4 * 4)
        
        # 计算信号线
        signal = kst.rolling(window=self.signal_period).mean()
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[(kst > signal) & (kst.shift(1) <= signal.shift(1))] = 1   # KST上穿信号线时买入
        self.signals[(kst < signal) & (kst.shift(1) >= signal.shift(1))] = -1  # KST下穿信号线时卖出