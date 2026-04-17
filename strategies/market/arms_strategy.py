"""
TRIN指标策略 (Arms Index)
衡量市场广度的指标
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class ArmsStrategy(BaseStrategy):
    """
    TRIN指标策略 (Arms Index)
    衡量市场广度的指标
    """
    
    def __init__(self, period=20, transaction_cost=0.001, position_size=1.0):
        super().__init__("Arms Strategy", transaction_cost, indicator_short_name="Arms", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成TRIN指标交易信号
        注意：此策略需要涨跌家数数据，实际应用中需要额外数据源
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close, volume列
        required_columns = ['close', 'volume']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 模拟涨跌家数（实际应用中需要真实数据）
        advancing_issues = pd.Series(np.random.randint(800, 1200, len(self.data)), index=self.data.index)
        declining_issues = pd.Series(np.random.randint(800, 1200, len(self.data)), index=self.data.index)
        advancing_volume = self.data['volume'] * np.random.uniform(0.4, 0.6, len(self.data))
        declining_volume = self.data['volume'] * np.random.uniform(0.4, 0.6, len(self.data))
        
        # 计算上涨下跌比率
        adr = (advancing_issues / declining_issues)
        avr = (advancing_volume / declining_volume)
        
        # 计算TRIN指标
        trin = avr / adr
        
        # 计算TRIN的移动平均
        trin_ma = trin.rolling(window=self.period).mean()
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[trin < trin_ma] = 1   # TRIN低于均值时买入（市场可能超卖）
        self.signals[trin > trin_ma] = -1  # TRIN高于均值时卖出（市场可能超买）