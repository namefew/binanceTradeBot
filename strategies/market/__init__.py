"""
市场指标策略模块
包含各种基于整体市场指标的技术分析策略
"""

# 从独立文件导入所有策略类
from .arms_strategy import ArmsStrategy
from .mcclellan_oscillator_strategy import McClellanOscillatorStrategy
from .chaikin_money_flow_strategy import ChaikinMoneyFlowStrategy
from .donchian_channel_strategy import DonchianChannelStrategy
from .triple_screen_trading_system_strategy import TripleScreenTradingSystemStrategy
from .vertical_horizontal_filter_strategy import VerticalHorizontalFilterStrategy

# 定义公开接口
__all__ = [
    'ArmsStrategy',
    'McClellanOscillatorStrategy',
    'ChaikinMoneyFlowStrategy',
    'DonchianChannelStrategy',
    'TripleScreenTradingSystemStrategy',
    'VerticalHorizontalFilterStrategy'
]