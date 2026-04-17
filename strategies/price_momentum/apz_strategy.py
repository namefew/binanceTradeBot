"""
自适应价格带策略 (Adaptive Price Zone, APZ)
根据研报：APZ是基于波动率的价格带，用于识别支撑和阻力位
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class APZStrategy(BaseStrategy):
    """
    自适应价格带策略 (Adaptive Price Zone, APZ)
    根据研报：APZ是基于波动率的价格带，用于识别支撑和阻力位
    """
    
    def __init__(self, period=20, multiplier=2, transaction_cost=0.001, position_size=1.0):
        super().__init__("APZ Strategy", transaction_cost, indicator_short_name="APZ", position_size=position_size)
        self.period = period
        self.multiplier = multiplier
        
    def generate_signals(self):
        """
        生成APZ交易信号
        当价格突破上轨时买入，跌破下轨时卖出
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有必要的列
        required_columns = ['close', 'high', 'low']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算中间价
        mid_price = (self.data['high'] + self.data['low'] + self.data['close']) / 3
        
        # 计算DEMA
        ema = mid_price.ewm(span=self.period).mean()
        ema_ema = ema.ewm(span=self.period).mean()
        dema = 2 * ema - ema_ema
        
        # 计算波动率
        volatility = mid_price.rolling(window=self.period).std()
        
        # 计算上下轨
        upper_band = dema + self.multiplier * volatility
        lower_band = dema - self.multiplier * volatility
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # 价格上穿上轨时买入
        self.signals[(self.data['close'] > upper_band) & (self.data['close'].shift(1) <= upper_band.shift(1))] = 1
        # 价格下穿下轨时卖出
        self.signals[(self.data['close'] < lower_band) & (self.data['close'].shift(1) >= lower_band.shift(1))] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)