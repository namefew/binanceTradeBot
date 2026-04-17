"""
肯特纳通道策略 (Keltner Channel, KC)
根据研报：KC是基于平均真实波幅的通道指标
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class KCStrategy(BaseStrategy):
    """
    肯特纳通道策略 (Keltner Channel, KC)
    根据研报：KC是基于平均真实波幅的通道指标
    """
    
    def __init__(self, period=20, multiplier=1.5, transaction_cost=0.001, position_size=1.0):
        super().__init__("KC Strategy", transaction_cost, indicator_short_name="KC", position_size=position_size)
        self.period = period
        self.multiplier = multiplier
        
    def generate_signals(self):
        """
        生成KC交易信号
        当价格上穿上轨时买入，下穿下轨时卖出
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有必要的列
        required_columns = ['close', 'high', 'low']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算真实波幅(TR)
        tr1 = self.data['high'] - self.data['low']
        tr2 = abs(self.data['high'] - self.data['close'].shift(1))
        tr3 = abs(self.data['low'] - self.data['close'].shift(1))
        tr = pd.DataFrame({'tr1': tr1, 'tr2': tr2, 'tr3': tr3}).max(axis=1)
        
        # 计算平均真实波幅(ATR)
        atr = tr.rolling(window=self.period).mean()
        
        # 计算中间线(EMA)
        middle_line = self.data['close'].ewm(span=self.period).mean()
        
        # 计算上下轨
        upper_band = middle_line + atr * self.multiplier
        lower_band = middle_line - atr * self.multiplier
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # 价格上穿上轨时买入
        self.signals[(self.data['close'] > upper_band) & (self.data['close'].shift(1) <= upper_band.shift(1))] = 1
        # 价格下穿下轨时卖出
        self.signals[(self.data['close'] < lower_band) & (self.data['close'].shift(1) >= lower_band.shift(1))] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)