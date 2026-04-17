"""
回测引擎
用于在历史数据上测试交易策略
"""
import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime
from strategies.base_strategy import BaseStrategy, Strategy, Signal


class Trade:
    """交易记录"""
    
    def __init__(self, timestamp: datetime, signal: str, price: float, 
                 quantity: float, commission: float = 0):
        self.timestamp = timestamp
        self.signal = signal
        self.price = price
        self.quantity = quantity
        self.commission = commission
        self.total_value = price * quantity + commission


class BacktestResult:
    """回测结果"""
    
    def __init__(self):
        self.trades: List[Trade] = []
        self.equity_curve: List[float] = []
        self.timestamps: List[datetime] = []
        self.initial_capital = 0
        self.final_capital = 0
        self.total_return = 0
        self.max_drawdown = 0
        self.sharpe_ratio = 0
        self.win_rate = 0
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
    
    def calculate_metrics(self):
        """计算回测指标"""
        if not self.equity_curve:
            return
        
        # 基本指标
        self.initial_capital = self.equity_curve[0]
        self.final_capital = self.equity_curve[-1]
        self.total_return = (self.final_capital - self.initial_capital) / self.initial_capital
        
        # 最大回撤
        peak = self.equity_curve[0]
        max_dd = 0
        for value in self.equity_curve:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            if drawdown > max_dd:
                max_dd = drawdown
        self.max_drawdown = max_dd
        
        # 收益率序列
        returns = np.diff(self.equity_curve) / self.equity_curve[:-1]
        
        # 夏普比率（假设无风险利率为0）
        if len(returns) > 0 and np.std(returns) > 0:
            self.sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252)
        
        # 交易统计
        self.total_trades = len(self.trades)
        if self.total_trades > 0:
            # 计算胜率
            buy_trades = [t for t in self.trades if t.signal == Signal.BUY]
            sell_trades = [t for t in self.trades if t.signal == Signal.SELL]
            
            winning = 0
            losing = 0
            for i in range(min(len(buy_trades), len(sell_trades))):
                profit = sell_trades[i].price - buy_trades[i].price
                if profit > 0:
                    winning += 1
                else:
                    losing += 1
            
            self.winning_trades = winning
            self.losing_trades = losing
            self.win_rate = winning / (winning + losing) if (winning + losing) > 0 else 0
    
    def summary(self) -> Dict:
        """返回回测摘要"""
        self.calculate_metrics()
        return {
            '策略名称': self.trades[0].signal if self.trades else 'N/A',
            '初始资金': f"{self.initial_capital:.2f}",
            '最终资金': f"{self.final_capital:.2f}",
            '总收益率': f"{self.total_return * 100:.2f}%",
            '最大回撤': f"{self.max_drawdown * 100:.2f}%",
            '夏普比率': f"{self.sharpe_ratio:.2f}",
            '总交易次数': self.total_trades,
            '盈利次数': self.winning_trades,
            '亏损次数': self.losing_trades,
            '胜率': f"{self.win_rate * 100:.2f}%"
        }


