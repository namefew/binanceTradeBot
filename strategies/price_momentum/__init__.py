"""
价格动量策略模块
包含各种基于价格动量的技术分析策略
"""

# 从独立文件导入所有策略类
from .tii_strategy import TIIStrategy
from .po_strategy import POStrategy
from .madisplaced_strategy import MADisplacedStrategy
from .t3_strategy import T3Strategy
from .adtm_strategy import ADTMStrategy
# WoodiesCCIStrategy moved to price_reversal module
# from .woodies_cci_strategy import WoodiesCCIStrategy
from .psar_strategy import PSARStrategy
from .elder_ray_strategy import ElderRayStrategy
from .gann_hi_lo_strategy import GannHiLoStrategy
# CoppockCurveStrategy moved to price_reversal module
# from .coppock_curve_strategy import CoppockCurveStrategy
# RVIStrategy moved to price_reversal module
# from .rvi_strategy import RVIStrategy
from .kst_strategy import KSTStrategy
from .tsi_strategy import TSIStrategy
from .trix_strategy import TrixStrategy
from .aroon_strategy import AroonStrategy
# FibonacciRetracementStrategy moved to price_reversal module
# from .fibonacci_retracement_strategy import FibonacciRetracementStrategy
from .linear_regression_strategy import LinearRegressionStrategy
from .hurst_exponent_strategy import HurstExponentStrategy
from .guppy_multiple_moving_average_strategy import GuppyMultipleMovingAverageStrategy
from .alligator_strategy import AlligatorStrategy
from .fractal_adaptive_moving_average_strategy import FractalAdaptiveMovingAverageStrategy
from .zero_lag_exponential_moving_average_strategy import ZeroLagExponentialMovingAverageStrategy
from .hull_moving_average_strategy import HullMovingAverageStrategy
from .least_squares_moving_average_strategy import LeastSquaresMovingAverageStrategy
from .kaufman_adaptive_moving_average_strategy import KaufmanAdaptiveMovingAverageStrategy
from .triple_exponential_moving_average_strategy import TripleExponentialMovingAverageStrategy
from .variable_index_dynamic_average_strategy import VariableIndexDynamicAverageStrategy
from .ehlers_instantaneous_trendline_strategy import EhlersInstantaneousTrendlineStrategy
from .ehlers_super_smoother_strategy import EhlersSuperSmootherStrategy
from .ehlers_roofing_filter_strategy import EhlersRoofingFilterStrategy
from .ehlers_band_pass_filter_strategy import EhlersBandPassFilterStrategy
from .ehlers_fisher_transform_strategy import EhlersFisherTransformStrategy
from .ehlers_mesa_adaptive_moving_average_strategy import EhlersMesaAdaptiveMovingAverageStrategy
from .acceleration_deceleration_strategy import AccelerationDecelerationStrategy
from .adx_strategy import ADXStrategy
from .alligator_balance_strategy import AlligatorBalanceStrategy
from .apz_strategy import APZStrategy
from .aroon_oscillator_strategy import AroonOscillatorStrategy
from .asi_strategy import ASIStrategy
from .atr_strategy import ATRStrategy
from .auto_regressive_strategy import AutoRegressiveStrategy
# CCIAlternativeStrategy moved to price_reversal module
# from .cci_alternative_strategy import CCIAlternativeStrategy
# CCIStrategy moved to price_reversal module
# from .cci_strategy import CCIStrategy
from .chaikin_volatility_strategy import ChaikinVolatilityStrategy
# ChandeForecastOscillatorStrategy moved to price_reversal module
# from .chande_forecast_oscillator_strategy import ChandeForecastOscillatorStrategy
from .chande_momentum_oscillator_strategy import ChandeMomentumOscillatorStrategy
# CMOStrategy moved to price_reversal module
# from .cmo_strategy import CMOStrategy
from .connors_rsi_strategy import ConnorsRSIStrategy
# CoppockCurveStrategy moved to price_reversal module
# from .coppock_curve_strategy import CoppockCurveStrategy
from .cyber_cycle_strategy import CyberCycleStrategy
from .dema_strategy import DEMAStrategy
# dema_strategy_alt.py does not exist
# from .dema_strategy_alt import DEMAStrategy as DEMAStrategyAlt
from .detrended_price_oscillator_strategy import DetrendedPriceOscillatorStrategy
# DonchianChannelStrategy moved to market module
# from .donchian_channel_strategy import DonchianChannelStrategy
# donchian_channel_strategy_alt.py does not exist
# from .donchian_channel_strategy_alt import DonchianChannelStrategy as DonchianChannelStrategyAlt
# DPOStrategy moved to price_reversal module
# from .dpo_strategy import DPOStrategy
from .dual_thrust_strategy import DualThrustStrategy
from .dynamic_momentum_index_strategy import DynamicMomentumIndexStrategy
from .ehlers_signal_processing_strategy import EhlersSignalProcessingStrategy
from .elder_impulse_strategy import ElderImpulseStrategy
from .elder_safe_zone_strategy import ElderSafeZoneStrategy
from .er_strategy import ERStrategy
from .ergodic_candlestick_oscillator_strategy import ErgodicCandlestickOscillatorStrategy
from .fb_strategy import FBStrategy
from .fisher_inverse_strategy import FisherInverseStrategy
# FisherTransformStrategy moved to price_reversal module
# from .fisher_transform_strategy import FisherTransformStrategy
# fisher_transform_strategy_alt.py does not exist
# from .fisher_transform_strategy_alt import FisherTransformStrategy as FisherTransformStrategyAlt
from .fourier_transform_strategy import FourierTransformStrategy
from .gann_hi_lo_strategy import GannHiLoStrategy
from .gator_oscillator_strategy import GatorOscillatorStrategy
from .gopalakrishnan_range_index_strategy import GopalakrishnanRangeIndexStrategy
from .hull_ma_strategy import HullMAStrategy
from .ichimoku_strategy import IchimokuStrategy
from .inertia_indicator_strategy import InertiaIndicatorStrategy
from .inertia_strategy import InertiaStrategy
from .intraday_momentum_index_strategy import IntradayMomentumIndexStrategy
from .kairi_relative_index_strategy import KairiRelativeIndexStrategy
from .kalman_filter_strategy import KalmanFilterStrategy
from .kc_strategy import KCStrategy
from .kdjd_strategy import KDJDStrategy
from .keltner_channel_strategy import KeltnerChannelStrategy
# keltner_channel_strategy_alt.py does not exist
# from .keltner_channel_strategy_alt import KeltnerChannelStrategy as KeltnerChannelStrategyAlt
from .know_sure_thing_strategy import KnowSureThingStrategy
from .machine_learning_strategy import MachineLearningStrategy
# MassIndexStrategy moved to price_reversal module
# from .mass_index_strategy import MassIndexStrategy
from .mc_ginley_dynamic_strategy import McGinleyDynamicStrategy
from .momentum_strategy import MomentumStrategy
from .multi_factor_strategy import MultiFactorStrategy
from .parabolic_sar_strategy import ParabolicSARStrategy
from .percent_rank_strategy import PercentRankStrategy
from .ppo_strategy import PPOStrategy
# PrettyGoodOscillatorStrategy moved to price_reversal module
# from .pretty_good_oscillator_strategy import PrettyGoodOscillatorStrategy
from .projection_oscillator_strategy import ProjectionOscillatorStrategy
from .qqe_strategy import QQEStrategy
from .relative_momentum_index_strategy import RelativeMomentumIndexStrategy
from .relative_vigor_index_strategy import RelativeVigorIndexStrategy
from .schaff_trend_cycle_strategy import SchaffTrendCycleStrategy
from .standard_error_bands_strategy import StandardErrorBandsStrategy
# StochasticOscillatorStrategy moved to price_reversal module
# from .stochastic_oscillator_strategy import StochasticOscillatorStrategy
from .supertrend_strategy import SupertrendStrategy
from .tema_strategy import TEMAStrategy
# tema_strategy_alt.py does not exist
# from .tema_strategy_alt import TEMAStrategy as TEMAStrategyAlt
from .tma_strategy import TMAStrategy
# TripleScreenTradingSystemStrategy moved to market module
# from .triple_screen_trading_system_strategy import TripleScreenTradingSystemStrategy
from .trix_strategy_alt import TRIXStrategy as TrixStrategyAlt
from .true_strength_index_strategy import TrueStrengthIndexStrategy
from .typ_strategy import TYPStrategy
# # UlcerIndexStrategy moved to price_reversal module
# from .ulcer_index_strategy import UlcerIndexStrategy
from .ultimate_oscillator_strategy import UltimateOscillatorStrategy
# from .vertical_horizontal_filter_strategy import VerticalHorizontalFilterStrategy
from .vma_strategy import VMAStrategy
from .volatility_breakout_strategy import VolatilityBreakoutStrategy
from .vortex_strategy import VortexStrategy
from .wavelet_transform_strategy import WaveletTransformStrategy
from .williams_alligator_strategy import WilliamsAlligatorStrategy
# from .williams_r_strategy import WilliamsRStrategy
# from .zigzag_strategy import ZigZagStrategy
from .zlmacd_strategy import ZLMACDStrategy

