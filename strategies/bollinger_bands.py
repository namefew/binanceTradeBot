"""
布林带策略
价格触及下轨买入，触及上轨卖出
"""
import pandas as pd
import numpy as np
from .base_strategy import Strategy, Signal


class BollingerBandsStrategy(Strategy):
    """布林带策略"""
    
    def __init__(self, period: int = 20, num_std: float = 2.0):
        super().__init__(name=f"BB_{period}_{num_std}")
        self.period = period
        self.num_std = num_std
    
    def calculate_bollinger_bands(self, prices: pd.Series) -> tuple:
        """计算布林带"""
        middle_band = prices.rolling(window=self.period).mean()
        std_dev = prices.rolling(window=self.period).std()
        upper_band = middle_band + (std_dev * self.num_std)
        lower_band = middle_band - (std_dev * self.num_std)
        return upper_band, middle_band, lower_band
    
    def generate_signal(self, data: pd.DataFrame, current_index: int) -> str:
        """
        基于布林带生成信号
        
        Args:
            data: K线数据
            current_index: 当前索引
            
        Returns:
            交易信号
        """
        # 确保有足够的数据
        if current_index < self.period:
            return Signal.HOLD
        
        # 计算布林带
        close_prices = data['close'].iloc[:current_index + 1]
        upper, middle, lower = self.calculate_bollinger_bands(close_prices)
        
        current_price = data['close'].iloc[current_index]
        prev_price = data['close'].iloc[current_index - 1]
        
        current_lower = lower.iloc[-1]
        current_upper = upper.iloc[-1]
        prev_lower = lower.iloc[-2] if len(lower) > 1 else current_lower
        prev_upper = upper.iloc[-2] if len(upper) > 1 else current_upper
        
        # 价格从下方向上突破下轨，买入信号
        if prev_price <= prev_lower and current_price > current_lower:
            return Signal.BUY
        
        # 价格从上方向下跌破上轨，卖出信号
        if prev_price >= prev_upper and current_price < current_upper:
            return Signal.SELL
        
        return Signal.HOLD
