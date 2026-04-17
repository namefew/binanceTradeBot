"""
Chande动量振荡器策略 (CMO)
用于测量价格动量的振荡器
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class CMOStrategy(BaseStrategy):
    """
    Chande动量振荡器策略 (CMO)
    用于测量价格动量的振荡器
    """
    
    def __init__(self, period=14, overbought=50, oversold=-50, transaction_cost=0.001, position_size=1.0):
        super().__init__("Chande Momentum Oscillator Strategy", transaction_cost, indicator_short_name="CMO", position_size=position_size)
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
        
    def generate_signals(self):
        """
        生成CMO交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算价格变化
        delta = self.data['close'].diff()
        
        # 计算上涨和下跌的和
        up = delta.where(delta > 0, 0)
        down = -delta.where(delta < 0, 0)
        
        sum_up = up.rolling(window=self.period).sum()
        sum_down = down.rolling(window=self.period).sum()
        
        # 计算CMO
        cmo = 100 * (sum_up - sum_down) / (sum_up + sum_down)
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[cmo < self.oversold] = 1    # 超卖时买入
        self.signals[cmo > self.overbought] = -1 # 超买时卖出