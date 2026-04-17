import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy

class NZhangTingStrategy(BaseStrategy):
    """
    N字涨停选股策略
    根据用户提供的选股逻辑实现的策略
    """
    
    def __init__(self, transaction_cost=0.001, position_size=1.0):
        super().__init__("N字涨停选股策略", transaction_cost, indicator_short_name="N字涨停", position_size=position_size)
        
    def generate_signals(self):
        """
        生成N字涨停选股策略交易信号
        """
        if self.data is None:
            raise ValueError("请先加载数据")
            
        # 确保数据中有必要的列
        required_columns = ['close', 'change_ratio', 'volume']
        if not all(col in self.data.columns for col in required_columns):
            raise ValueError(f"数据中缺少必要的列，需要包含: {required_columns}")
            
        # 创建信号序列
        self.signals = pd.Series(0, index=self.data.index)
        
        # 第一步：筛选下午2:30后涨幅在3-5%的股票
        # 这里我们假设数据是按日频度存储的，所以直接使用收盘价和涨跌幅
        # 实际应用中可能需要更精确的时间过滤
        condition1 = (self.data['change_ratio'] >= 0.03) & (self.data['change_ratio'] <= 0.05)
        
        # 第二步：筛选量比大于1的股票
        # 计算平均成交量作为基准
        avg_volume = self.data['volume'].mean()
        if avg_volume > 0:
            volume_ratio = self.data['volume'] / avg_volume
            condition2 = volume_ratio > 1.0
        else:
            condition2 = pd.Series(False, index=self.data.index)
        
        # 第三步：如果有换手率数据，则筛选换手率在3%-15%之间的股票，否则跳过此条件
        if 'turnover_rate' in self.data.columns:
            condition3 = (self.data['turnover_rate'] >= 0.03) & (self.data['turnover_rate'] <= 0.15)
        else:
            # 如果没有换手率数据，此条件默认为True
            condition3 = pd.Series(True, index=self.data.index)
        
        # 第四步：如果有流通市值数据，则筛选流通市值在30亿-300亿之间的股票，否则跳过此条件
        if 'circulating_market_cap' in self.data.columns:
            condition4 = (self.data['circulating_market_cap'] >= 30) & (self.data['circulating_market_cap'] <= 300)
        else:
            # 如果没有流通市值数据，此条件默认为True
            condition4 = pd.Series(True, index=self.data.index)
        
        # 第五步：筛选成交量持续放大的股票
        # 检查最近3天成交量是否持续放大
        volume_rolling = self.data['volume'].rolling(window=3)
        condition5 = volume_rolling.apply(lambda x: x.iloc[0] < x.iloc[1] and x.iloc[1] < x.iloc[2] if len(x) == 3 else False, raw=False)
        # 处理NaN值
        condition5 = condition5.fillna(False).astype(bool)
        
        # 第六步：筛选K线形态良好的股票
        # 检查5/10/20日均线多头向上发散
        # 计算移动平均线
        ma5 = self.data['close'].rolling(window=5).mean()
        ma10 = self.data['close'].rolling(window=10).mean()
        ma20 = self.data['close'].rolling(window=20).mean()
        
        # 检查均线多头排列 (允许一定的容差)
        tolerance = 0.01  # 1%的容差
        condition6 = (ma5 > ma10 * (1 - tolerance)) & (ma10 > ma20 * (1 - tolerance))
        
        # 综合所有条件
        final_condition = condition1 & condition2 & condition3 & condition4 & condition5 & condition6
        
        # 生成买入信号
        self.signals[final_condition] = 1
        
        # 添加卖出信号
        # 当股价跌破20日均线时卖出
        condition_sell = self.data['close'] < ma20
        
        # 生成卖出信号
        self.signals[condition_sell] = -1
        
        # 确保买卖信号不会同时存在
        # 如果某一天既有买入又有卖出信号，优先执行买入信号
        # 这里我们简单处理，确保信号值为-1, 0, 或 1
        self.signals[self.signals == 1] = 1
        self.signals[self.signals == -1] = -1
        self.signals[(self.signals != 1) & (self.signals != -1)] = 0
        
        # 打印调试信息
        print(f"各条件满足的股票数量:")
        print(f"  涨幅条件(3-5%): {condition1.sum()}")
        print(f"  量比条件(>1): {condition2.sum()}")
        print(f"  换手率条件(3-15%): {condition3.sum()}")
        print(f"  流通市值条件(30-300亿): {condition4.sum()}")
        print(f"  成交量持续放大: {condition5.sum()}")
        print(f"  均线多头排列: {condition6.sum()}")
        print(f"  综合条件: {final_condition.sum()}")