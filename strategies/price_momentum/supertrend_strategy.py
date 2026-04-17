"""
超级趋势策略 (Supertrend)
用于识别市场趋势方向
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class SupertrendStrategy(BaseStrategy):
    """
    超级趋势策略 (Supertrend)
    用于识别市场趋势方向
    """
    
    def __init__(self, period=10, multiplier=3, transaction_cost=0.001, position_size=1.0):
        super().__init__("Supertrend Strategy", transaction_cost, indicator_short_name="Supertrend", position_size=position_size)
        self.period = period
        self.multiplier = multiplier
        
    def generate_signals(self):
        """
        生成超级趋势交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有high, low, close列
        required_columns = ['high', 'low', 'close']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算ATR
        tr1 = self.data['high'] - self.data['low']
        tr2 = abs(self.data['high'] - self.data['close'].shift(1))
        tr3 = abs(self.data['low'] - self.data['close'].shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=self.period).mean()
        
        # 计算上下轨
        up = ((self.data['high'] + self.data['low']) / 2) - (self.multiplier * atr)
        dn = ((self.data['high'] + self.data['low']) / 2) + (self.multiplier * atr)
        
        # 计算趋势
        trend_up = pd.Series(0, index=self.data.index)
        trend_down = pd.Series(0, index=self.data.index)
        trend = pd.Series(1, index=self.data.index)
        
        for i in range(1, len(self.data)):
            if self.data['close'].iloc[i] > trend_down.iloc[i-1]:
                trend.iloc[i] = 1
            elif self.data['close'].iloc[i] < trend_up.iloc[i-1]:
                trend.iloc[i] = -1
            else:
                trend.iloc[i] = trend.iloc[i-1]
                
            if trend.iloc[i] > 0:
                trend_up.iloc[i] = max(up.iloc[i], trend_up.iloc[i-1]) if trend.iloc[i-1] > 0 else up.iloc[i]
            else:
                trend_up.iloc[i] = up.iloc[i]
                
            if trend.iloc[i] < 0:
                trend_down.iloc[i] = min(dn.iloc[i], trend_down.iloc[i-1]) if trend.iloc[i-1] < 0 else dn.iloc[i]
            else:
                trend_down.iloc[i] = dn.iloc[i]
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[trend == 1] = 1   # 上升趋势时买入
        self.signals[trend == -1] = -1 # 下降趋势时卖出