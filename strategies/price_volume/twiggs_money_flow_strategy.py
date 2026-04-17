"""
Twigg's 资金流量策略 (Twiggs Money Flow)
根据研报：衡量资金流入流出的指标
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class TwiggsMoneyFlowStrategy(BaseStrategy):
    """
    Twigg's 资金流量策略 (Twiggs Money Flow)
    根据研报：衡量资金流入流出的指标
    """
    
    def __init__(self, period=21, transaction_cost=0.001, position_size=1.0):
        super().__init__("Twiggs Money Flow Strategy", transaction_cost, indicator_short_name="TMF", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成Twiggs Money Flow交易信号
        当指标上穿/下穿零轴时产生交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有必要的列
        required_columns = ['high', 'low', 'close', 'volume']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算真实价格范围
        trh = np.maximum(self.data['high'], self.data['close'].shift(1))
        trl = np.minimum(self.data['low'], self.data['close'].shift(1))
        tr = trh - trl
        
        # 计算AD
        ad = (self.data['close'] - self.data['low']) - (self.data['high'] - self.data['close'])
        ad = ad / (self.data['high'] - self.data['low']) * self.data['volume']
        ad = ad.fillna(0)
        
        # 计算AD的修正版本
        modified_ad = ad * tr / (self.data['high'] - self.data['low'])
        modified_ad = modified_ad.fillna(0)
        
        # 计算TMF
        tmf = modified_ad.rolling(window=self.period).sum() / self.data['volume'].rolling(window=self.period).sum()
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # TMF上穿0时买入
        self.signals[(tmf > 0) & (tmf.shift(1) <= 0)] = 1
        # TMF下穿0时卖出
        self.signals[(tmf < 0) & (tmf.shift(1) >= 0)] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)