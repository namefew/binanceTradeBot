"""
量子趋势指标策略 (Quantitative Qualitative Estimation, QQE)
根据研报：基于RSI和ATR的自适应趋势指标
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class QQEStrategy(BaseStrategy):
    """
    量子趋势指标策略 (Quantitative Qualitative Estimation, QQE)
    根据研报：基于RSI和ATR的自适应趋势指标
    """
    
    def __init__(self, rsi_period=14, sf=5, qqe_factor=4.236, transaction_cost=0.001, position_size=1.0):
        super().__init__("QQE Strategy", transaction_cost, indicator_short_name="QQE", position_size=position_size)
        self.rsi_period = rsi_period
        self.sf = sf
        self.qqe_factor = qqe_factor
        
    def generate_signals(self):
        """
        生成QQE交易信号
        当QQE线上穿/下穿零轴时产生交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算RSI
        delta = self.data['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=self.rsi_period).mean()
        avg_loss = loss.rolling(window=self.rsi_period).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        # 计算ATR
        tr1 = self.data['high'] - self.data['low']
        tr2 = abs(self.data['high'] - self.data['close'].shift(1))
        tr3 = abs(self.data['low'] - self.data['close'].shift(1))
        tr = pd.DataFrame({'tr1': tr1, 'tr2': tr2, 'tr3': tr3}).max(axis=1)
        atr_rsi = tr.rolling(window=self.rsi_period).mean()
        
        # 计算QQE (简化版本)
        dar = atr_rsi.ewm(span=self.sf).mean() * self.qqe_factor
        long_filter = rsi.shift(1) + dar
        short_filter = rsi.shift(1) - dar
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # RSI上穿long_filter时买入
        self.signals[(rsi > long_filter) & (rsi.shift(1) <= long_filter.shift(1))] = 1
        # RSI下穿short_filter时卖出
        self.signals[(rsi < short_filter) & (rsi.shift(1) >= short_filter.shift(1))] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)