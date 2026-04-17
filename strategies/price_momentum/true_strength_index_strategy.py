"""
真实强度指数策略 (True Strength Index, TSI)
根据研报：双重平滑的动量指标
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class TrueStrengthIndexStrategy(BaseStrategy):
    """
    真实强度指数策略 (True Strength Index, TSI)
    根据研报：双重平滑的动量指标
    """
    
    def __init__(self, short_period=25, long_period=13, signal_period=7, transaction_cost=0.001, position_size=1.0):
        super().__init__("True Strength Index Strategy", transaction_cost, indicator_short_name="TSI", position_size=position_size)
        self.short_period = short_period
        self.long_period = long_period
        self.signal_period = signal_period
        
    def generate_signals(self):
        """
        生成TSI交易信号
        当TSI上穿/下穿信号线时产生交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算价格变化
        price_change = self.data['close'] - self.data['close'].shift(1)
        
        # 双重EMA平滑
        ema1 = price_change.ewm(span=self.long_period).mean()
        ema2 = ema1.ewm(span=self.short_period).mean()
        
        abs_price_change = abs(price_change)
        abs_ema1 = abs_price_change.ewm(span=self.long_period).mean()
        abs_ema2 = abs_ema1.ewm(span=self.short_period).mean()
        
        # 计算TSI
        tsi = (ema2 / abs_ema2) * 100
        
        # 计算信号线
        signal_line = tsi.ewm(span=self.signal_period).mean()
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # TSI上穿信号线时买入
        self.signals[(tsi > signal_line) & (tsi.shift(1) <= signal_line.shift(1))] = 1
        # TSI下穿信号线时卖出
        self.signals[(tsi < signal_line) & (tsi.shift(1) >= signal_line.shift(1))] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)