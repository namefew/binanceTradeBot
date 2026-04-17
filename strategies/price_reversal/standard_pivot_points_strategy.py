"""
标准轴心点策略
用于识别支撑位和阻力位
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class StandardPivotPointsStrategy(BaseStrategy):
    """
    标准轴心点策略
    用于识别支撑位和阻力位
    """
    
    def __init__(self, transaction_cost=0.001, position_size=1.0):
        super().__init__("Standard Pivot Points Strategy", transaction_cost, indicator_short_name="Pivot Points", position_size=position_size)
        
    def generate_signals(self):
        """
        生成轴心点交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有high, low, close列
        required_columns = ['high', 'low', 'close']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算轴心点
        pivot = (self.data['high'] + self.data['low'] + self.data['close']) / 3
        
        # 计算支撑位和阻力位
        r1 = (2 * pivot) - self.data['low']
        s1 = (2 * pivot) - self.data['high']
        r2 = pivot + (self.data['high'] - self.data['low'])
        s2 = pivot - (self.data['high'] - self.data['low'])
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[(self.data['close'] > s1) & (self.data['close'].shift(1) <= s1.shift(1))] = 1   # 价格上穿支撑位时买入
        self.signals[(self.data['close'] < r1) & (self.data['close'].shift(1) >= r1.shift(1))] = -1  # 价格下穿阻力位时卖出