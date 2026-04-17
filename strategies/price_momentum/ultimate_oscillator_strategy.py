"""
终极振荡器策略 (Ultimate Oscillator)
结合不同时间周期的动量指标
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class UltimateOscillatorStrategy(BaseStrategy):
    """
    终极振荡器策略 (Ultimate Oscillator)
    结合不同时间周期的动量指标
    """
    
    def __init__(self, period1=7, period2=14, period3=28, transaction_cost=0.001, position_size=1.0):
        super().__init__("Ultimate Oscillator Strategy", transaction_cost, indicator_short_name="Ultimate Oscillator", position_size=position_size)
        self.period1 = period1
        self.period2 = period2
        self.period3 = period3
        
    def generate_signals(self):
        """
        生成终极振荡器交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有high, low, close列
        required_columns = ['high', 'low', 'close']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算买入压力 (BP)
        bp = self.data['close'] - pd.concat([self.data['low'], self.data['close'].shift(1)], axis=1).min(axis=1)
        
        # 计算真实范围 (TR)
        tr1 = self.data['high'] - self.data['low']
        tr2 = abs(self.data['high'] - self.data['close'].shift(1))
        tr3 = abs(self.data['low'] - self.data['close'].shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # 计算不同周期的平均值
        avg_bp1 = bp.rolling(window=self.period1).sum()
        avg_tr1 = tr.rolling(window=self.period1).sum()
        
        avg_bp2 = bp.rolling(window=self.period2).sum()
        avg_tr2 = tr.rolling(window=self.period2).sum()
        
        avg_bp3 = bp.rolling(window=self.period3).sum()
        avg_tr3 = tr.rolling(window=self.period3).sum()
        
        # 计算终极振荡器
        uo = 100 * ((4 * avg_bp1 / avg_tr1) + (2 * avg_bp2 / avg_tr2) + (avg_bp3 / avg_tr3)) / (4 + 2 + 1)
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[(uo < 30) & (uo.shift(1) >= 30)] = 1   # 超卖时买入
        self.signals[(uo > 70) & (uo.shift(1) <= 70)] = -1  # 超买时卖出