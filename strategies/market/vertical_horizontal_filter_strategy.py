"""
垂直水平过滤器策略 (Vertical Horizontal Filter, VHF)
根据研报：判断市场趋势性或盘整性的指标
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class VerticalHorizontalFilterStrategy(BaseStrategy):
    """
    垂直水平过滤器策略 (Vertical Horizontal Filter, VHF)
    根据研报：判断市场趋势性或盘整性的指标
    """
    
    def __init__(self, period=28, transaction_cost=0.001, position_size=1.0):
        super().__init__("Vertical Horizontal Filter Strategy", transaction_cost, indicator_short_name="VHF", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成VHF交易信号
        当VHF高于阈值时采用趋势策略，低于阈值时采用震荡策略
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算期间内价格变化绝对值之和
        price_change_sum = abs(self.data['close'] - self.data['close'].shift(1)).rolling(window=self.period).sum()
        
        # 计算期间内最高价与最低价之差
        period_high = self.data['close'].rolling(window=self.period).max()
        period_low = self.data['close'].rolling(window=self.period).min()
        high_low_diff = period_high - period_low
        
        # 计算VHF
        vhf = high_low_diff / price_change_sum
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # VHF低于0.3时买入（震荡市场）
        self.signals[(vhf < 0.3) & (vhf.shift(1) >= 0.3)] = 1
        # VHF高于0.7时卖出（趋势市场）
        self.signals[(vhf > 0.7) & (vhf.shift(1) <= 0.7)] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)