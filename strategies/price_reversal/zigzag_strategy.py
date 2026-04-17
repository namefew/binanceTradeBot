"""
之字转向策略 (ZigZag Indicator)
用于识别重要的价格转折点
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class ZigZagStrategy(BaseStrategy):
    """
    之字转向策略 (ZigZag Indicator)
    用于识别重要的价格转折点
    """
    
    def __init__(self, deviation=5, transaction_cost=0.001, position_size=1.0):
        super().__init__("ZigZag Strategy", transaction_cost, indicator_short_name="ZigZag", position_size=position_size)
        self.deviation = deviation
        
    def generate_signals(self):
        """
        生成之字转向交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有high, low列
        required_columns = ['high', 'low']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 计算之字转向点
        zigzag_points = []
        last_point = None
        trend = 0  # 0表示无趋势，1表示上升趋势，-1表示下降趋势
        
        for i in range(len(self.data)):
            if last_point is None:
                last_point = {'index': i, 'price': self.data['close'].iloc[i], 'type': 'start'}
                zigzag_points.append(last_point)
                continue
                
            if trend >= 0:  # 上升或无趋势
                # 寻找新的高点
                if self.data['high'].iloc[i] > last_point['price'] * (1 + self.deviation/100):
                    # 确认新的高点
                    if len(zigzag_points) > 1 and zigzag_points[-1]['type'] == 'high':
                        zigzag_points.pop()  # 移除之前的高点
                    zigzag_points.append({'index': i, 'price': self.data['high'].iloc[i], 'type': 'high'})
                    last_point = zigzag_points[-1]
                    trend = -1  # 下一步寻找低点
                elif self.data['low'].iloc[i] < last_point['price'] * (1 - self.deviation/100):
                    # 确认新的低点
                    if len(zigzag_points) > 1 and zigzag_points[-1]['type'] == 'low':
                        zigzag_points.pop()  # 移除之前的低点
                    zigzag_points.append({'index': i, 'price': self.data['low'].iloc[i], 'type': 'low'})
                    last_point = zigzag_points[-1]
                    trend = 1  # 下一步寻找高点
            else:  # 下降趋势
                # 寻找新的低点
                if self.data['low'].iloc[i] < last_point['price'] * (1 - self.deviation/100):
                    # 确认新的低点
                    if len(zigzag_points) > 1 and zigzag_points[-1]['type'] == 'low':
                        zigzag_points.pop()  # 移除之前的低点
                    zigzag_points.append({'index': i, 'price': self.data['low'].iloc[i], 'type': 'low'})
                    last_point = zigzag_points[-1]
                    trend = 1  # 下一步寻找高点
                elif self.data['high'].iloc[i] > last_point['price'] * (1 + self.deviation/100):
                    # 确认新的高点
                    if len(zigzag_points) > 1 and zigzag_points[-1]['type'] == 'high':
                        zigzag_points.pop()  # 移除之前的高点
                    zigzag_points.append({'index': i, 'price': self.data['high'].iloc[i], 'type': 'high'})
                    last_point = zigzag_points[-1]
                    trend = -1  # 下一步寻找低点
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        for i in range(1, len(zigzag_points)):
            point = zigzag_points[i]
            prev_point = zigzag_points[i-1]
            
            if point['type'] == 'high' and prev_point['type'] == 'low':
                # 从低点到高点，买入信号
                self.signals.iloc[point['index']] = 1
            elif point['type'] == 'low' and prev_point['type'] == 'high':
                # 从高点到低点，卖出信号
                self.signals.iloc[point['index']] = -1