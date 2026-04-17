"""
McGinley动态指标策略
自动调整以适应市场速度的移动平均线
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class McGinleyDynamicStrategy(BaseStrategy):
    """
    McGinley动态指标策略
    自动调整以适应市场速度的移动平均线
    """
    
    def __init__(self, period=20, transaction_cost=0.001, position_size=1.0):
        super().__init__("McGinley Dynamic Strategy", transaction_cost, indicator_short_name="McGinley Dynamic", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成McGinley Dynamic交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算McGinley Dynamic
        md = pd.Series(0, index=self.data.index)
        md.iloc[0] = self.data['close'].iloc[0]
        
        for i in range(1, len(self.data)):
            # McGinley Dynamic公式
            md.iloc[i] = md.iloc[i-1] + (self.data['close'].iloc[i] - md.iloc[i-1]) / (self.period * ((self.data['close'].iloc[i] / md.iloc[i-1]) ** 4))
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[self.data['close'] > md] = 1   # 价格高于McGinley Dynamic时买入
        self.signals[self.data['close'] < md] = -1  # 价格低于McGinley Dynamic时卖出