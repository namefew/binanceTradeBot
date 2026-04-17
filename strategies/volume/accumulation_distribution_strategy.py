"""
累积/派发指标策略 (Accumulation/Distribution)
衡量资金流入流出的指标
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class AccumulationDistributionStrategy(BaseStrategy):
    """
    累积/派发指标策略 (Accumulation/Distribution)
    衡量资金流入流出的指标
    """
    
    def __init__(self, transaction_cost=0.001, position_size=1.0):
        super().__init__("Accumulation/Distribution Strategy", transaction_cost, indicator_short_name="A/D", position_size=position_size)
        
    def generate_signals(self):
        """
        生成累积/派发指标交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有high, low, close, volume列
        required_columns = ['high', 'low', 'close', 'volume']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算CLV（收盘价位置值）
        clv = ((self.data['close'] - self.data['low']) - (self.data['high'] - self.data['close'])) / (self.data['high'] - self.data['low'])
        clv = clv.fillna(0)  # 处理除零情况
        
        # 计算资金流量
        money_flow = clv * self.data['volume']
        
        # 计算累积/派发线
        adl = money_flow.cumsum()
        
        # 计算ADL的移动平均
        adl_ma = adl.rolling(window=10).mean()
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[adl > adl_ma] = 1   # ADL高于均值时买入
        self.signals[adl < adl_ma] = -1  # ADL低于均值时卖出