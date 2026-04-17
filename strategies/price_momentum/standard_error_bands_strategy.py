"""
标准误差带策略 (Standard Error Bands)
根据研报：基于线性回归的标准误差通道策略
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class StandardErrorBandsStrategy(BaseStrategy):
    """
    标准误差带策略 (Standard Error Bands)
    根据研报：基于线性回归的标准误差通道策略
    """
    
    def __init__(self, period=20, multiplier=2, transaction_cost=0.001, position_size=1.0):
        super().__init__("Standard Error Bands Strategy", transaction_cost, indicator_short_name="Standard Error Bands", position_size=position_size)
        self.period = period
        self.multiplier = multiplier
        
    def linear_regression_with_error(self, series, period):
        """
        计算线性回归和标准误差
        """
        x = np.arange(period)
        lr_values = pd.Series(index=series.index)
        std_errors = pd.Series(index=series.index)
        
        for i in range(len(series)):
            if i < period - 1:
                lr_values.iloc[i] = np.nan
                std_errors.iloc[i] = np.nan
            else:
                y = series.iloc[i - period + 1:i + 1].values
                slope, intercept = np.polyfit(x, y, 1)
                lr_values.iloc[i] = slope * (period - 1) + intercept
                
                # 计算标准误差
                fitted_values = slope * x + intercept
                residuals = y - fitted_values
                std_error = np.sqrt(np.sum(residuals ** 2) / (period - 2))
                std_errors.iloc[i] = std_error
                
        return lr_values, std_errors
    
    def generate_signals(self):
        """
        生成Standard Error Bands交易信号
        当价格突破上下轨时产生交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算线性回归和标准误差
        lr_values, std_errors = self.linear_regression_with_error(self.data['close'], self.period)
        
        # 计算上下轨
        upper_band = lr_values + std_errors * self.multiplier
        lower_band = lr_values - std_errors * self.multiplier
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # 价格上穿上轨时买入
        self.signals[(self.data['close'] > upper_band) & (self.data['close'].shift(1) <= upper_band.shift(1))] = 1
        # 价格下穿下轨时卖出
        self.signals[(self.data['close'] < lower_band) & (self.data['close'].shift(1) >= lower_band.shift(1))] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)