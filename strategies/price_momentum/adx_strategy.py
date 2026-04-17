"""
ADX策略 (Average Directional Index)
用于衡量趋势强度的指标
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class ADXStrategy(BaseStrategy):
    """
    ADX策略 (Average Directional Index)
    用于衡量趋势强度的指标
    """
    
    def __init__(self, period=14, threshold=20, transaction_cost=0.001, position_size=1.0):
        super().__init__("ADX Strategy", transaction_cost, indicator_short_name="ADX", position_size=position_size)
        self.period = period
        self.threshold = threshold
        
    def generate_signals(self):
        """
        生成ADX交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有high, low, close列
        required_columns = ['high', 'low', 'close']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算真实波幅 (TR)
        high_low = self.data['high'] - self.data['low']
        high_close = abs(self.data['high'] - self.data['close'].shift(1))
        low_close = abs(self.data['low'] - self.data['close'].shift(1))
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        
        # 计算方向运动
        up_move = self.data['high'] - self.data['high'].shift(1)
        down_move = self.data['low'].shift(1) - self.data['low']
        
        # 初始化+DM和-DM
        plus_dm = pd.Series(0, index=self.data.index)
        minus_dm = pd.Series(0, index=self.data.index)
        
        # 计算+DM和-DM
        plus_dm[(up_move > down_move) & (up_move > 0)] = up_move
        minus_dm[(down_move > up_move) & (down_move > 0)] = down_move
        
        # 计算+DI和-DI
        plus_di = 100 * (plus_dm.ewm(alpha=1/self.period).mean() / tr.ewm(alpha=1/self.period).mean())
        minus_di = 100 * (minus_dm.ewm(alpha=1/self.period).mean() / tr.ewm(alpha=1/self.period).mean())
        
        # 计算ADX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.ewm(alpha=1/self.period).mean()
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # 当+DI上穿-DI且ADX高于阈值时买入
        self.signals[(plus_di > minus_di) & (plus_di.shift(1) <= minus_di.shift(1)) & (adx > self.threshold)] = 1
        # 当+DI下穿-DI且ADX高于阈值时卖出
        self.signals[(plus_di < minus_di) & (plus_di.shift(1) >= minus_di.shift(1)) & (adx > self.threshold)] = -1