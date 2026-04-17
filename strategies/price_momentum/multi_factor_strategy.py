"""
多因子策略
结合多个技术指标的信号
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class MultiFactorStrategy(BaseStrategy):
    """
    多因子策略
    结合多个技术指标的信号
    """
    
    def __init__(self, transaction_cost=0.001, position_size=1.0):
        super().__init__("Multi-Factor Strategy", transaction_cost, indicator_short_name="Multi-Factor", position_size=position_size)
        
    def generate_signals(self):
        """
        生成多因子交易信号
        结合移动平均线、RSI和MACD信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有必要的列
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 1. 移动平均线信号
        short_ma = self.data['close'].rolling(window=5).mean()
        long_ma = self.data['close'].rolling(window=20).mean()
        ma_signal = pd.Series(0, index=self.data.index)
        ma_signal[short_ma > long_ma] = 1
        ma_signal[short_ma < long_ma] = -1
        
        # 2. RSI信号
        delta = self.data['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        rsi_signal = pd.Series(0, index=self.data.index)
        rsi_signal[rsi < 30] = 1
        rsi_signal[rsi > 70] = -1
        
        # 3. MACD信号
        exp1 = self.data['close'].ewm(span=12).mean()
        exp2 = self.data['close'].ewm(span=26).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9).mean()
        macd_signal = pd.Series(0, index=self.data.index)
        macd_signal[macd > signal] = 1
        macd_signal[macd < signal] = -1
        
        # 合并信号（只有当至少两个指标给出相同信号时才交易）
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[(ma_signal == 1) & (rsi_signal == 1)] = 1
        self.signals[(ma_signal == 1) & (macd_signal == 1)] = 1
        self.signals[(rsi_signal == 1) & (macd_signal == 1)] = 1
        self.signals[(ma_signal == -1) & (rsi_signal == -1)] = -1
        self.signals[(ma_signal == -1) & (macd_signal == -1)] = -1
        self.signals[(rsi_signal == -1) & (macd_signal == -1)] = -1