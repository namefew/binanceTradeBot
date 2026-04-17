"""
弗里德里克·布林策略 (Fractal Bands, FB)
根据研报：FB指标基于分形几何理论，用于识别价格的支撑和阻力位
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class FBStrategy(BaseStrategy):
    """
    弗里德里克·布林策略 (Fractal Bands, FB)
    根据研报：FB指标基于分形几何理论，用于识别价格的支撑和阻力位
    """
    
    def __init__(self, period=20, transaction_cost=0.001, position_size=1.0):
        super().__init__("FB Strategy", transaction_cost, indicator_short_name="FB", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成FB交易信号
        当价格突破上轨时买入，跌破下轨时卖出
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有必要的列
        required_columns = ['close', 'high', 'low']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算分形带
        # 上轨：周期内最高价的移动平均 + 标准差
        upper_band = self.data['high'].rolling(window=self.period).mean() + \
                     self.data['high'].rolling(window=self.period).std()
        
        # 下轨：周期内最低价的移动平均 - 标准差
        lower_band = self.data['low'].rolling(window=self.period).mean() - \
                     self.data['low'].rolling(window=self.period).std()
        
        # 中轨：收盘价的移动平均
        middle_band = self.data['close'].rolling(window=self.period).mean()
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # 价格上穿上轨时买入
        self.signals[(self.data['close'] > upper_band) & (self.data['close'].shift(1) <= upper_band.shift(1))] = 1
        # 价格下穿下轨时卖出
        self.signals[(self.data['close'] < lower_band) & (self.data['close'].shift(1) >= lower_band.shift(1))] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)