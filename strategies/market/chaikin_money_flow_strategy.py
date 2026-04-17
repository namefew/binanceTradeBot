"""
Chaikin资金流量策略
衡量资金流入流出的指标
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class ChaikinMoneyFlowStrategy(BaseStrategy):
    """
    Chaikin资金流量策略
    衡量资金流入流出的指标
    """
    
    def __init__(self, period=21, threshold=0, transaction_cost=0.001, position_size=1.0):
        super().__init__("Chaikin Money Flow Strategy", transaction_cost, indicator_short_name="CMF", position_size=position_size)
        self.period = period
        self.threshold = threshold
        
    def generate_signals(self):
        """
        生成Chaikin资金流量交易信号
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
        
        # 计算Chaikin资金流量
        cmf = money_flow.rolling(window=self.period).sum() / self.data['volume'].rolling(window=self.period).sum()
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[cmf > self.threshold] = 1   # 资金流量为正时买入
        self.signals[cmf < self.threshold] = -1  # 资金流量为负时卖出