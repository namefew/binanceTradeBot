"""
Chaikin震荡指标策略
结合了累积/派发线和MACD的概念
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class ChaikinOscillatorStrategy(BaseStrategy):
    """
    Chaikin震荡指标策略
    结合了累积/派发线和MACD的概念
    """
    
    def __init__(self, fast_period=3, slow_period=10, transaction_cost=0.001, position_size=1.0):
        super().__init__("Chaikin Oscillator Strategy", transaction_cost, indicator_short_name="Chaikin Oscillator", position_size=position_size)
        self.fast_period = fast_period
        self.slow_period = slow_period
        
    def generate_signals(self):
        """
        生成Chaikin震荡指标交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有high, low, close, volume列
        required_columns = ['high', 'low', 'close', 'volume']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算CLV（收盘价位置值）
        clv = ((self.data['close'] - self.data['low']) - (self.data['high'] - self.data['close'])) / (self.data['high'] - self.data['low'])
        clv = clv.fillna(0)  # 处理除零情况
        
        # 计算ADL（累积/派发线）
        adl = (clv * self.data['volume']).cumsum()
        
        # 计算Chaikin Oscillator
        fast_ema = adl.ewm(span=self.fast_period).mean()
        slow_ema = adl.ewm(span=self.slow_period).mean()
        chaikin_osc = fast_ema - slow_ema
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[(chaikin_osc > 0) & (chaikin_osc.shift(1) <= 0)] = 1   # 震荡线上穿零轴时买入
        self.signals[(chaikin_osc < 0) & (chaikin_osc.shift(1) >= 0)] = -1  # 震荡线下穿零轴时卖出