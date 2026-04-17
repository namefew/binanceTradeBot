"""
区间震荡线(Detrended Price Oscillator, DPO)策略
根据研报，DPO=CLOSE-REF(MA(CLOSE,N),N/2+1)，N=20
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy

class DPOStrategy(BaseStrategy):
    """
    区间震荡线(Detrended Price Oscillator, DPO)策略
    根据研报，DPO=CLOSE-REF(MA(CLOSE,N),N/2+1)，N=20
    """
    
    def __init__(self, n=20, transaction_cost=0.001, position_size=1.0):
        super().__init__("DPO Strategy", transaction_cost, indicator_short_name="DPO", position_size=position_size)
        self.n = n
        
    def generate_signals(self):
        """
        生成DPO交易信号
        当DPO上穿0时买入，下穿0时卖出
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算DPO
        # 1. 计算收盘价的N日简单移动平均
        ma = self.data['close'].rolling(window=self.n).mean()
        
        # 2. 将移动平均线向前移动N/2+1位
        shifted_ma = ma.shift(int(self.n/2 + 1))
        
        # 3. 计算DPO = CLOSE - REF(MA(CLOSE,N),N/2+1)
        dpo = self.data['close'] - shifted_ma
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[dpo > 0] = 1    # DPO>0时买入
        self.signals[dpo < 0] = -1   # DPO<0时卖出
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)