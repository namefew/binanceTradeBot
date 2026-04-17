"""
漩涡指标策略 (Vortex Indicator)
用于识别趋势的开始和结束
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class VortexStrategy(BaseStrategy):
    """
    漩涡指标策略 (Vortex Indicator)
    用于识别趋势的开始和结束
    """
    
    def __init__(self, period=14, transaction_cost=0.001, position_size=1.0):
        super().__init__("Vortex Strategy", transaction_cost, indicator_short_name="Vortex", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成漩涡指标交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有high, low, close列
        required_columns = ['high', 'low', 'close']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算VM+和VM-
        vm_plus = abs(self.data['high'] - self.data['low'].shift(1))
        vm_minus = abs(self.data['low'] - self.data['high'].shift(1))
        
        # 计算真实波幅(TR)
        tr = pd.concat([
            self.data['high'] - self.data['low'],
            abs(self.data['high'] - self.data['close'].shift(1)),
            abs(self.data['low'] - self.data['close'].shift(1))
        ], axis=1).max(axis=1)
        
        # 计算VI+和VI-
        vi_plus = vm_plus.rolling(window=self.period).sum() / tr.rolling(window=self.period).sum()
        vi_minus = vm_minus.rolling(window=self.period).sum() / tr.rolling(window=self.period).sum()
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[(vi_plus > vi_minus) & (vi_plus.shift(1) <= vi_minus.shift(1))] = 1   # VI+上穿VI-时买入
        self.signals[(vi_plus < vi_minus) & (vi_plus.shift(1) >= vi_minus.shift(1))] = -1  # VI+下穿VI-时卖出