"""
艾达安全区域策略 (Elder Safe Zone)
根据研报：结合艾达射线和安全区域的策略
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class ElderSafeZoneStrategy(BaseStrategy):
    """
    艾达安全区域策略 (Elder Safe Zone)
    根据研报：结合艾达射线和安全区域的策略
    """
    
    def __init__(self, period=13, multiplier=2.5, transaction_cost=0.001, position_size=1.0):
        super().__init__("Elder Safe Zone Strategy", transaction_cost, indicator_short_name="Elder Safe Zone", position_size=position_size)
        self.period = period
        self.multiplier = multiplier
        
    def generate_signals(self):
        """
        生成Elder Safe Zone交易信号
        当价格突破安全区域时产生交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有必要的列
        required_columns = ['high', 'low', 'close']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算EMA
        ema = self.data['close'].ewm(span=self.period).mean()
        
        # 计算熊力和牛力
        bull_power = self.data['high'] - ema
        bear_power = self.data['low'] - ema
        
        # 计算安全区域
        avg_bull_power = bull_power.rolling(window=self.period).mean()
        avg_bear_power = bear_power.rolling(window=self.period).mean()
        
        std_bull_power = bull_power.rolling(window=self.period).std()
        std_bear_power = bear_power.rolling(window=self.period).std()
        
        upper_safe_zone = avg_bull_power + std_bull_power * self.multiplier
        lower_safe_zone = avg_bear_power - std_bear_power * self.multiplier
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # 牛力上穿安全区域时买入
        self.signals[(bull_power > upper_safe_zone) & (bull_power.shift(1) <= upper_safe_zone.shift(1))] = 1
        # 熊力下穿安全区域时卖出
        self.signals[(bear_power < lower_safe_zone) & (bear_power.shift(1) >= lower_safe_zone.shift(1))] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)