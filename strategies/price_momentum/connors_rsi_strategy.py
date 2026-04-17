"""
康纳斯相对强弱指数策略 (Connors RSI)
根据研报：三重RSI组合指标
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class ConnorsRSIStrategy(BaseStrategy):
    """
    康纳斯相对强弱指数策略 (Connors RSI)
    根据研报：三重RSI组合指标
    """
    
    def __init__(self, rsi_period=3, streak_period=2, percent_period=100, overbought=90, oversold=10, transaction_cost=0.001, position_size=1.0):
        super().__init__("Connors RSI Strategy", transaction_cost, indicator_short_name="Connors RSI", position_size=position_size)
        self.rsi_period = rsi_period
        self.streak_period = streak_period
        self.percent_period = percent_period
        self.overbought = overbought
        self.oversold = oversold
        
    def calculate_rsi(self, series, period):
        """
        计算RSI
        """
        delta = series.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def generate_signals(self):
        """
        生成Connors RSI交易信号
        当指标上穿/下穿阈值时产生交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算价格变化百分比
        price_pct_change = self.data['close'].pct_change()
        
        # 计算连续上涨/下跌天数
        def calculate_streak(series):
            streak = pd.Series(0, index=series.index)
            for i in range(1, len(series)):
                if series.iloc[i] > series.iloc[i-1]:
                    streak.iloc[i] = streak.iloc[i-1] + 1 if streak.iloc[i-1] >= 0 else 1
                elif series.iloc[i] < series.iloc[i-1]:
                    streak.iloc[i] = streak.iloc[i-1] - 1 if streak.iloc[i-1] <= 0 else -1
                else:
                    streak.iloc[i] = 0
            return streak
        
        streak = calculate_streak(self.data['close'])
        
        # 计算三个RSI
        rsi1 = self.calculate_rsi(self.data['close'], self.rsi_period)
        rsi2 = self.calculate_rsi(streak, self.streak_period)
        rsi3 = self.calculate_rsi(price_pct_change, self.percent_period)
        
        # 计算Connors RSI
        connors_rsi = (rsi1 + rsi2 + rsi3) / 3
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # Connors RSI上穿10时买入
        self.signals[(connors_rsi > self.oversold) & (connors_rsi.shift(1) <= self.oversold)] = 1
        # Connors RSI下穿90时卖出
        self.signals[(connors_rsi < self.overbought) & (connors_rsi.shift(1) >= self.overbought)] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)