"""
可变指数动态平均线策略 (VIDYA)
根据市场波动性调整的移动平均线
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class VariableIndexDynamicAverageStrategy(BaseStrategy):
    """
    可变指数动态平均线策略 (VIDYA)
    根据市场波动性调整的移动平均线
    """
    
    def __init__(self, period=14, alpha=0.2, transaction_cost=0.001, position_size=1.0):
        super().__init__("VIDYA Strategy", transaction_cost, indicator_short_name="VIDYA", position_size=position_size)
        self.period = period
        self.alpha = alpha
        
    def generate_signals(self):
        """
        生成VIDYA交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算价格变化
        price_change = self.data['close'].diff().abs()
        
        # 计算波动性
        volatility = price_change.rolling(window=self.period).std()
        
        # 计算变异系数
        mean_price = self.data['close'].rolling(window=self.period).mean()
        coefficient_of_variation = volatility / mean_price
        
        # 计算动态平滑因子
        alpha_t = self.alpha * coefficient_of_variation
        alpha_t = alpha_t.clip(0.01, 0.99)  # 限制在合理范围内
        
        # 计算VIDYA
        vidya = pd.Series(0, index=self.data.index)
        vidya.iloc[0] = self.data['close'].iloc[0]
        
        for i in range(1, len(self.data)):
            vidya.iloc[i] = alpha_t.iloc[i] * self.data['close'].iloc[i] + (1 - alpha_t.iloc[i]) * vidya.iloc[i-1]
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[self.data['close'] > vidya] = 1   # 价格高于VIDYA时买入
        self.signals[self.data['close'] < vidya] = -1  # 价格低于VIDYA时卖出