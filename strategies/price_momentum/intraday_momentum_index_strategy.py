"""
日内动量指数策略 (Intraday Momentum Index, IMI)
根据研报：衡量日内价格变动的动量指标
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class IntradayMomentumIndexStrategy(BaseStrategy):
    """
    日内动量指数策略 (Intraday Momentum Index, IMI)
    根据研报：衡量日内价格变动的动量指标
    """
    
    def __init__(self, period=14, overbought=70, oversold=30, transaction_cost=0.001, position_size=1.0):
        super().__init__("Intraday Momentum Index Strategy", transaction_cost, indicator_short_name="IMI", position_size=position_size)
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
        
    def generate_signals(self):
        """
        生成IMI交易信号
        当指标上穿/下穿阈值时产生交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有必要的列
        required_columns = ['open', 'close']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算上涨和下跌的日内动量
        price_diff = self.data['close'] - self.data['open']
        up_days = price_diff.where(price_diff > 0, 0)
        down_days = (-price_diff).where(price_diff < 0, 0)
        
        # 计算平均上涨和下跌动量
        avg_up = up_days.rolling(window=self.period).mean()
        avg_down = down_days.rolling(window=self.period).mean()
        
        # 计算IMI
        imi = 100 * avg_up / (avg_up + avg_down)
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # IMI上穿30时买入
        self.signals[(imi > self.oversold) & (imi.shift(1) <= self.oversold)] = 1
        # IMI下穿70时卖出
        self.signals[(imi < self.overbought) & (imi.shift(1) >= self.overbought)] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)