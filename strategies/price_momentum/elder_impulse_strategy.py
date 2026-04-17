"""
艾达冲力指标策略 (Elder Impulse)
根据研报：结合EMA和MACD直方图判断市场状态
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class ElderImpulseStrategy(BaseStrategy):
    """
    艾达冲力指标策略 (Elder Impulse)
    根据研报：结合EMA和MACD直方图判断市场状态
    """
    
    def __init__(self, ema_period=13, macd_fast=12, macd_slow=26, macd_signal=9, transaction_cost=0.001, position_size=1.0):
        super().__init__("Elder Impulse Strategy", transaction_cost, indicator_short_name="Elder Impulse", position_size=position_size)
        self.ema_period = ema_period
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        
    def generate_signals(self):
        """
        生成Elder Impulse交易信号
        根据颜色变化产生交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算EMA
        ema = self.data['close'].ewm(span=self.ema_period).mean()
        
        # 计算MACD
        ema_fast = self.data['close'].ewm(span=self.macd_fast).mean()
        ema_slow = self.data['close'].ewm(span=self.macd_slow).mean()
        macd_line = ema_fast - ema_slow
        macd_signal_line = macd_line.ewm(span=self.macd_signal).mean()
        macd_histogram = macd_line - macd_signal_line
        
        # 确定市场状态 (简化版本)
        # 绿色：EMA上升且MACD柱状图上升
        # 蓝色：EMA上升且MACD柱状图下降
        # 红色：EMA下降
        
        ema_up = ema > ema.shift(1)
        macd_hist_up = macd_histogram > macd_histogram.shift(1)
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # 当变为绿色时买入
        self.signals[(ema_up & macd_hist_up) & ~(ema_up.shift(1) & macd_hist_up.shift(1))] = 1
        # 当变为红色时卖出
        self.signals[~ema_up & ema_up.shift(1)] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)