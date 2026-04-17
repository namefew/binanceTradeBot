"""
惯性指标策略 (Inertia Indicator)
根据研报：基于相对离散累积(RSI)和线性回归的指标
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class InertiaStrategy(BaseStrategy):
    """
    惯性指标策略 (Inertia Indicator)
    根据研报：基于相对离散累积(RSI)和线性回归的指标
    """
    
    def __init__(self, period=20, signal_period=5, transaction_cost=0.001, position_size=1.0):
        super().__init__("Inertia Strategy", transaction_cost, indicator_short_name="Inertia", position_size=position_size)
        self.period = period
        self.signal_period = signal_period
        
    def linear_regression_slope(self, series, period):
        """
        计算线性回归斜率
        """
        x = np.arange(period)
        slopes = series.rolling(window=period).apply(
            lambda y: np.polyfit(x, y, 1)[0] if len(y) == period else np.nan, 
            raw=True
        )
        return slopes
    
    def generate_signals(self):
        """
        生成Inertia交易信号
        当Inertia指标上穿/下穿零轴时产生交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有必要的列
        required_columns = ['high', 'low', 'close']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算典型价格
        typical_price = (self.data['high'] + self.data['low'] + self.data['close']) / 3
        
        # 计算RSI
        delta = typical_price.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=self.period).mean()
        avg_loss = loss.rolling(window=self.period).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        # 计算Inertia指标 (RSI的线性回归斜率)
        inertia = self.linear_regression_slope(rsi, self.period)
        
        # 计算信号线
        inertia_signal = inertia.rolling(window=self.signal_period).mean()
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # Inertia上穿信号线时买入
        self.signals[(inertia > inertia_signal) & (inertia.shift(1) <= inertia_signal.shift(1))] = 1
        # Inertia下穿信号线时卖出
        self.signals[(inertia < inertia_signal) & (inertia.shift(1) >= inertia_signal.shift(1))] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)