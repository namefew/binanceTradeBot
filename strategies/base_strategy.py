"""
基础策略类
定义策略的基本结构和通用方法
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from abc import ABC, abstractmethod
from enum import Enum


class Signal(Enum):
    """交易信号枚举"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class Strategy(ABC):
    """
    回测引擎使用的策略基类
    """
    
    def __init__(self, name: str = "BaseStrategy"):
        self.name = name
        self.cash = 0
        self.position = 0
        
    def reset(self):
        """重置策略状态"""
        self.cash = 0
        self.position = 0
    
    @abstractmethod
    def generate_signal(self, data: pd.DataFrame, current_index: int) -> str:
        """
        生成交易信号 - 抽象方法，需要在子类中实现
        
        Args:
            data: K线数据
            current_index: 当前索引
            
        Returns:
            交易信号 (Signal.BUY, Signal.SELL, or Signal.HOLD)
        """
        pass
    
    def on_trade_executed(self, signal: str, price: float, quantity: float):
        """
        当交易执行时的回调
        
        Args:
            signal: 交易信号
            price: 成交价格
            quantity: 成交数量
        """
        pass

    def calculate_positions(self):
        pass


class BaseStrategy(ABC):
    """
    main.py使用的策略基类（用于批量回测）
    """
    
    def __init__(self, name, transaction_cost=0.001, indicator_short_name=None, position_size=1.0):
        self.name = name
        self.indicator_short_name = indicator_short_name  # 指标简称，对应研报中的第一列
        self.data = None
        self.signals = None
        self.positions = None
        self.returns = None
        self.transaction_cost = transaction_cost  # 交易成本，默认0.1%
        self.position_size = position_size  # 仓位比例，默认1.0（全仓）
        
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
        根据信号计算持仓
        
        【关键修复】使用状态机逻辑，确保一买一卖间隔开来
        避免连续买入或连续卖出导致的资金计算错误
        """
        if self.signals is None:
            raise ValueError("请先生成交易信号")
            
        # 初始化 positions 数组
        self.positions = pd.Series(0, index=self.signals.index)
        
        # 状态机：跟踪当前持仓状态
        current_position = 0  # 0=空仓, 1=多头, -1=空头
        
        for i in range(1, len(self.signals)):
            signal = self.signals.iloc[i]
            
            if signal == 1 and current_position == 0:
                # 买入信号且当前空仓 -> 开多仓
                self.positions.iloc[i] = 1
                current_position = 1
            elif signal == -1 and current_position == 1:
                # 卖出信号且当前持有多头 -> 平仓
                self.positions.iloc[i] = 0
                current_position = 0
            elif signal == -1 and current_position == 0:
                # 卖出信号且当前空仓 -> 开空仓（如果支持做空）
                self.positions.iloc[i] = -1
                current_position = -1
            elif signal == 1 and current_position == -1:
                # 买入信号且当前持有空头 -> 平空仓
                self.positions.iloc[i] = 0
                current_position = 0
            else:
                # 其他情况保持当前仓位
                self.positions.iloc[i] = current_position
        
        # 第一天不持仓
        self.positions.iloc[0] = 0
        
    def calculate_returns(self):
        """
        计算策略收益
        """
        if self.positions is None:
            raise ValueError("请先计算持仓")
            
        # 计算收益率
        self.data['returns'] = self.data['close'].pct_change()
        
        # 【关键修复】使用 fillna() 替代直接赋值，确保 NaN 被正确填充
        self.data['returns'] = self.data['returns'].fillna(0.0)
        
        # 【关键修复】应用仓位比例，不要全仓交易
        # position_size 控制实际投入资金的比例
        self.returns = self.positions * self.data['returns'] * self.position_size
        
        # 计算交易成本
        position_changes = self.positions.diff().abs()  # 计算仓位变化
        position_changes = position_changes.fillna(0.0)  # 填充第一个 NaN
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
            
        # 【关键修复】移除这里的归一化，统一由 engine.py 处理
        # 原因：避免双重归一化导致资金曲线异常跳涨
            
        # 保存 portfolio_value 用于绘图
        self.portfolio_value = cumulative_returns
        
        # 检查是否有足够的数据
        if len(self.returns) == 0:
            return {
                'cumulative_return': 0,
                'annual_return': 0,
                'volatility': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0
            }
        
        # 年化收益率
        annual_return = (1 + self.returns).prod() ** (252 / len(self.returns)) - 1
        
        # 波动率
        volatility = self.returns.std() * np.sqrt(252)
        
        # 夏普比率（无风险利率设为0.02）
        # 修复：确保所有值都是标量
        def to_scalar(val):
            if isinstance(val, (int, float)):
                return val
            elif hasattr(val, 'iloc'):
                return float(val.iloc[0] if len(val) > 0 else 0)
            elif hasattr(val, 'values'):
                return float(val.values[0] if len(val.values) > 0 else 0)
            else:
                return float(val)
        
        vol_scalar = to_scalar(volatility)
        annual_return_scalar = to_scalar(annual_return)
        cumulative_return_scalar = to_scalar(cumulative_returns.iloc[-1] - 1) if len(cumulative_returns) > 0 else 0
        
        # 处理除以零的情况
        sharpe_ratio = 0
        if vol_scalar != 0:
            sharpe_ratio = (annual_return_scalar - 0.02) / vol_scalar
        elif annual_return_scalar > 0.02:
            sharpe_ratio = np.inf  # 正收益且零风险
        elif annual_return_scalar < 0.02:
            sharpe_ratio = -np.inf  # 负收益且零风险
        else:
            sharpe_ratio = 0  # 零收益且零风险
            
        # 最大回撤
        if len(cumulative_returns) > 0:
            peak = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - peak) / peak
            max_drawdown = drawdown.min()
        else:
            max_drawdown = 0
        
        # 确保所有值都是标量
        max_drawdown_scalar = to_scalar(max_drawdown)
        
        # 处理NaN值
        if np.isnan(cumulative_return_scalar):
            cumulative_return_scalar = 0
        if np.isnan(annual_return_scalar):
            annual_return_scalar = 0
        if np.isnan(vol_scalar):
            vol_scalar = 0
        if np.isnan(sharpe_ratio):
            sharpe_ratio = 0
        if np.isnan(max_drawdown_scalar):
            max_drawdown_scalar = 0
        
        metrics = {
            'cumulative_return': cumulative_return_scalar,
            'annual_return': annual_return_scalar,
            'volatility': vol_scalar,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown_scalar
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
