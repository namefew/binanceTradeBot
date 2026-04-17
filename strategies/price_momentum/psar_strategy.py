"""
抛物线SAR策略 (Parabolic Stop and Reverse)
与前面的ParabolicSARStrategy类似，但实现方式略有不同
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class PSARStrategy(BaseStrategy):
    """
    抛物线SAR策略 (Parabolic Stop and Reverse)
    与前面的ParabolicSARStrategy类似，但实现方式略有不同
    """
    
    def __init__(self, step=0.02, max_step=0.2, transaction_cost=0.001, position_size=1.0):
        super().__init__("PSAR Strategy", transaction_cost, indicator_short_name="PSAR", position_size=position_size)
        self.step = step
        self.max_step = max_step
        
    def generate_signals(self):
        """
        生成PSAR交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有high, low, close列
        required_columns = ['high', 'low', 'close']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 初始化变量
        sar = pd.Series(0.0, index=self.data.index)
        trend = pd.Series(0, index=self.data.index)  # 1表示上升趋势，-1表示下降趋势
        ep = pd.Series(0.0, index=self.data.index)   # 极值点
        af = pd.Series(0.0, index=self.data.index)   # 加速因子
        
        # 第一天
        sar.iloc[0] = self.data['close'].iloc[0]
        trend.iloc[0] = 1
        ep.iloc[0] = self.data['high'].iloc[0]
        af.iloc[0] = self.step
        
        for i in range(1, len(self.data)):
            sar.iloc[i] = sar.iloc[i-1] + af.iloc[i-1] * (ep.iloc[i-1] - sar.iloc[i-1])
            
            if trend.iloc[i-1] > 0:  # 上升趋势
                if self.data['low'].iloc[i] < sar.iloc[i]:
                    # 趋势反转
                    trend.iloc[i] = -1
                    sar.iloc[i] = ep.iloc[i-1]
                    ep.iloc[i] = self.data['low'].iloc[i]
                    af.iloc[i] = self.step
                else:
                    trend.iloc[i] = 1
                    if self.data['high'].iloc[i] > ep.iloc[i-1]:
                        ep.iloc[i] = self.data['high'].iloc[i]
                        af.iloc[i] = min(af.iloc[i-1] + self.step, self.max_step)
                    else:
                        af.iloc[i] = af.iloc[i-1]
                    sar.iloc[i] = min(sar.iloc[i], self.data['low'].iloc[i-1], self.data['low'].iloc[i])
            else:  # 下降趋势
                if self.data['high'].iloc[i] > sar.iloc[i]:
                    # 趋势反转
                    trend.iloc[i] = 1
                    sar.iloc[i] = ep.iloc[i-1]
                    ep.iloc[i] = self.data['high'].iloc[i]
                    af.iloc[i] = self.step
                else:
                    trend.iloc[i] = -1
                    if self.data['low'].iloc[i] < ep.iloc[i-1]:
                        ep.iloc[i] = self.data['low'].iloc[i]
                        af.iloc[i] = min(af.iloc[i-1] + self.step, self.max_step)
                    else:
                        af.iloc[i] = af.iloc[i-1]
                    sar.iloc[i] = max(sar.iloc[i], self.data['high'].iloc[i-1], self.data['high'].iloc[i])
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[trend == 1] = 1   # 上升趋势时买入
        self.signals[trend == -1] = -1 # 下降趋势时卖出