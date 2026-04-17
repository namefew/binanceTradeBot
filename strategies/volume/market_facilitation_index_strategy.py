"""
市场促进指数策略 (Market Facilitation Index)
衡量价格变动效率的指标
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class MarketFacilitationIndexStrategy(BaseStrategy):
    """
    市场促进指数策略 (Market Facilitation Index)
    衡量价格变动效率的指标
    """
    
    def __init__(self, transaction_cost=0.001, position_size=1.0):
        super().__init__("Market Facilitation Index Strategy", transaction_cost, indicator_short_name="MFI", position_size=position_size)
        
    def generate_signals(self):
        """
        生成市场促进指数交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有high, low, volume列
        required_columns = ['high', 'low', 'volume']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算市场促进指数
        mfi = (self.data['high'] - self.data['low']) / self.data['volume']
        
        # 计算变化
        mfi_change = mfi - mfi.shift(1)
        volume_change = self.data['volume'] - self.data['volume'].shift(1)
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # 价格变化增加且成交量减少时买入（高效变化）
        self.signals[(mfi_change > 0) & (volume_change < 0)] = 1
        # 价格变化减少且成交量增加时卖出（低效变化）
        self.signals[(mfi_change < 0) & (volume_change > 0)] = -1