"""
鳄鱼平衡策略
基于鳄鱼指标的平衡点策略
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class AlligatorBalanceStrategy(BaseStrategy):
    """
    鳄鱼平衡策略
    基于鳄鱼指标的平衡点策略
    """
    
    def __init__(self, transaction_cost=0.001, position_size=1.0):
        super().__init__("Alligator Balance Strategy", transaction_cost, indicator_short_name="Alligator Balance", position_size=position_size)
        
    def generate_signals(self):
        """
        生成鳄鱼平衡交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有high, low列
        required_columns = ['high', 'low']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算SMMA（平滑移动平均线）
        def smma(series, period):
            smma_values = pd.Series(0, index=series.index)
            smma_values.iloc[period-1] = series.iloc[:period].mean()
            for i in range(period, len(series)):
                smma_values.iloc[i] = (smma_values.iloc[i-1] * (period - 1) + series.iloc[i]) / period
            return smma_values
        
        # 计算鳄鱼的颚、牙齿和嘴唇
        jaw = smma((self.data['high'] + self.data['low']) / 2, 13).shift(8)
        teeth = smma((self.data['high'] + self.data['low']) / 2, 8).shift(5)
        lips = smma((self.data['high'] + self.data['low']) / 2, 5).shift(3)
        
        # 计算鳄鱼平衡点
        alligator_balance = (jaw + teeth + lips) / 3
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[self.data['close'] > alligator_balance] = 1   # 价格高于平衡点时买入
        self.signals[self.data['close'] < alligator_balance] = -1  # 价格低于平衡点时卖出