"""
累计摆动指标策略 (Accumulation Swing Index, ASI)
根据研报：ASI用于测量市场趋势的强度和方向
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class ASIStrategy(BaseStrategy):
    """
    累计摆动指标策略 (Accumulation Swing Index, ASI)
    根据研报：ASI用于测量市场趋势的强度和方向
    """
    
    def __init__(self, limit_move_value=0.5, transaction_cost=0.001, position_size=1.0):
        super().__init__("ASI Strategy", transaction_cost, indicator_short_name="ASI", position_size=position_size)
        self.limit_move_value = limit_move_value
        
    def generate_signals(self):
        """
        生成ASI交易信号
        当ASI上穿/下穿其移动平均线时产生买入/卖出信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有必要的列
        required_columns = ['open', 'high', 'low', 'close']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算ASI
        # 1. 计算各种价格差
        c_y = self.data['close'] - self.data['close'].shift(1)
        h_y = self.data['high'] - self.data['close'].shift(1)
        l_y = self.data['low'] - self.data['close'].shift(1)
        h_c = self.data['high'] - self.data['close']
        l_c = self.data['low'] - self.data['close']
        h_l = self.data['high'] - self.data['low']
        c_o = abs(self.data['close'] - self.data['open'])
        h_o = abs(self.data['high'] - self.data['open'].shift(1))
        l_o = abs(self.data['low'] - self.data['open'].shift(1))
        
        # 2. 确定R值
        r = pd.DataFrame({
            'r1': h_y - (l_y / 2) + (c_y / 4),
            'r2': h_c - (l_c / 2) + (c_y / 4),
            'r3': h_l + (c_y / 4)
        }).max(axis=1)
        
        # 3. 确定K值
        k = pd.DataFrame({
            'k1': h_l,
            'k2': h_o,
            'k3': l_o
        }).max(axis=1)
        
        # 4. 计算T值
        t = pd.DataFrame({
            't1': h_l,
            't2': c_o.shift(1)
        }).max(axis=1)
        
        # 5. 计算SI
        si = (c_y + (c_y / 2) + (h_y / 4) + (l_y / 4)) * (k / r) * (self.limit_move_value / t)
        
        # 6. 计算ASI
        asi = si.cumsum()
        
        # 计算ASI的移动平均线
        asi_ma = asi.rolling(window=20).mean()
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # ASI上穿ASI_MA时买入
        self.signals[(asi > asi_ma) & (asi.shift(1) <= asi_ma.shift(1))] = 1
        # ASI下穿ASI_MA时卖出
        self.signals[(asi < asi_ma) & (asi.shift(1) >= asi_ma.shift(1))] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)