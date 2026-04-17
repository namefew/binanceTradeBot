"""
相当好振荡器策略 (Pretty Good Oscillator)
基于移动平均线和平均真实波幅的振荡器
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class PrettyGoodOscillatorStrategy(BaseStrategy):
    """
    相当好振荡器策略 (Pretty Good Oscillator)
    基于移动平均线和平均真实波幅的振荡器
    """
    
    def __init__(self, period=14, transaction_cost=0.001, position_size=1.0):
        super().__init__("Pretty Good Oscillator Strategy", transaction_cost, indicator_short_name="PGO", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成相当好振荡器交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有high, low, close列
        required_columns = ['high', 'low', 'close']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算移动平均线
        ma = self.data['close'].rolling(window=self.period).mean()
        
        # 计算真实波幅(TR)
        tr1 = self.data['high'] - self.data['low']
        tr2 = abs(self.data['high'] - self.data['close'].shift(1))
        tr3 = abs(self.data['low'] - self.data['close'].shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # 计算平均真实波幅(ATR)
        atr = tr.rolling(window=self.period).mean()
        
        # 计算相当好振荡器
        pgo = (self.data['close'] - ma) / atr
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[pgo < -2] = 1   # 超卖时买入
        self.signals[pgo > 2] = -1   # 超买时卖出