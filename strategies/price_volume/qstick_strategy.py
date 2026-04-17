"""
Qstick指标策略
衡量收盘价与开盘价差值的移动平均
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class QstickStrategy(BaseStrategy):
    """
    Qstick指标策略
    衡量收盘价与开盘价差值的移动平均
    """
    
    def __init__(self, period=20, transaction_cost=0.001, position_size=1.0):
        super().__init__("Qstick Strategy", transaction_cost, indicator_short_name="Qstick", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成Qstick指标交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有open, close列
        required_columns = ['open', 'close']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算收盘价与开盘价的差值
        close_open_diff = self.data['close'] - self.data['open']
        
        # 计算Qstick
        qstick = close_open_diff.rolling(window=self.period).mean()
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[qstick > 0] = 1   # Qstick为正时买入
        self.signals[qstick < 0] = -1  # Qstick为负时卖出
        
        # 添加指标到数据中
        self.data['qstick'] = qstick
        
    def calculate_positions(self):
        """
        计算持仓
        """
        if self.signals is None:
            raise ValueError("请先生成信号")
            
        # 根据信号计算持仓
        self.positions = self.signals.shift(1).fillna(0)