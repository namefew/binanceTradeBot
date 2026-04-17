"""
Guppy多重移动平均线策略
使用多条不同周期的EMA来识别趋势
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class GuppyMultipleMovingAverageStrategy(BaseStrategy):
    """
    Guppy多重移动平均线策略
    使用多条不同周期的EMA来识别趋势
    """
    
    def __init__(self, transaction_cost=0.001, position_size=1.0):
        super().__init__("Guppy Multiple Moving Average Strategy", transaction_cost, indicator_short_name="GMMA", position_size=position_size)

    def generate_signals(self):
        """
        生成GMMA交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算短期EMA (3, 5, 8, 10, 12, 15)
        short_ema_3 = self.data['close'].ewm(span=3).mean()
        short_ema_5 = self.data['close'].ewm(span=5).mean()
        short_ema_8 = self.data['close'].ewm(span=8).mean()
        short_ema_10 = self.data['close'].ewm(span=10).mean()
        short_ema_12 = self.data['close'].ewm(span=12).mean()
        short_ema_15 = self.data['close'].ewm(span=15).mean()
        
        # 计算长期EMA (30, 35, 40, 45, 50, 60)
        long_ema_30 = self.data['close'].ewm(span=30).mean()
        long_ema_35 = self.data['close'].ewm(span=35).mean()
        long_ema_40 = self.data['close'].ewm(span=40).mean()
        long_ema_45 = self.data['close'].ewm(span=45).mean()
        long_ema_50 = self.data['close'].ewm(span=50).mean()
        long_ema_60 = self.data['close'].ewm(span=60).mean()
        
        # 判断短期和长期趋势
        short_trend = (short_ema_3 > short_ema_5) & (short_ema_5 > short_ema_8) & \
                      (short_ema_8 > short_ema_10) & (short_ema_10 > short_ema_12) & (short_ema_12 > short_ema_15)
        
        long_trend = (long_ema_30 > long_ema_35) & (long_ema_35 > long_ema_40) & \
                     (long_ema_40 > long_ema_45) & (long_ema_45 > long_ema_50) & (long_ema_50 > long_ema_60)
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[(short_trend) & (long_trend)] = 1   # 短期和长期趋势一致向上时买入
        self.signals[(~short_trend) & (~long_trend)] = -1  # 短期和长期趋势一致向下时卖出