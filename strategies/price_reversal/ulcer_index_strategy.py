"""
溃疡指数策略 (Ulcer Index)
根据研报：衡量价格下跌风险的指标
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class UlcerIndexStrategy(BaseStrategy):
    """
    溃疡指数策略 (Ulcer Index)
    根据研报：衡量价格下跌风险的指标
    """
    
    def __init__(self, period=14, transaction_cost=0.001, position_size=1.0):
        super().__init__("Ulcer Index Strategy", transaction_cost, indicator_short_name="Ulcer Index", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成Ulcer Index交易信号
        当Ulcer Index下降到一定程度时买入，上升到一定程度时卖出
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算最高价序列
        max_close = self.data['close'].rolling(window=self.period).max()
        
        # 计算跌幅百分比
        percent_drawdown = ((self.data['close'] - max_close) / max_close) * 100
        
        # 计算平方跌幅
        squared_drawdown = percent_drawdown ** 2
        
        # 计算Ulcer Index
        ulcer_index = np.sqrt(squared_drawdown.rolling(window=self.period).mean())
        
        # 生成信号 (简化版)
        self.signals = pd.Series(0, index=self.data.index)
        # 当Ulcer Index下降到较低水平时买入
        self.signals[(ulcer_index < 5) & (ulcer_index.shift(1) >= 5)] = 1
        # 当Ulcer Index上升到较高水平时卖出
        self.signals[(ulcer_index > 15) & (ulcer_index.shift(1) <= 15)] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)