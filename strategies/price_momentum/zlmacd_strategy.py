"""
零滞后指数移动平均线MACD策略 (Zero Lag MACD)
根据研报：ZLMACD=(2*EMA(CLOSE,N1)-EMA(EMA(CLOSE,N1),N1))-(2*EMA(CLOSE,N2)-EMA(EMA(CLOSE,N2),N2))
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy

class ZLMACDStrategy(BaseStrategy):
    """
    零滞后指数移动平均线MACD策略 (Zero Lag MACD)
    根据研报：ZLMACD=(2*EMA(CLOSE,N1)-EMA(EMA(CLOSE,N1),N1))-(2*EMA(CLOSE,N2)-EMA(EMA(CLOSE,N2),N2))
    """
    
    def __init__(self, n1=20, n2=100, transaction_cost=0.001, position_size=1.0):
        super().__init__("ZLMACD Strategy", transaction_cost, indicator_short_name="ZLMACD", position_size=position_size)
        self.n1 = n1
        self.n2 = n2
        
    def generate_signals(self):
        """
        生成ZLMACD交易信号
        当ZLMACD上穿/下穿0时产生买入/卖出信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算DEMA(N1)
        ema1 = self.data['close'].ewm(span=self.n1).mean()
        ema_ema1 = ema1.ewm(span=self.n1).mean()
        dema1 = 2 * ema1 - ema_ema1
        
        # 计算DEMA(N2)
        ema2 = self.data['close'].ewm(span=self.n2).mean()
        ema_ema2 = ema2.ewm(span=self.n2).mean()
        dema2 = 2 * ema2 - ema_ema2
        
        # 计算ZLMACD
        zlmacd = dema1 - dema2
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # ZLMACD上穿0时买入
        self.signals[(zlmacd > 0) & (zlmacd.shift(1) <= 0)] = 1
        # ZLMACD下穿0时卖出
        self.signals[(zlmacd < 0) & (zlmacd.shift(1) >= 0)] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)