# 定义公开接口
__all__ = [
    'TIIStrategy',
    'POStrategy',
    'MADisplacedStrategy',
    'T3Strategy',
    'ADTMStrategy',
# WoodiesCCIStrategy moved to price_reversal module
    # 'WoodiesCCIStrategy',
    # CoppockCurveStrategy moved to price_reversal module
    # 'CoppockCurveStrategy',
    # RVIStrategy moved to price_reversal module
    # 'RVIStrategy',
    'PSARStrategy',
    'ElderRayStrategy',
    'GannHiLoStrategy',
    # 'RVIStrategy',
    'KSTStrategy',
    'TSIStrategy',
    'TrixStrategy',
    'AroonStrategy',
    # FibonacciRetracementStrategy moved to price_reversal module
    # 'FibonacciRetracementStrategy',
    'LinearRegressionStrategy',
    'HurstExponentStrategy',
    'GuppyMultipleMovingAverageStrategy',
    'AlligatorStrategy',
    'FractalAdaptiveMovingAverageStrategy',
    'ZeroLagExponentialMovingAverageStrategy',
    'HullMovingAverageStrategy',
    'LeastSquaresMovingAverageStrategy',
    'KaufmanAdaptiveMovingAverageStrategy',
    'TripleExponentialMovingAverageStrategy',
    'VariableIndexDynamicAverageStrategy',
    'McGinleyDynamicStrategy',
    'EhlersInstantaneousTrendlineStrategy',
    'EhlersSuperSmootherStrategy',
    'EhlersRoofingFilterStrategy',
    'EhlersBandPassFilterStrategy',
    'EhlersFisherTransformStrategy',
    'EhlersMesaAdaptiveMovingAverageStrategy',
    'AccelerationDecelerationStrategy',
    'ADXStrategy',
    'AlligatorBalanceStrategy',
    'APZStrategy',
    'AroonOscillatorStrategy',
    'ASIStrategy',
    'ATRStrategy',
    'AutoRegressiveStrategy',
    # CCIAlternativeStrategy moved to price_reversal module
    # 'CCIAlternativeStrategy',
    # CCIStrategy moved to price_reversal module
    # 'CCIStrategy',
    'ChaikinVolatilityStrategy',
    # ChandeForecastOscillatorStrategy moved to price_reversal module
    # 'ChandeForecastOscillatorStrategy',
    'ChandeMomentumOscillatorStrategy',
    # CMOStrategy moved to price_reversal module
    # 'CMOStrategy',
    'ConnorsRSIStrategy',
    # CCIAlternativeStrategy moved to price_reversal module
    # 'CCIAlternativeStrategy',
    'CyberCycleStrategy',
    'DEMAStrategy',
    # dema_strategy_alt.py does not exist
    # 'DEMAStrategyAlt',
    'DetrendedPriceOscillatorStrategy',
    # DonchianChannelStrategy moved to market module
    # 'DonchianChannelStrategy',
    # donchian_channel_strategy_alt.py does not exist
    # 'DonchianChannelStrategyAlt',
    # DPOStrategy moved to price_reversal module
    # 'DPOStrategy',
    'DualThrustStrategy',
    'DynamicMomentumIndexStrategy',
    'EhlersSignalProcessingStrategy',
    'ElderImpulseStrategy',
    'ElderSafeZoneStrategy',
    'ERStrategy',
    'ErgodicCandlestickOscillatorStrategy',
    'FBStrategy',
    'FisherInverseStrategy',
    # FisherTransformStrategy moved to price_reversal module
    # 'FisherTransformStrategy',
    # fisher_transform_strategy_alt.py does not exist
    # 'FisherTransformStrategyAlt',
    'FourierTransformStrategy',
    'GatorOscillatorStrategy',
    'GopalakrishnanRangeIndexStrategy',
    'HullMAStrategy',
    'IchimokuStrategy',
    'InertiaIndicatorStrategy',
    'InertiaStrategy',
    'IntradayMomentumIndexStrategy',
    'KairiRelativeIndexStrategy',
    'KalmanFilterStrategy',
    'KCStrategy',
    'KDJDStrategy',
    'KeltnerChannelStrategy',
    # keltner_channel_strategy_alt.py does not exist
    # 'KeltnerChannelStrategyAlt',
    'KnowSureThingStrategy',
    'MachineLearningStrategy',
    # MassIndexStrategy moved to price_reversal module
    # 'MassIndexStrategy',
    'McGinleyDynamicStrategy',
    'MomentumStrategy',
    'MultiFactorStrategy',
    'ParabolicSARStrategy',
    'PercentRankStrategy',
    'PPOStrategy',
    # PrettyGoodOscillatorStrategy moved to price_reversal module
    # 'PrettyGoodOscillatorStrategy',
    'ProjectionOscillatorStrategy',
    'QQEStrategy',
    'RelativeMomentumIndexStrategy',
    'RelativeVigorIndexStrategy',
    'SchaffTrendCycleStrategy',
    'StandardErrorBandsStrategy',
    # StochasticOscillatorStrategy moved to price_reversal module
    # 'StochasticOscillatorStrategy',
    'SupertrendStrategy',
    'TEMAStrategy',
    # tema_strategy_alt.py does not exist
    # 'TEMAStrategyAlt',
    'TMAStrategy',
    # TripleScreenTradingSystemStrategy moved to market module
    # 'TripleScreenTradingSystemStrategy',
    'TrixStrategyAlt',
    'TrueStrengthIndexStrategy',
    'TYPStrategy',
    # UlcerIndexStrategy moved to price_reversal module
    # 'UlcerIndexStrategy',
    'UltimateOscillatorStrategy',
    # 'VerticalHorizontalFilterStrategy',
    'VMAStrategy',
    'VolatilityBreakoutStrategy',
    'VortexStrategy',
    'WaveletTransformStrategy',
    'WilliamsAlligatorStrategy',
    # 'WilliamsRStrategy',
    # 'ZigZagStrategy',
    'ZLMACDStrategy'
]