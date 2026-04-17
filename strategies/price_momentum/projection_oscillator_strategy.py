"""
投影震荡器策略 (Projection Oscillator)
根据研报：基于线性回归预测的震荡指标
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class ProjectionOscillatorStrategy(BaseStrategy):
    """
    投影震荡器策略 (Projection Oscillator)
    根据研报：基于线性回归预测的震荡指标
    """
    
    def __init__(self, period=14, smooth_period=3, transaction_cost=0.001, position_size=1.0):
        super().__init__("Projection Oscillator Strategy", transaction_cost, indicator_short_name="Projection Oscillator", position_size=position_size)
        self.period = period
        self.smooth_period = smooth_period
        
    def generate_signals(self):
        """
        生成Projection Oscillator交易信号
        当指标上穿/下穿阈值时产生交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有必要的列
        required_columns = ['high', 'low', 'close']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算线性回归预测值
        x = np.arange(self.period)
        projected_high = self.data['high'].rolling(window=self.period).apply(
            lambda y: np.poly1d(np.polyfit(x, y, 1))(self.period-1) if len(y) == self.period else np.nan,
            raw=True
        )
        
        projected_low = self.data['low'].rolling(window=self.period).apply(
            lambda y: np.poly1d(np.polyfit(x, y, 1))(self.period-1) if len(y) == self.period else np.nan,
            raw=True
        )
        
        # 计算Projection Oscillator
        po = ((self.data['close'] - projected_low) / (projected_high - projected_low)) * 100
        po_smooth = po.rolling(window=self.smooth_period).mean()
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # PO上穿30时买入
        self.signals[(po_smooth > 30) & (po_smooth.shift(1) <= 30)] = 1
        # PO下穿70时卖出
        self.signals[(po_smooth < 70) & (po_smooth.shift(1) >= 70)] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)