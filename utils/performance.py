"""
绩效分析模块
计算各种交易绩效指标
"""
import numpy as np
import pandas as pd
from typing import List, Dict
from datetime import datetime


class PerformanceAnalyzer:
    """绩效分析器"""
    
    def __init__(self, equity_curve: List[float], timestamps: List[datetime] = None):
        """
        初始化绩效分析器
        
        Args:
            equity_curve: 权益曲线数据
            timestamps: 时间戳列表
        """
        self.equity_curve = np.array(equity_curve)
        self.timestamps = timestamps
        self.returns = self._calculate_returns()
    
    def _calculate_returns(self) -> np.ndarray:
        """计算收益率序列"""
        if len(self.equity_curve) < 2:
            return np.array([])
        returns = np.diff(self.equity_curve) / self.equity_curve[:-1]
        return returns
    
    def total_return(self) -> float:
        """总收益率"""
        if len(self.equity_curve) < 2:
            return 0.0
        return (self.equity_curve[-1] - self.equity_curve[0]) / self.equity_curve[0]
    
    def annualized_return(self) -> float:
        """年化收益率"""
        total_ret = self.total_return()
        if not self.timestamps or len(self.timestamps) < 2:
            return total_ret
        
        # 计算年数
        days = (self.timestamps[-1] - self.timestamps[0]).days
        years = days / 365.25
        
        if years <= 0:
            return 0.0
        
        return (1 + total_ret) ** (1 / years) - 1
    
    def max_drawdown(self) -> float:
        """最大回撤"""
        if len(self.equity_curve) == 0:
            return 0.0
        
        peak = self.equity_curve[0]
        max_dd = 0
        
        for value in self.equity_curve:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            if drawdown > max_dd:
                max_dd = drawdown
        
        return max_dd
    
    def sharpe_ratio(self, risk_free_rate: float = 0.0) -> float:
        """
        夏普比率
        
        Args:
            risk_free_rate: 无风险利率（年化）
        """
        if len(self.returns) == 0 or np.std(self.returns) == 0:
            return 0.0
        
        # 日化无风险利率
        daily_rf = risk_free_rate / 252
        
        excess_returns = self.returns - daily_rf
        sharpe = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
        
        return sharpe
    
    def sortino_ratio(self, risk_free_rate: float = 0.0) -> float:
        """
        索提诺比率（只考虑下行波动）
        
        Args:
            risk_free_rate: 无风险利率（年化）
        """
        if len(self.returns) == 0:
            return 0.0
        
        daily_rf = risk_free_rate / 252
        excess_returns = self.returns - daily_rf
        
        # 只考虑负收益
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) == 0:
            return float('inf')
        
        downside_std = np.std(downside_returns)
        
        if downside_std == 0:
            return 0.0
        
        sortino = np.mean(excess_returns) / downside_std * np.sqrt(252)
        
        return sortino
    
    def calmar_ratio(self) -> float:
        """卡玛比率（年化收益/最大回撤）"""
        max_dd = self.max_drawdown()
        if max_dd == 0:
            return 0.0
        
        ann_return = self.annualized_return()
        return ann_return / max_dd
    
    def win_rate(self, trades: List[Dict] = None) -> float:
        """
        胜率
        
        Args:
            trades: 交易记录列表，包含'signal'和'price'字段
        """
        if not trades or len(trades) == 0:
            return 0.0
        
        buy_trades = [t for t in trades if t.get('signal') == 'BUY']
        sell_trades = [t for t in trades if t.get('signal') == 'SELL']
        
        if len(buy_trades) == 0 or len(sell_trades) == 0:
            return 0.0
        
        winning = 0
        total_rounds = min(len(buy_trades), len(sell_trades))
        
        for i in range(total_rounds):
            profit = sell_trades[i].get('price', 0) - buy_trades[i].get('price', 0)
            if profit > 0:
                winning += 1
        
        return winning / total_rounds if total_rounds > 0 else 0.0
    
    def profit_factor(self, trades: List[Dict] = None) -> float:
        """
        盈利因子（总盈利/总亏损）
        
        Args:
            trades: 交易记录列表
        """
        if not trades or len(trades) == 0:
            return 0.0
        
        buy_trades = [t for t in trades if t.get('signal') == 'BUY']
        sell_trades = [t for t in trades if t.get('signal') == 'SELL']
        
        total_profit = 0
        total_loss = 0
        
        total_rounds = min(len(buy_trades), len(sell_trades))
        
        for i in range(total_rounds):
            profit = sell_trades[i].get('price', 0) - buy_trades[i].get('price', 0)
            if profit > 0:
                total_profit += profit
            else:
                total_loss += abs(profit)
        
        if total_loss == 0:
            return float('inf') if total_profit > 0 else 0.0
        
        return total_profit / total_loss
    
    def volatility(self) -> float:
        """波动率（年化）"""
        if len(self.returns) == 0:
            return 0.0
        return np.std(self.returns) * np.sqrt(252)
    
    def get_all_metrics(self, trades: List[Dict] = None) -> Dict:
        """
        获取所有绩效指标
        
        Args:
            trades: 交易记录列表
            
        Returns:
            包含所有指标的字典
        """
        return {
            '总收益率': f"{self.total_return() * 100:.2f}%",
            '年化收益率': f"{self.annualized_return() * 100:.2f}%",
            '最大回撤': f"{self.max_drawdown() * 100:.2f}%",
            '夏普比率': f"{self.sharpe_ratio():.2f}",
            '索提诺比率': f"{self.sortino_ratio():.2f}",
            '卡玛比率': f"{self.calmar_ratio():.2f}",
            '波动率': f"{self.volatility() * 100:.2f}%",
            '胜率': f"{self.win_rate(trades) * 100:.2f}%",
            '盈利因子': f"{self.profit_factor(trades):.2f}",
            '初始资金': f"{self.equity_curve[0]:.2f}" if len(self.equity_curve) > 0 else "N/A",
            '最终资金': f"{self.equity_curve[-1]:.2f}" if len(self.equity_curve) > 0 else "N/A",
        }
