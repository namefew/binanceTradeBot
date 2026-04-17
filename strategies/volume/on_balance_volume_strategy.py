"""
能量潮指标策略 (On Balance Volume)
通过成交量确认价格趋势
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class OnBalanceVolumeStrategy(BaseStrategy):
    """
    能量潮指标策略 (On Balance Volume)
    通过成交量确认价格趋势
    """
    
    def __init__(self, transaction_cost=0.001, position_size=1.0):
        super().__init__("On Balance Volume Strategy", transaction_cost, indicator_short_name="On Balance Volume", position_size=position_size)
        
    def generate_signals(self):
        """
        生成能量潮指标交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close, volume列
        required_columns = ['close', 'volume']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算OBV
        obv = pd.Series(0, index=self.data.index)
        for i in range(1, len(self.data)):
            if self.data['close'].iloc[i] > self.data['close'].iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] + self.data['volume'].iloc[i]
            elif self.data['close'].iloc[i] < self.data['close'].iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] - self.data['volume'].iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]
        
        # 计算OBV的移动平均
        obv_ma = obv.rolling(window=10).mean()
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[obv > obv_ma] = 1   # OBV高于均值时买入
        self.signals[obv < obv_ma] = -1  # OBV低于均值时卖出