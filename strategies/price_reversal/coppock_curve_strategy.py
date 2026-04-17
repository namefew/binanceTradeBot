"""
哥普克曲线策略 (Coppock Curve)
根据研报：一种长周期的动量指标，主要用于识别长期牛市的开始
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class CoppockCurveStrategy(BaseStrategy):
    """
    哥普克曲线策略 (Coppock Curve)
    根据研报：一种长周期的动量指标，主要用于识别长期牛市的开始
    """
    
    def __init__(self, short_period=11, long_period=14, wma_period=10, transaction_cost=0.001, position_size=1.0):
        super().__init__("Coppock Curve Strategy", transaction_cost, indicator_short_name="Coppock", position_size=position_size)
        self.short_period = short_period
        self.long_period = long_period
        self.wma_period = wma_period
        
    def generate_signals(self):
        """
        生成Coppock Curve交易信号
        当指标从负值向上突破0时买入，从正值向下跌破0时卖出
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算ROC
        roc_short = self.data['close'].pct_change(self.short_period)
        roc_long = self.data['close'].pct_change(self.long_period)
        
        # 计算ROC之和
        roc_sum = roc_short + roc_long
        
        # 计算WMA
        weights = np.arange(1, self.wma_period + 1)
        coppock = roc_sum.rolling(self.wma_period).apply(
            lambda x: np.dot(x, weights) / weights.sum(), raw=True)
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # 指标从负值向上突破0时买入
        self.signals[(coppock > 0) & (coppock.shift(1) <= 0)] = 1
        # 指标从正值向下跌破0时卖出
        self.signals[(coppock < 0) & (coppock.shift(1) >= 0)] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)