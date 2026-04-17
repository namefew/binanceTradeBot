"""
去趋势价格振荡器策略 (DPO)
去除价格趋势以识别周期性高低点
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class DetrendedPriceOscillatorStrategy(BaseStrategy):
    """
    去趋势价格振荡器策略 (DPO)
    去除价格趋势以识别周期性高低点
    """
    
    def __init__(self, period=20, transaction_cost=0.001, position_size=1.0):
        super().__init__("Detrended Price Oscillator Strategy", transaction_cost, indicator_short_name="DPO", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成去趋势价格振荡器交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算DPO
        sma = self.data['close'].rolling(window=self.period).mean()
        shift_period = self.period // 2 + 1
        dpo = self.data['close'].shift(shift_period) - sma
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[(dpo > 0) & (dpo.shift(1) <= 0)] = 1   # DPO上穿零轴时买入
        self.signals[(dpo < 0) & (dpo.shift(1) >= 0)] = -1  # DPO下穿零轴时卖出