"""
趋势强度指数(Trend Intensity Index, TII)策略
根据研报：TII=100*SUMPOS/(SUMPOS+SUMNEG)
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class TIIStrategy(BaseStrategy):
    """
    趋势强度指数(Trend Intensity Index, TII)策略
    根据研报：TII=100*SUMPOS/(SUMPOS+SUMNEG)
    """
    
    def __init__(self, n1=40, m=None, n2=9, transaction_cost=0.001, position_size=1.0):
        super().__init__("TII Strategy", transaction_cost, indicator_short_name="TII", position_size=position_size)
        self.n1 = n1
        self.m = m if m is not None else int(n1/2) + 1
        self.n2 = n2
        
    def generate_signals(self):
        """
        生成TII交易信号
        当TII上穿TII_SIGNAL时买入，下穿时卖出
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算TII
        close_ma = self.data['close'].rolling(window=self.n1).mean()
        dev = self.data['close'] - close_ma
        
        # 计算正负偏差
        devpos = dev.where(dev > 0, 0)
        devneg = (-dev).where(dev < 0, 0)
        
        # 计算SUMPOS和SUMNEG
        sumpos = devpos.rolling(window=self.m).sum()
        sumneg = devneg.rolling(window=self.m).sum()
        
        # 计算TII
        tii = 100 * sumpos / (sumpos + sumneg)
        
        # 计算信号线
        tii_signal = tii.ewm(span=self.n2).mean()
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # TII上穿TII_SIGNAL时买入
        self.signals[(tii > tii_signal) & (tii.shift(1) <= tii_signal.shift(1))] = 1
        # TII下穿TII_SIGNAL时卖出
        self.signals[(tii < tii_signal) & (tii.shift(1) >= tii_signal.shift(1))] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)