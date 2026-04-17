"""
钱德动量震荡器策略 (Chande Momentum Oscillator, CMO)
根据研报：衡量价格动量的震荡指标
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class ChandeMomentumOscillatorStrategy(BaseStrategy):
    """
    钱德动量震荡器策略 (Chande Momentum Oscillator, CMO)
    根据研报：衡量价格动量的震荡指标
    """
    
    def __init__(self, period=14, overbought=50, oversold=-50, transaction_cost=0.001, position_size=1.0):
        super().__init__("Chande Momentum Oscillator Strategy", transaction_cost, indicator_short_name="CMO", position_size=position_size)
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
        
    def generate_signals(self):
        """
        生成CMO交易信号
        当指标上穿/下穿阈值时产生交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算价格变化
        price_diff = self.data['close'].diff()
        
        # 计算上涨和下跌的绝对值之和
        up_sum = price_diff.where(price_diff > 0, 0).rolling(window=self.period).sum()
        down_sum = (-price_diff).where(price_diff < 0, 0).rolling(window=self.period).sum()
        
        # 计算CMO
        cmo = 100 * (up_sum - down_sum) / (up_sum + down_sum)
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # CMO上穿-50时买入
        self.signals[(cmo > self.oversold) & (cmo.shift(1) <= self.oversold)] = 1
        # CMO下穿50时卖出
        self.signals[(cmo < self.overbought) & (cmo.shift(1) >= self.overbought)] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)