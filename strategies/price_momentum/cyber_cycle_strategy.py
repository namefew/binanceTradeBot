"""
Cyber Cycle策略
用于识别价格周期性波动的指标
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class CyberCycleStrategy(BaseStrategy):
    """
    Cyber Cycle策略
    用于识别价格周期性波动的指标
    """
    
    def __init__(self, alpha=0.07, transaction_cost=0.001, position_size=1.0):
        super().__init__("Cyber Cycle Strategy", transaction_cost, indicator_short_name="Cyber Cycle", position_size=position_size)
        self.alpha = alpha
        
    def generate_signals(self):
        """
        生成Cyber Cycle交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有high, low列
        required_columns = ['high', 'low']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算价格
        price = (self.data['high'] + self.data['low']) / 2
        
        # 计算平滑价格
        smooth = pd.Series(0, index=self.data.index)
        for i in range(2, len(price)):
            smooth.iloc[i] = (4 * price.iloc[i] + 3 * price.iloc[i-1] + 2 * price.iloc[i-2] + price.iloc[i-3]) / 10
        
        # 计算Cyber Cycle
        cycle = pd.Series(0, index=self.data.index)
        for i in range(6, len(smooth)):
            cycle.iloc[i] = (1 - 0.5 * self.alpha) ** 2 * (smooth.iloc[i] - 2 * smooth.iloc[i-1] + smooth.iloc[i-2]) + \
                           2 * (1 - self.alpha) * cycle.iloc[i-1] - (1 - self.alpha) ** 2 * cycle.iloc[i-2]
        
        # 计算信号线
        signal = pd.Series(0, index=self.data.index)
        for i in range(1, len(cycle)):
            signal.iloc[i] = (cycle.iloc[i] + cycle.iloc[i-1]) / 2
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[(cycle > signal) & (cycle.shift(1) <= signal.shift(1))] = 1   # Cycle上穿信号线时买入
        self.signals[(cycle < signal) & (cycle.shift(1) >= signal.shift(1))] = -1  # Cycle下穿信号线时卖出