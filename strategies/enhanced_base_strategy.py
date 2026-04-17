"""
增强版基础策略类
定义策略的基本结构和通用方法，考虑交易限制
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from abc import ABC, abstractmethod

class EnhancedBaseStrategy(ABC):
    """
    抽象基类，定义策略的基本结构，考虑交易限制
    """
    
    def __init__(self, name, transaction_cost=0.001, indicator_short_name=None):
        self.name = name
        self.indicator_short_name = indicator_short_name  # 指标简称，对应研报中的第一列
        self.data = None
        self.signals = None
        self.positions = None
        self.returns = None
        self.transaction_cost = transaction_cost  # 交易成本，默认0.1%
        
    def load_data(self, data):
        """
        加载数据
        
        Parameters:
        data (DataFrame): 股票数据
        """
        self.data = data.copy()
        
    @abstractmethod
    def generate_signals(self):
        """
        生成交易信号 - 抽象方法，需要在子类中实现
        """
        pass
        
    def calculate_positions(self):
        """
        根据信号计算持仓，考虑交易限制
        """
        if self.signals is None:
            raise ValueError("请先生成交易信号")
            
        # 简单的持仓规则：信号为1时全仓买入，信号为-1时全仓卖出，信号为0时保持
        self.positions = self.signals.shift(1)  # 延迟一天执行交易
        self.positions.iloc[0] = 0  # 第一天不持仓
        
        # 检查是否有交易限制数据
        if 'limit_up' in self.data.columns and 'limit_down' in self.data.columns:
            # 在一字涨停时无法买入
            self.positions[self.data['limit_up'] & (self.positions > 0)] = 0
            # 在一字跌停时无法卖出
            self.positions[self.data['limit_down'] & (self.positions < 0)] = 0
            
    def calculate_returns(self):
        """
        计算策略收益
        """
        if self.positions is None:
            raise ValueError("请先计算持仓")
            
        # 计算收益率
        self.data['returns'] = self.data['close'].pct_change()
        self.returns = self.positions * self.data['returns']
        
        # 计算交易成本
        position_changes = self.positions.diff().abs()  # 计算仓位变化
        transaction_costs = position_changes * self.transaction_cost  # 计算交易成本
        self.returns = self.returns - transaction_costs  # 从收益中扣除交易成本
        
    def performance_metrics(self):
        """
        计算策略表现指标
        """
        if self.returns is None:
            raise ValueError("请先计算收益")
            
        # 累计收益
        cumulative_returns = (1 + self.returns).cumprod()
        
        # 保存portfolio_value用于绘图
        self.portfolio_value = cumulative_returns
        
        # 年化收益率
        annual_return = (1 + self.returns).prod() ** (252 / len(self.returns)) - 1
        
        # 波动率
        volatility = self.returns.std() * np.sqrt(252)
        
        # 夏普比率（无风险利率设为0.02）
        sharpe_ratio = (annual_return - 0.02) / volatility if volatility != 0 else 0
        
        # 最大回撤
        peak = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - peak) / peak
        max_drawdown = drawdown.min()
        
        metrics = {
            'cumulative_return': cumulative_returns.iloc[-1] - 1,
            'annual_return': annual_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown
        }
        
        return metrics
        
    def plot_results(self):
        """
        绘制策略结果
        """
        if self.returns is None:
            raise ValueError("请先计算收益")
            
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # 绘制价格和累计收益
        ax1.plot(self.data['close'], label='Price')
        cumulative_returns = (1 + self.returns).cumprod()
        ax2.plot(cumulative_returns, label='Cumulative Returns')
        
        ax1.set_title(f'{self.name} - Price')
        ax1.legend()
        
        ax2.set_title(f'{self.name} - Cumulative Returns')
        ax2.legend()
        
        plt.tight_layout()
        plt.show()