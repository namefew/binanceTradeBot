"""
麦克莱伦振荡器策略
基于涨跌家数的市场广度指标
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class McClellanOscillatorStrategy(BaseStrategy):
    """
    麦克莱伦振荡器策略
    基于涨跌家数的市场广度指标
    """
    
    def __init__(self, period_fast=19, period_slow=39, transaction_cost=0.001, position_size=1.0):
        super().__init__("McClellan Oscillator Strategy", transaction_cost, indicator_short_name="MO", position_size=position_size)
        self.period_fast = period_fast
        self.period_slow = period_slow
        
    def generate_signals(self):
        """
        生成麦克莱伦振荡器交易信号
        注意：此策略需要涨跌家数数据，实际应用中需要额外数据源
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 模拟涨跌家数（实际应用中需要真实数据）
        advancing_issues = pd.Series(np.random.randint(800, 1200, len(self.data)), index=self.data.index)
        declining_issues = pd.Series(np.random.randint(800, 1200, len(self.data)), index=self.data.index)
        
        # 计算净上涨家数
        net_advances = advancing_issues - declining_issues
        
        # 计算快速和慢速EMA
        fast_ema = net_advances.ewm(span=self.period_fast).mean()
        slow_ema = net_advances.ewm(span=self.period_slow).mean()
        
        # 计算麦克莱伦振荡器
        mcclellan_osc = fast_ema - slow_ema
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        self.signals[(mcclellan_osc > 0) & (mcclellan_osc.shift(1) <= 0)] = 1   # 振荡器上穿零轴时买入
        self.signals[(mcclellan_osc < 0) & (mcclellan_osc.shift(1) >= 0)] = -1  # 振荡器下穿零轴时卖出