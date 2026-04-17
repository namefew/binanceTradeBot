"""
资金流量指数策略 (Money Flow Index)
结合价格和成交量的动量指标
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class MoneyFlowIndexStrategy(BaseStrategy):
    """
    资金流量指数策略 (Money Flow Index)
    结合价格和成交量的动量指标
    """
    
    def __init__(self, period=14, overbought=80, oversold=20, transaction_cost=0.001, position_size=1.0):
        super().__init__("Money Flow Index Strategy", transaction_cost, indicator_short_name="MFI", position_size=position_size)
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
        
    def generate_signals(self):
        """
        生成资金流量指数交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有high, low, close, volume列
        required_columns = ['high', 'low', 'close', 'volume']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算典型价格
        typical_price = (self.data['high'] + self.data['low'] + self.data['close']) / 3
        
        # 计算资金流量
        money_flow = typical_price * self.data['volume']
        
        # 确定正负资金流量
        positive_flow = pd.Series(0, index=self.data.index)
        negative_flow = pd.Series(0, index=self.data.index)
        
        for i in range(1, len(self.data)):
            if typical_price.iloc[i] > typical_price.iloc[i-1]:
                positive_flow.iloc[i] = money_flow.iloc[i]
            elif typical_price.iloc[i] < typical_price.iloc[i-1]:
                negative_flow.iloc[i] = money_flow.iloc[i]
        
        # 计算正负资金流量的和
        positive_mf_sum = positive_flow.rolling(window=self.period).sum()
        negative_mf_sum = negative_flow.rolling(window=self.period).sum()
        
        # 计算资金流量比率
        money_flow_ratio = positive_mf_sum / negative_mf_sum
        
        # 计算MFI
        mfi = 100 - (100 / (1 + money_flow_ratio))
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[mfi < self.oversold] = 1   # 超卖时买入
        self.signals[mfi > self.overbought] = -1  # 超买时卖出