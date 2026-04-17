"""
动态动量指数策略 (Dynamic Momentum Index)
根据研报：根据市场波动性调整计算周期的动量指标
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class DynamicMomentumIndexStrategy(BaseStrategy):
    """
    动态动量指数策略 (Dynamic Momentum Index)
    根据研报：根据市场波动性调整计算周期的动量指标
    """
    
    def __init__(self, period=14, volatility_period=10, transaction_cost=0.001, position_size=1.0):
        super().__init__("Dynamic Momentum Index Strategy", transaction_cost, indicator_short_name="DMI", position_size=position_size)
        self.period = period
        self.volatility_period = volatility_period
        
    def generate_signals(self):
        """
        生成Dynamic Momentum Index交易信号
        当指标上穿/下穿阈值时产生交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算波动率
        volatility = self.data['close'].pct_change().rolling(window=self.volatility_period).std()
        
        # 计算动态周期 (简化处理)
        volatility_mean = volatility.rolling(window=20).mean()
        # 避免除以零的情况
        volatility_ratio = volatility / volatility_mean
        volatility_ratio = volatility_ratio.fillna(1)  # 填充NaN值
        dynamic_period = np.round(14 * volatility_ratio).astype(int)
        dynamic_period = np.clip(dynamic_period, 5, 30)  # 限制周期在5-30之间
        
        # 计算动态RSI (简化版)
        delta = self.data['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # 使用动态周期计算平均值
        avg_gain = pd.Series(index=self.data.index, dtype=float)
        avg_loss = pd.Series(index=self.data.index, dtype=float)
        
        # 使用更简单的方法计算动态移动平均
        for i in range(len(self.data)):
            period = dynamic_period.iloc[i]
            if i >= period:
                avg_gain.iloc[i] = gain.iloc[i-period+1:i+1].mean()
                avg_loss.iloc[i] = loss.iloc[i-period+1:i+1].mean()
        
        # 避免除以零和无穷大的情况
        rs = avg_gain / avg_loss
        rs = rs.replace([np.inf, -np.inf], np.nan).fillna(0)
        dmi = 100 - (100 / (1 + rs))
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # DMI下穿30时买入
        self.signals[(dmi < 30) & (dmi.shift(1) >= 30)] = 1
        # DMI上穿70时卖出
        self.signals[(dmi > 70) & (dmi.shift(1) <= 70)] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)