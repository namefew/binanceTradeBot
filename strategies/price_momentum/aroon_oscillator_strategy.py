"""
阿隆振荡器策略 (Aroon Oscillator)
根据研报：Aroon Oscillator = Aroon Up - Aroon Down
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class AroonOscillatorStrategy(BaseStrategy):
    """
    阿隆振荡器策略 (Aroon Oscillator)
    根据研报：Aroon Oscillator = Aroon Up - Aroon Down
    """
    
    def __init__(self, period=25, transaction_cost=0.001, position_size=1.0):
        super().__init__("Aroon Oscillator Strategy", transaction_cost, indicator_short_name="Aroon Oscillator", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成Aroon Oscillator交易信号
        当Aroon Oscillator上穿0时买入，下穿0时卖出
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有必要的列
        required_columns = ['high', 'low']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算Aroon Up和Aroon Down
        # Aroon Up = ((周期 - 周期内最高价以来的天数) / 周期) * 100
        rolling_high = self.data['high'].rolling(window=self.period)
        days_since_high = rolling_high.apply(lambda x: (self.period - 1) - x[::-1].argmax(), raw=True)
        aroon_up = ((self.period - days_since_high) / self.period) * 100
        
        # Aroon Down = ((周期 - 周期内最低价以来的天数) / 周期) * 100
        rolling_low = self.data['low'].rolling(window=self.period)
        days_since_low = rolling_low.apply(lambda x: (self.period - 1) - x[::-1].argmin(), raw=True)
        aroon_down = ((self.period - days_since_low) / self.period) * 100
        
        # 计算Aroon Oscillator
        aroon_osc = aroon_up - aroon_down
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # Aroon Oscillator上穿0时买入
        self.signals[(aroon_osc > 0) & (aroon_osc.shift(1) <= 0)] = 1
        # Aroon Oscillator下穿0时卖出
        self.signals[(aroon_osc < 0) & (aroon_osc.shift(1) >= 0)] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)