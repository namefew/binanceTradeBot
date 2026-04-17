"""
Ehlers MESA自适应移动平均线策略
使用瞬时周期来调整移动平均线
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class EhlersMesaAdaptiveMovingAverageStrategy(BaseStrategy):
    """
    Ehlers MESA自适应移动平均线策略
    使用瞬时周期来调整移动平均线
    """
    
    def __init__(self, period=20, transaction_cost=0.001, position_size=1.0):
        super().__init__("Ehlers MESA Adaptive Moving Average Strategy", transaction_cost, indicator_short_name="MAMA", position_size=position_size)
        self.period = period
        
    def generate_signals(self):
        """
        生成MESA自适应移动平均线交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有close列
        if 'close' not in self.data.columns:
            raise ValueError("数据中缺少close列")
            
        # 计算瞬时周期
        smooth = pd.Series(0, index=self.data.index)
        detrender = pd.Series(0, index=self.data.index)
        i1 = pd.Series(0, index=self.data.index)
        q1 = pd.Series(0, index=self.data.index)
        i2 = pd.Series(0, index=self.data.index)
        q2 = pd.Series(0, index=self.data.index)
        re = pd.Series(0, index=self.data.index)
        im = pd.Series(0, index=self.data.index)
        period = pd.Series(0, index=self.data.index)
        smooth_period = pd.Series(0, index=self.data.index)
        
        for i in range(6, len(self.data)):
            # 平滑价格数据
            smooth.iloc[i] = (4 * self.data['close'].iloc[i] + 3 * self.data['close'].iloc[i-1] + 
                             2 * self.data['close'].iloc[i-2] + self.data['close'].iloc[i-3]) / 10
            
            # 计算去趋势器
            detrender.iloc[i] = (0.0962 * smooth.iloc[i] + 0.5769 * smooth.iloc[i-2] - 
                                0.5769 * smooth.iloc[i-4] - 0.0962 * smooth.iloc[i-6]) * (0.075 * period.iloc[i-1] + 0.54)
            
            # 计算同相和正交分量
            q1.iloc[i] = (0.0962 * detrender.iloc[i] + 0.5769 * detrender.iloc[i-2] - 
                         0.5769 * detrender.iloc[i-4] - 0.0962 * detrender.iloc[i-6]) * (0.075 * period.iloc[i-1] + 0.54)
            i1.iloc[i] = detrender.iloc[i-3]
            
            # 计算超前同相和正交分量
            i2.iloc[i] = i1.iloc[i] * (0.2 * period.iloc[i-1] + 0.5) + i1.iloc[i-1] * (0.4 * period.iloc[i-1] + 0.5) + \
                        i1.iloc[i-2] * (0.2 * period.iloc[i-1] + 0.5)
            q2.iloc[i] = q1.iloc[i] * (0.2 * period.iloc[i-1] + 0.5) + q1.iloc[i-1] * (0.4 * period.iloc[i-1] + 0.5) + \
                        q1.iloc[i-2] * (0.2 * period.iloc[i-1] + 0.5)
            
            # 计算实部和虚部
            re.iloc[i] = i2.iloc[i] * i2.iloc[i-1] + q2.iloc[i] * q2.iloc[i-1]
            im.iloc[i] = i2.iloc[i] * q2.iloc[i-1] - q2.iloc[i] * i2.iloc[i-1]
            
            # 计算周期
            if im.iloc[i] != 0 and re.iloc[i] != 0:
                period.iloc[i] = 2 * 3.14159 / np.arctan(im.iloc[i] / re.iloc[i])
            period.iloc[i] = min(max(period.iloc[i], 6), 50)
            
            # 平滑周期
            smooth_period.iloc[i] = 0.25 * period.iloc[i] + 0.75 * smooth_period.iloc[i-1]
        
        # 计算MESA自适应移动平均线
        mama = pd.Series(0, index=self.data.index)
        fama = pd.Series(0, index=self.data.index)
        
        for i in range(1, len(self.data)):
            # 计算平滑系数
            alpha = 0.5 * (smooth_period.iloc[i] - 1)
            alpha = max(0.01, min(0.99, alpha))
            
            # 计算MAMA和FAMA
            mama.iloc[i] = alpha * self.data['close'].iloc[i] + (1 - alpha) * mama.iloc[i-1]
            fama.iloc[i] = 0.5 * alpha * mama.iloc[i] + (1 - 0.5 * alpha) * fama.iloc[i-1]
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[self.data['close'] > mama] = 1   # 价格高于MAMA时买入
        self.signals[self.data['close'] < mama] = -1  # 价格低于MAMA时卖出