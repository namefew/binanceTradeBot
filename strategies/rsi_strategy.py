"""
RSI超买超卖策略
当RSI低于超卖线时买入，高于超买线时卖出
"""
import pandas as pd
import numpy as np
from .base_strategy import Strategy, Signal


class RSIStrategy(Strategy):
    """RSI策略"""
    
    def __init__(self, period: int = 14, oversold: float = 30, overbought: float = 70):
        super().__init__(name=f"RSI_{period}_{oversold}_{overbought}")
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
    
    def calculate_rsi(self, prices: pd.Series, period: int) -> pd.Series:
        """计算RSI指标"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def generate_signal(self, data: pd.DataFrame, current_index: int) -> str:
        """
        基于RSI生成信号
        
        Args:
            data: K线数据
            current_index: 当前索引
            
        Returns:
            交易信号
        """
        # 确保有足够的数据
        if current_index < self.period + 1:
            return Signal.HOLD
        
        # 计算RSI
        close_prices = data['close'].iloc[:current_index + 1]
        rsi_series = self.calculate_rsi(close_prices, self.period)
        current_rsi = rsi_series.iloc[-1]
        prev_rsi = rsi_series.iloc[-2] if len(rsi_series) > 1 else current_rsi
        
        # 超卖区域买入（RSI从下方穿越超卖线）
        if prev_rsi <= self.oversold and current_rsi > self.oversold:
            return Signal.BUY
        
        # 超买区域卖出（RSI从上方穿越超买线）
        if prev_rsi >= self.overbought and current_rsi < self.overbought:
            return Signal.SELL
        
        return Signal.HOLD
