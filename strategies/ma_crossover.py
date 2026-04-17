"""
双均线交叉策略
当短期均线上穿长期均线时买入，下穿时卖出
"""
import pandas as pd
from .base_strategy import Strategy, Signal


class MovingAverageCrossover(Strategy):
    """双均线交叉策略"""
    
    def __init__(self, short_window: int = 10, long_window: int = 30):
        super().__init__(name=f"MA_Crossover_{short_window}_{long_window}")
        self.short_window = short_window
        self.long_window = long_window
    
    def generate_signal(self, data: pd.DataFrame, current_index: int) -> str:
        """
        基于均线交叉生成信号
        
        Args:
            data: K线数据
            current_index: 当前索引
            
        Returns:
            交易信号
        """
        # 确保有足够的数据计算均线
        if current_index < self.long_window:
            return Signal.HOLD
        
        # 计算短期和长期均线
        short_ma = data['close'].iloc[current_index - self.short_window + 1:current_index + 1].mean()
        long_ma = data['close'].iloc[current_index - self.long_window + 1:current_index + 1].mean()
        
        # 计算前一个时间点的均线
        prev_short_ma = data['close'].iloc[current_index - self.short_window:current_index].mean()
        prev_long_ma = data['close'].iloc[current_index - self.long_window:current_index].mean()
        
        # 金叉：短期均线上穿长期均线
        if prev_short_ma <= prev_long_ma and short_ma > long_ma:
            return Signal.BUY
        
        # 死叉：短期均线下穿长期均线
        if prev_short_ma >= prev_long_ma and short_ma < long_ma:
            return Signal.SELL
        
        return Signal.HOLD
