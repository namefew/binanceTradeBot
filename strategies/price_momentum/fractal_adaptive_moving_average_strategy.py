"""
分形自适应移动平均线策略 (FRAMA)
根据价格波动性调整周期的移动平均线
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class FractalAdaptiveMovingAverageStrategy(BaseStrategy):
    """
    分形自适应移动平均线策略 (FRAMA)
    根据价格波动性调整周期的移动平均线
    """
    
    def __init__(self, period=16, transaction_cost=0.001, position_size=1.0):
        super().__init__("FRAMA Strategy", transaction_cost, indicator_short_name="FRAMA", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成FRAMA交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有high, low列
        required_columns = ['high', 'low']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算FRAMA
        price_range = (self.data['high'] + self.data['low']) / 2
        frama = pd.Series(0, index=self.data.index)
        
        # 初始化前N个值
        frama.iloc[:self.period] = price_range.iloc[:self.period]
        
        for i in range(self.period, len(self.data)):
            # 计算N1, N2, N3
            n1 = np.log(
                (price_range.iloc[i-self.period:i-self.period//2].max() - 
                 price_range.iloc[i-self.period:i-self.period//2].min()) / (self.period // 2)
            )
            
            n2 = np.log(
                (price_range.iloc[i-self.period//2:i].max() - 
                 price_range.iloc[i-self.period//2:i].min()) / (self.period // 2)
            )
            
            n3 = np.log(
                (price_range.iloc[i-self.period:i].max() - 
                 price_range.iloc[i-self.period:i].min()) / self.period
            )
            
            # 计算分形维度
            try:
                dimen = (n1 + n2 - n3) / n3
                alpha = np.exp(-4.6 * (dimen - 1))
                alpha = max(0.01, min(1, alpha))  # 限制alpha在0.01到1之间
            except:
                alpha = 0.5
            
            # 计算FRAMA
            frama.iloc[i] = alpha * price_range.iloc[i] + (1 - alpha) * frama.iloc[i-1]
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[price_range > frama] = 1   # 价格高于FRAMA时买入
        self.signals[price_range < frama] = -1  # 价格低于FRAMA时卖出