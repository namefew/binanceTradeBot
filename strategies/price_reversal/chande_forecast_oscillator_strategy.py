"""
钱德预测振荡器策略 (Chande Forecast Oscillator, CFO)
根据研报：衡量价格与线性回归预测值之间的偏差
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class ChandeForecastOscillatorStrategy(BaseStrategy):
    """
    钱德预测振荡器策略 (Chande Forecast Oscillator, CFO)
    根据研报：衡量价格与线性回归预测值之间的偏差
    """
    
    def __init__(self, period=14, transaction_cost=0.001, position_size=1.0):
        super().__init__("Chande Forecast Oscillator Strategy", transaction_cost, indicator_short_name="CFO", position_size=position_size)
        self.period = period
        
    def linear_regression_forecast(self, series, period):
        """
        计算线性回归预测值
        """
        x = np.arange(period)
        forecasts = series.rolling(window=period).apply(
            lambda y: np.poly1d(np.polyfit(x, y, 1))(period-1) if len(y) == period else np.nan,
            raw=True
        )
        return forecasts
    
    def generate_signals(self):
        """
        生成CFO交易信号
        当CFO上穿/下穿零轴时产生交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算线性回归预测值
        forecast = self.linear_regression_forecast(self.data['close'], self.period)
        
        # 计算CFO
        cfo = (self.data['close'] - forecast) / self.data['close'] * 100
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # CFO上穿零轴时买入
        self.signals[(cfo > 0) & (cfo.shift(1) <= 0)] = 1
        # CFO下穿零轴时卖出
        self.signals[(cfo < 0) & (cfo.shift(1) >= 0)] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)