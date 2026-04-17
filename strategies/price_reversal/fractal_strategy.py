"""
分形策略 (Fractal Strategy)
基于分形几何的价格模式识别策略
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class FractalStrategy(BaseStrategy):
    """
    分形策略 (Fractal Strategy)
    基于分形几何的价格模式识别策略
    """
    
    def __init__(self, period=5, transaction_cost=0.001, position_size=1.0):
        super().__init__("Fractal Strategy", transaction_cost, indicator_short_name="Fractal", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成分形交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有high, low列
        required_columns = ['high', 'low']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算分形
        # 上升分形（看跌）- 延迟确认，不使用未来数据
        bear_fractals = pd.Series(False, index=self.data.index)
        for i in range(4, len(self.data)):
            if (self.data['high'].iloc[i - 2] > self.data['high'].iloc[i - 3] and
                    self.data['high'].iloc[i - 2] > self.data['high'].iloc[i - 4] and
                    self.data['high'].iloc[i - 2] > self.data['high'].iloc[i - 1] and
                    self.data['high'].iloc[i - 2] > self.data['high'].iloc[i]):
                bear_fractals.iloc[i] = True  # 在分形点之后确认信号
                
        # 下降分形（看涨）
        bull_fractals = pd.Series(False, index=self.data.index)
        for i in range(4, len(self.data) ):
            if (self.data['low'].iloc[i-2] < self.data['low'].iloc[i-3] and
                self.data['low'].iloc[i-2] < self.data['low'].iloc[i-4] and
                self.data['low'].iloc[i-2] < self.data['low'].iloc[i-1] and
                self.data['low'].iloc[i-2] < self.data['low'].iloc[i]):
                bull_fractals.iloc[i] = True
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[bull_fractals] = 1   # 出现下降分形时买入
        self.signals[bear_fractals] = -1  # 出现上升分形时卖出