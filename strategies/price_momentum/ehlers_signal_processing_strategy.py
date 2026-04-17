"""
埃勒斯信号处理策略
使用数字信号处理技术来识别和预测价格趋势
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy
from strategies.technical_indicators import TechnicalIndicators

class EhlersSignalProcessingStrategy(BaseStrategy):
    """
    埃勒斯信号处理策略
    使用数字信号处理技术来识别和预测价格趋势
    """
    
    def __init__(self, period=20, transaction_cost=0.001, position_size=1.0):
        super().__init__("Ehlers Signal Processing Strategy", transaction_cost, indicator_short_name="Ehlers Signal Processing", position_size=position_size)
        self.period = period
    
    def generate_signals(self):
        """
        生成交易信号
        """
        # 计算信号处理指标 (简化版本)
        price = self.data['close']
        
        # 计算去趋势价格
        detrended = price - price.rolling(window=self.period).mean()
        
        # 计算信号能量
        signal_energy = detrended.rolling(window=self.period).apply(lambda x: np.sum(x**2) if len(x.dropna()) == len(x) else 0, raw=False)
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        
        # 当信号能量从低变高时买入
        energy_ma = signal_energy.rolling(window=5).mean()
        buy_condition = (energy_ma > energy_ma.shift(1)) & (energy_ma.shift(1) <= energy_ma.shift(2))
        # 当信号能量从高变低时卖出
        sell_condition = (energy_ma < energy_ma.shift(1)) & (energy_ma.shift(1) >= energy_ma.shift(2))
        
        self.signals[buy_condition] = 1
        self.signals[sell_condition] = -1