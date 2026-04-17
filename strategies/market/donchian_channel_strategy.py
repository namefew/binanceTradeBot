"""
唐奇安通道策略 (Donchian Channel)
根据研报：基于价格极值的通道突破策略
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class DonchianChannelStrategy(BaseStrategy):
    """
    唐奇安通道策略 (Donchian Channel)
    根据研报：基于价格极值的通道突破策略
    """
    
    def __init__(self, period=20, transaction_cost=0.001, position_size=1.0):
        super().__init__("Donchian Channel Strategy", transaction_cost, indicator_short_name="DC", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成Donchian Channel交易信号
        价格突破上轨时买入，跌破下轨时卖出
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有必要的列
        required_columns = ['high', 'low']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算通道
        upper_channel = self.data['high'].rolling(window=self.period).max()
        lower_channel = self.data['low'].rolling(window=self.period).min()
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # 价格突破上轨时买入
        self.signals[(self.data['close'] > upper_channel) & (self.data['close'].shift(1) <= upper_channel.shift(1))] = 1
        # 价格跌破下轨时卖出
        self.signals[(self.data['close'] < lower_channel) & (self.data['close'].shift(1) >= lower_channel.shift(1))] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)