class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, strategy: Strategy, initial_capital: float = 10000,
                 commission_rate: float = 0.001, position_size: float = 0.1):
        """
        初始化回测引擎
        
        Args:
            strategy: 交易策略
            initial_capital: 初始资金
            commission_rate: 手续费率
            position_size: 每次交易使用的资金比例
        """
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.position_size = position_size
        self.result = BacktestResult()
    
    def run(self, data: pd.DataFrame) -> BacktestResult:
        """
        运行回测
        
        Args:
            data: 历史K线数据，必须包含open_time, open, high, low, close, volume
            
        Returns:
            回测结果
        """
        # 重置策略状态（如果策略有reset方法）
        if hasattr(self.strategy, 'reset'):
            self.strategy.reset()
            self.strategy.cash = self.initial_capital
        elif hasattr(self.strategy, 'load_data'):
            # BaseStrategy类型的策略，需要加载数据并生成信号
            # 更新策略的手续费率为用户配置的值
            if hasattr(self.strategy, 'transaction_cost'):
                self.strategy.transaction_cost = self.commission_rate
            
            # 【关键修复】设置仓位比例，不要全仓交易
            if hasattr(self.strategy, 'position_size'):
                self.strategy.position_size = self.position_size
            
            self.strategy.load_data(data)
            self.strategy.generate_signals()
            self.strategy.calculate_positions()
            self.strategy.calculate_returns()
            
            # 计算绩效指标
            metrics = self.strategy.performance_metrics()
            
            # 构建回测结果
            self.result = BacktestResult()
            self.result.initial_capital = self.initial_capital
                        
            # 过滤掉 NaN 和 Inf 值
            import numpy as np
            portfolio_values = self.strategy.portfolio_value.replace([np.inf, -np.inf], np.nan).dropna()
                        
            if len(portfolio_values) > 0:
                # 【关键修复】归一化处理：强制让曲线从初始资金开始
                # 这样可以消除策略初始计算偏移导致的"暴涨"或"暴跌"假象
                first_val = portfolio_values.iloc[0]
                if first_val != 0 and not np.isnan(first_val):
                    # 将所有值除以第一个值，使起始点变为 1.0
                    normalized_values = portfolio_values / first_val
                else:
                    normalized_values = portfolio_values
                            
                # 计算权益曲线
                self.result.equity_curve = (normalized_values * self.initial_capital).tolist()
                self.result.final_capital = self.result.equity_curve[-1]
                            
                # 确保 timestamps 与 equity_curve 长度一致
                valid_indices = self.strategy.portfolio_value.replace([np.inf, -np.inf], np.nan).notna()
                self.result.timestamps = data['open_time'][valid_indices].tolist()
            else:
                self.result.final_capital = self.initial_capital
                self.result.equity_curve = [self.initial_capital]
                self.result.timestamps = data['open_time'].tolist()
            
            # 计算交易次数并生成交易记录
            position_changes = self.strategy.positions.diff()
            self.result.total_trades = int(position_changes.abs().sum())
            
            # 生成交易记录
            for i in range(1, len(self.strategy.positions)):
                pos_change = position_changes.iloc[i]
                if pos_change != 0:  # 有仓位变化
                    timestamp = data['open_time'].iloc[i]
                    price = data['close'].iloc[i]
                    
                    # 计算交易数量和方向
                    # BaseStrategy使用标准化仓位(0或1)，需要转换为实际交易数量
                    # 【修复】应用 position_size 参数，不要全仓交易
                    quantity = abs(pos_change) * self.initial_capital * self.position_size / price
                    signal = Signal.BUY if pos_change > 0 else Signal.SELL
                    commission = quantity * price * self.commission_rate
                    
                    trade = Trade(timestamp, signal, price, quantity, commission)
                    self.result.trades.append(trade)
            
            # 计算最大回撤和其他指标
            if self.result.equity_curve:
                # 计算最大回撤
                peak = self.result.equity_curve[0]
                max_dd = 0
                for value in self.result.equity_curve:
                    if value > peak:
                        peak = value
                    drawdown = (peak - value) / peak
                    if drawdown > max_dd:
                        max_dd = drawdown
                self.result.max_drawdown = max_dd
                
                # 计算夏普比率
                import numpy as np
                returns = np.diff(self.result.equity_curve) / self.result.equity_curve[:-1]
                if len(returns) > 0 and np.std(returns) > 0:
                    self.result.sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252)
                
                # 计算胜率
                buy_trades = [t for t in self.result.trades if t.signal == Signal.BUY]
                sell_trades = [t for t in self.result.trades if t.signal == Signal.SELL]
                
                winning = 0
                losing = 0
                for i in range(min(len(buy_trades), len(sell_trades))):
                    profit = sell_trades[i].price - buy_trades[i].price
                    if profit > 0:
                        winning += 1
                    else:
                        losing += 1
                
                self.result.winning_trades = winning
                self.result.losing_trades = losing
                self.result.win_rate = winning / (winning + losing) if (winning + losing) > 0 else 0
            
            return self.result
        else:
            raise AttributeError("策略必须实现 reset() 方法或 load_data()/generate_signals() 方法")
        
        # 以下代码仅适用于Strategy类型的策略（有reset方法）
        if not hasattr(self.strategy, 'reset'):
            # BaseStrategy类型已经在上面处理并返回
            return self.result
        
        # 初始化结果
        self.result = BacktestResult()
        self.result.initial_capital = self.initial_capital
        
        cash = self.initial_capital
        position = 0
        
        print(f"开始回测，共 {len(data)} 条数据...")
        
        # 遍历每个时间点
        for i in range(len(data)):
            current_price = data['close'].iloc[i]
            timestamp = data['open_time'].iloc[i]
            
            # 生成信号
            signal = self.strategy.generate_signal(data, i)
            
            # 执行交易
            if signal == Signal.BUY and cash > 0 and position == 0:
                # 计算买入数量
                trade_value = cash * self.position_size
                quantity = trade_value / current_price
                commission = trade_value * self.commission_rate
                
                if quantity > 0:
                    trade = Trade(timestamp, signal, current_price, quantity, commission)
                    self.result.trades.append(trade)
                    
                    cash -= (trade_value + commission)
                    position += quantity
                    
                    # 更新策略状态
                    self.strategy.on_trade_executed(signal, current_price, quantity)
            
            elif signal == Signal.SELL and position > 0:
                # 卖出全部持仓
                trade_value = position * current_price
                commission = trade_value * self.commission_rate
                
                trade = Trade(timestamp, signal, current_price, position, commission)
                self.result.trades.append(trade)
                
                cash += (trade_value - commission)
                position = 0
                
                # 更新策略状态
                self.strategy.on_trade_executed(signal, current_price, trade.quantity)
            
            # 记录权益曲线
            total_equity = cash + position * current_price
            self.result.equity_curve.append(total_equity)
            self.result.timestamps.append(timestamp)
        
        self.result.final_capital = self.result.equity_curve[-1] if self.result.equity_curve else self.initial_capital
        
        print("回测完成！")
        return self.result
