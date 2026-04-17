"""
能量K线震荡器策略 (Ergodic Candlestick Oscillator)
根据研报：基于K线形态的能量震荡指标
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class ErgodicCandlestickOscillatorStrategy(BaseStrategy):
    """
    能量K线震荡器策略 (Ergodic Candlestick Oscillator)
    根据研报：基于K线形态的能量震荡指标
    """
    
    def __init__(self, period=14, transaction_cost=0.001, position_size=1.0):
        super().__init__("Ergodic Candlestick Oscillator Strategy", transaction_cost, indicator_short_name="ECO", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成Ergodic Candlestick Oscillator交易信号
        当指标上穿/下穿阈值时产生交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有必要的列
        required_columns = ['open', 'high', 'low', 'close']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算K线实体
        body = self.data['close'] - self.data['open']
        
        # 计算上影线和下影线
        upper_shadow = self.data['high'] - np.maximum(self.data['close'], self.data['open'])
        lower_shadow = np.minimum(self.data['close'], self.data['open']) - self.data['low']
        
        # 计算EMA
        ema_body = body.ewm(span=self.period).mean()
        ema_upper_shadow = upper_shadow.ewm(span=self.period).mean()
        ema_lower_shadow = lower_shadow.ewm(span=self.period).mean()
        
        # 计算能量震荡器
        eco = ema_body / (ema_body + ema_upper_shadow + ema_lower_shadow) * 100
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # ECO上穿50时买入
        self.signals[(eco > 50) & (eco.shift(1) <= 50)] = 1
        # ECO下穿50时卖出
        self.signals[(eco < 50) & (eco.shift(1) >= 50)] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)