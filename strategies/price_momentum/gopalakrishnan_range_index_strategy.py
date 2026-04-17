"""
戈帕拉克里希南范围指数策略 (Gopalakrishnan Range Index, GRI)
根据研报：衡量价格波动范围的指标
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class GopalakrishnanRangeIndexStrategy(BaseStrategy):
    """
    戈帕拉克里希南范围指数策略 (Gopalakrishnan Range Index, GRI)
    根据研报：衡量价格波动范围的指标
    """
    
    def __init__(self, period=14, transaction_cost=0.001, position_size=1.0):
        super().__init__("Gopalakrishnan Range Index Strategy", transaction_cost, indicator_short_name="GRI", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成GRI交易信号
        当指标发生转折时产生交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有必要的列
        required_columns = ['high', 'low']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算真实范围
        true_range = self.data['high'] - self.data['low']
        
        # 计算TR的最高值和最低值
        tr_high = true_range.rolling(window=self.period).max()
        tr_low = true_range.rolling(window=self.period).min()
        
        # 计算GRI
        gri = 100 * np.log10(tr_high / tr_low) / np.log10(self.period)
        
        # 计算GRI信号线
        gri_signal = gri.rolling(window=3).mean()
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # GRI上穿信号线时买入
        self.signals[(gri > gri_signal) & (gri.shift(1) <= gri_signal.shift(1))] = 1
        # GRI下穿信号线时卖出
        self.signals[(gri < gri_signal) & (gri.shift(1) >= gri_signal.shift(1))] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)