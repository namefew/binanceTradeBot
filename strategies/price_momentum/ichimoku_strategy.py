"""
一目均衡图策略 (Ichimoku Kinko Hyo)
一种综合性技术指标
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class IchimokuStrategy(BaseStrategy):
    """
    一目均衡图策略 (Ichimoku Kinko Hyo)
    一种综合性技术指标
    """
    
    def __init__(self, tenkan_period=9, kijun_period=26, senkou_period=52, transaction_cost=0.001, position_size=1.0):
        super().__init__("Ichimoku Strategy", transaction_cost, indicator_short_name="Ichimoku", position_size=position_size)
        self.tenkan_period = tenkan_period
        self.kijun_period = kijun_period
        self.senkou_period = senkou_period
        
    def generate_signals(self):
        """
        生成一目均衡图交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有high, low列
        required_columns = ['high', 'low']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算转换线 (Tenkan-sen)
        tenkan_high = self.data['high'].rolling(window=self.tenkan_period).max()
        tenkan_low = self.data['low'].rolling(window=self.tenkan_period).min()
        tenkan_sen = (tenkan_high + tenkan_low) / 2
        
        # 计算基准线 (Kijun-sen)
        kijun_high = self.data['high'].rolling(window=self.kijun_period).max()
        kijun_low = self.data['low'].rolling(window=self.kijun_period).min()
        kijun_sen = (kijun_high + kijun_low) / 2
        
        # 计算先行带 (Senkou Span)
        senkou_span_a = (tenkan_sen + kijun_sen) / 2
        senkou_span_b_high = self.data['high'].rolling(window=self.senkou_period).max()
        senkou_span_b_low = self.data['low'].rolling(window=self.senkou_period).min()
        senkou_span_b = (senkou_span_b_high + senkou_span_b_low) / 2
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # 价格在云层之上且转换线上穿基准线时买入
        self.signals[(self.data['close'] > senkou_span_a) & (tenkan_sen > kijun_sen) & 
                     (tenkan_sen.shift(1) <= kijun_sen.shift(1))] = 1
        # 价格在云层之下且转换线下穿基准线时卖出
        self.signals[(self.data['close'] < senkou_span_a) & (tenkan_sen < kijun_sen) & 
                     (tenkan_sen.shift(1) >= kijun_sen.shift(1))] = -1