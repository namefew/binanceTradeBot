"""
动态买卖气指标(ADTM)策略
根据研报：ADTM=(STM-SBM)/MAX(STM,SBM)
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class ADTMStrategy(BaseStrategy):
    """
    动态买卖气指标(ADTM)策略
    根据研报：ADTM=(STM-SBM)/MAX(STM,SBM)
    """
    
    def __init__(self, n=20, transaction_cost=0.001, position_size=1.0):
        super().__init__("ADTM Strategy", transaction_cost, indicator_short_name="ADTM", position_size=position_size)
        self.n = n
        
    def generate_signals(self):
        """
        生成ADTM交易信号
        当ADTM上穿0.5时买入，下穿-0.5时卖出
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有必要的列
        required_columns = ['open', 'high', 'low']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算DTM和DBM
        open_gt_ref_open = self.data['open'] > self.data['open'].shift(1)
        high_minus_open = self.data['high'] - self.data['open']
        open_minus_ref_open = self.data['open'] - self.data['open'].shift(1)
        open_minus_low = self.data['open'] - self.data['low']
        ref_open_minus_open = self.data['open'].shift(1) - self.data['open']
        
        # 使用pandas方法替代numpy.where
        cond1 = high_minus_open.where(open_gt_ref_open, 0)
        cond2 = open_minus_ref_open.where(open_gt_ref_open, 0)
        dtm = pd.concat([cond1, cond2], axis=1).max(axis=1)
        
        cond3 = open_minus_low.where(~open_gt_ref_open, 0)
        cond4 = ref_open_minus_open.where(~open_gt_ref_open, 0)
        dbm = pd.concat([cond3, cond4], axis=1).max(axis=1)
        
        # 计算STM和SBM
        stm = dtm.rolling(window=self.n).sum()
        sbm = dbm.rolling(window=self.n).sum()
        
        # 计算ADTM
        max_stm_sbm = pd.concat([stm, sbm], axis=1).max(axis=1)
        adtm = (stm - sbm) / max_stm_sbm
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        # ADTM上穿0.5时买入
        adtm_gt_05 = adtm > 0.5
        adtm_shift_le_05 = adtm.shift(1) <= 0.5
        self.signals[adtm_gt_05 & adtm_shift_le_05] = 1
        # ADTM下穿-0.5时卖出
        adtm_lt_neg05 = adtm < -0.5
        adtm_shift_ge_neg05 = adtm.shift(1) >= -0.5
        self.signals[adtm_lt_neg05 & adtm_shift_ge_neg05] = -1
        
        # 处理信号变化点，保持信号直到下一个变化点
        self.signals = self.signals.replace(to_replace=0, method='ffill').fillna(0)