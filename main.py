"""
主程序
用于运行和测试各种策略
"""

import pandas as pd
import numpy as np
import warnings
import os
import traceback
import pickle
import logging
import random
import matplotlib.pyplot as plt
import seaborn as sns

from strategies.factor_scoring_strategy import FactorScoringStrategy
from strategies.n_zhangting.n_zhangting_strategy import NZhangTingStrategy

warnings.filterwarnings('ignore')

# 定义全局交易费用
TRANSACTION_COST = 0.0000

from data.data_source import  load_stock_trading_data, load_single_stock_data
from strategies.technical_indicators import MovingAverageStrategy,MACDStrategy,RSIStategy,BollingerBandsStrategy,KDStrategy,BuyAndHoldStrategy

# 导入新的策略分类
from strategies  import *



def load_all_stock_data():
    """
    从CSV文件加载所有股票数据

    Returns:
    dict: 股票数据字典，键为股票代码，值为对应的DataFrame
    """
    # 检查是否存在预处理的数据文件
    processed_data_file = os.path.join(os.path.dirname(__file__), 'data', 'processed_stock_data.pkl')
    if os.path.exists(processed_data_file):
        print("从预处理文件加载数据...")
        with open(processed_data_file, 'rb') as f:
            return pickle.load(f)

    # 获取data目录路径
    data_dir = os.path.join(os.path.dirname(__file__), '../myQuant/data')
    csv_dir = os.path.join(data_dir, 'stock-trading-data-2024-09-28N')

    # 查找CSV文件
    if not os.path.exists(csv_dir):
        print(f"目录 {csv_dir} 不存在")
        return {}

    # 加载所有股票数据
    stock_data_dict = load_stock_trading_data(csv_dir)

    # 保存预处理的数据
    with open(processed_data_file, 'wb') as f:
        pickle.dump(stock_data_dict, f)
    print(f"数据已保存到 {processed_data_file}")

    return stock_data_dict


def setup_logging():
    """
    设置日志配置
    """
    # 创建logs目录（如果不存在）
    log_dir = os.path.join(os.getcwd(), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 配置日志格式和文件
    log_file = os.path.join(log_dir, 'strategy_results.log')
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8')
            # 移除了StreamHandler，避免控制台重复输出
        ]
    )
    
    return logging.getLogger(__name__)

def run_strategy(strategy, data, stock_code=None):
    """
    运行策略并输出结果
    
    Parameters:
    strategy (BaseStrategy): 策略实例
    data (DataFrame): 股票数据
    stock_code (str): 股票代码
    """
    logger = logging.getLogger(__name__)
    stock_info = f" ({stock_code})" if stock_code else ""
    log_msg = f"运行策略: {strategy.name}{stock_info}"
    print(log_msg)  # 仅在控制台打印一次
    logger.info("=" * 50)
    logger.info(log_msg)
    
    try:
        # 加载数据
        strategy.load_data(data)
        
        # 生成信号
        strategy.generate_signals()
        
        # 计算持仓
        strategy.calculate_positions()
        
        # 计算收益
        strategy.calculate_returns()
        
        # 计算表现指标
        metrics = strategy.performance_metrics()
        
        # 检查并处理NaN值
        for key, value in metrics.items():
            if np.isnan(value) or np.isinf(value):
                metrics[key] = 0
        
        # 输出结果
        log_msg = f"累计收益: {metrics['cumulative_return']:.2%}"
        print(log_msg)  # 仅在控制台打印一次
        logger.info(log_msg)
        
        log_msg = f"年化收益: {metrics['annual_return']:.2%}"
        print(log_msg)  # 仅在控制台打印一次
        logger.info(log_msg)
        
        log_msg = f"波动率: {metrics['volatility']:.2%}"
        print(log_msg)  # 仅在控制台打印一次
        logger.info(log_msg)
        
        log_msg = f"夏普比率: {metrics['sharpe_ratio']:.2f}"
        print(log_msg)  # 仅在控制台打印一次
        logger.info(log_msg)
        
        log_msg = f"最大回撤: {metrics['max_drawdown']:.2%}"
        print(log_msg)  # 仅在控制台打印一次
        logger.info(log_msg)
        
        # 返回结果以便进一步分析
        return metrics
    except Exception as e:
        error_msg = f"运行策略 {strategy.name} 时出错: {str(e)}"
        print(error_msg)  # 仅在控制台打印一次
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return None

def run_strategies_on_all_stocks():
    """
    在所有股票上运行策略
    """
    logger = logging.getLogger(__name__)
    log_msg = "加载所有股票数据..."
    print(log_msg)  # 仅在控制台打印一次
    logger.info(log_msg)
    
    stock_data_dict = load_all_stock_data()
    
    if not stock_data_dict:
        log_msg = "无法加载股票数据"
        print(log_msg)  # 仅在控制台打印一次
        logger.error(log_msg)
        return
    
    log_msg = f"成功加载 {len(stock_data_dict)} 只股票的数据"
    print(log_msg)  # 仅在控制台打印一次
    logger.info(log_msg)
    
    # 定义要运行的策略 (添加交易成本参数)
    strategies = get_all_strategies()
    
    # 存储所有结果
    all_results = []
    
    # 对每只股票运行策略
    # 随机选择50只股票，如果股票总数不足50只，则选择所有股票
    all_stocks = list(stock_data_dict.items())
    nums = 10
    if len(all_stocks) > nums:
        test_stocks = random.sample(all_stocks, nums)
        log_msg = f"随机选取{nums}只股票进行测试"
    else:
        test_stocks = all_stocks
        log_msg = f"股票总数不足{nums}只，将对所有{len(all_stocks)}只股票进行测试"
    
    print(log_msg)  # 仅在控制台打印一次
    logger.info(log_msg)
    print(f"将在 {len(test_stocks)} 只股票上运行策略")  # 仅在控制台打印一次
    logger.info(f"将在 {len(test_stocks)} 只股票上运行策略")
    
    for stock_code, stock_data in test_stocks:
        print(f"\n{'='*60}")
        print(f"正在分析股票: {stock_code}")
        print(f"{'='*60}")
        
        # 对每个策略运行分析
        for strategy in strategies:
            try:
                metrics = run_strategy(strategy, stock_data, stock_code)
                if metrics is not None:
                    # 存储结果
                    result = {
                        'stock_code': stock_code,
                        'strategy': strategy.name,
                        'cumulative_return': metrics['cumulative_return'],
                        'annual_return': metrics['annual_return'],
                        'volatility': metrics['volatility'],
                        'sharpe_ratio': metrics['sharpe_ratio'],
                        'max_drawdown': metrics['max_drawdown']
                    }
                    all_results.append(result)
            except Exception as e:
                print(f"运行策略 {strategy.name} 时出错: {e}")
                traceback.print_exc()
    
    # 汇总结果
    if all_results:
        results_df = pd.DataFrame(all_results)
        print(f"\n{'='*80}")
        print("策略表现汇总")
        print(f"{'='*80}")
        
        # 按策略分组，显示平均表现
        summary = results_df.groupby('strategy').agg({
            'cumulative_return': 'mean',
            'annual_return': 'mean',
            'volatility': 'mean',
            'sharpe_ratio': 'mean',
            'max_drawdown': 'mean'
        }).round(4)
        
        # 按夏普比率从高到低排序
        summary = summary.sort_values('sharpe_ratio', ascending=False)
        
        # 设置pandas显示选项，确保完整显示所有数据而不省略
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)
        
        print("\n各策略平均表现 (按夏普比率排序):")
        print(summary)
        
        # 找出表现最好的策略（按夏普比率）
        if not results_df.empty:
            best_strategy = results_df.loc[results_df['sharpe_ratio'].idxmax()]
            print(f"\n表现最好的策略:")
            print(f"策略: {best_strategy['strategy']}")
            print(f"股票: {best_strategy['stock_code']}")
            print(f"夏普比率: {best_strategy['sharpe_ratio']:.4f}")
            print(f"累计收益: {best_strategy['cumulative_return']:.2%}")
            print(f"年化收益: {best_strategy['annual_return']:.2%}")
            print(f"波动率: {best_strategy['volatility']:.2%}")
            print(f"最大回撤: {best_strategy['max_drawdown']:.2%}")


def get_all_strategies():
    strategies = [
        MovingAverageStrategy(short_window=5, long_window=20, transaction_cost=TRANSACTION_COST),
        RSIStategy(period=14, overbought=70, oversold=30, transaction_cost=TRANSACTION_COST),
        MACDStrategy(fast_period=12, slow_period=26, signal_period=9, transaction_cost=TRANSACTION_COST),
        BollingerBandsStrategy(window=20, num_std=2, transaction_cost=TRANSACTION_COST),
        KDStrategy(k_period=14, d_period=3, overbought=80, oversold=20, transaction_cost=TRANSACTION_COST),
        MeanReversionStrategy(window=20, z_score_threshold=1.5, transaction_cost=TRANSACTION_COST),
        MomentumStrategy(window=90, threshold=0.05, transaction_cost=TRANSACTION_COST),
        DualThrustStrategy(period=2, k1=0.7, k2=0.7, transaction_cost=TRANSACTION_COST),
        CCIStrategy(period=20, overbought=100, oversold=-100, transaction_cost=TRANSACTION_COST),
        MultiFactorStrategy(transaction_cost=TRANSACTION_COST),
        BuyAndHoldStrategy(transaction_cost=TRANSACTION_COST),  # 添加买入持有策略
        # 价格反转类策略
        WilliamsRStrategy(period=14, overbought=-20, oversold=-80, transaction_cost=TRANSACTION_COST),
        StochasticOscillatorStrategy(k_period=14, d_period=3, overbought=80, oversold=20,
                                     transaction_cost=TRANSACTION_COST),
        CMOStrategy(period=14, overbought=50, oversold=-50, transaction_cost=TRANSACTION_COST),
        ROCStrategy(period=12, threshold=0, transaction_cost=TRANSACTION_COST),
        TrixStrategy(period=15, signal_period=9, transaction_cost=TRANSACTION_COST),
        CCIAlternativeStrategy(period=20, overbought=100, oversold=-100, transaction_cost=TRANSACTION_COST),
        FisherTransformStrategy(period=10, transaction_cost=TRANSACTION_COST),
        PPOStrategy(fast_period=12, slow_period=26, signal_period=9, transaction_cost=TRANSACTION_COST),
        AwesomeOscillatorStrategy(transaction_cost=TRANSACTION_COST),
        KeltnerChannelStrategy(period=20, multiplier=1.5, transaction_cost=TRANSACTION_COST),
        ElderRayStrategy(period=13, transaction_cost=TRANSACTION_COST),
        SchaffTrendCycleStrategy(period=10, fast_period=23, slow_period=50, transaction_cost=TRANSACTION_COST),
        CoppockCurveStrategy(short_period=11, long_period=14, wma_period=10, transaction_cost=TRANSACTION_COST),
        ChandeForecastOscillatorStrategy(period=14, transaction_cost=TRANSACTION_COST),
        MassIndexStrategy(period=9, threshold=27, transaction_cost=TRANSACTION_COST),
        UlcerIndexStrategy(period=14, transaction_cost=TRANSACTION_COST),
        TrueStrengthIndexStrategy(short_period=25, long_period=13, signal_period=7, transaction_cost=TRANSACTION_COST),
        UltimateOscillatorStrategy(period1=7, period2=14, period3=28, transaction_cost=TRANSACTION_COST),
        DonchianChannelStrategy(period=20, transaction_cost=TRANSACTION_COST),
        DetrendedPriceOscillatorStrategy(period=20, transaction_cost=TRANSACTION_COST),
        AroonStrategy(period=25, transaction_cost=TRANSACTION_COST),
        StochasticRSIStrategy(rsi_period=14, stoch_period=14, overbought=80, oversold=20,
                              transaction_cost=TRANSACTION_COST),
        FractalStrategy(period=5, transaction_cost=TRANSACTION_COST),
        MarketMeannessIndexStrategy(transaction_cost=TRANSACTION_COST),
        PrettyGoodOscillatorStrategy(transaction_cost=TRANSACTION_COST),
        StandardPivotPointsStrategy(transaction_cost=TRANSACTION_COST),
        # 趋势跟踪类策略
        ADXStrategy(period=14, transaction_cost=TRANSACTION_COST),
        PSARStrategy(step=0.02, max_step=0.2, transaction_cost=TRANSACTION_COST),
        IchimokuStrategy(transaction_cost=TRANSACTION_COST),
        VortexStrategy(period=14, transaction_cost=TRANSACTION_COST),
        HullMAStrategy(period=20, transaction_cost=TRANSACTION_COST),
        SupertrendStrategy(period=14, multiplier=3, transaction_cost=TRANSACTION_COST),
        # 价格动量类策略
        WoodiesCCIStrategy(period=20, overbought=100, oversold=-100, transaction_cost=TRANSACTION_COST),
        GannHiLoStrategy(period=3, transaction_cost=TRANSACTION_COST),
        RVIStrategy(period=10, transaction_cost=TRANSACTION_COST),
        TIIStrategy(n1=40, n2=9, transaction_cost=TRANSACTION_COST),
        POStrategy(short_period=9, long_period=26, transaction_cost=TRANSACTION_COST),
        MADisplacedStrategy(n=20, m=10, transaction_cost=TRANSACTION_COST),
        T3Strategy(n=20, va=0.5, transaction_cost=TRANSACTION_COST),
        ADTMStrategy(n=20, transaction_cost=TRANSACTION_COST),
        ZLMACDStrategy(n1=20, n2=100, transaction_cost=TRANSACTION_COST),
        TMAStrategy(n=20, transaction_cost=TRANSACTION_COST),
        TYPStrategy(n1=10, n2=30, transaction_cost=TRANSACTION_COST),
        KDJDStrategy(n=20, m=60, overbought=70, oversold=30, transaction_cost=TRANSACTION_COST),
        VMAStrategy(n=20, transaction_cost=TRANSACTION_COST),
        FBStrategy(period=20, transaction_cost=TRANSACTION_COST),
        DEMAStrategy(period=20, transaction_cost=TRANSACTION_COST),
        APZStrategy(period=20, multiplier=2, transaction_cost=TRANSACTION_COST),
        ASIStrategy(limit_move_value=0.5, transaction_cost=TRANSACTION_COST),
        AroonOscillatorStrategy(period=25, transaction_cost=TRANSACTION_COST),
        KCStrategy(period=20, multiplier=1.5, transaction_cost=TRANSACTION_COST),
        KSTStrategy(r1=10, r2=15, r3=20, r4=30, s1=10, s2=10, s3=10, s4=15, sig=9, transaction_cost=TRANSACTION_COST),
        TSIStrategy(period=20, transaction_cost=TRANSACTION_COST),
        GuppyMultipleMovingAverageStrategy(transaction_cost=TRANSACTION_COST),
        AlligatorStrategy(transaction_cost=TRANSACTION_COST),
        ZeroLagExponentialMovingAverageStrategy(period=20, transaction_cost=TRANSACTION_COST),
        EhlersSuperSmootherStrategy(period=20, transaction_cost=TRANSACTION_COST),
        EhlersFisherTransformStrategy(transaction_cost=TRANSACTION_COST),
        EhlersMesaAdaptiveMovingAverageStrategy(transaction_cost=TRANSACTION_COST),
        HullMovingAverageStrategy(period=9, transaction_cost=TRANSACTION_COST),
        LeastSquaresMovingAverageStrategy(period=20, transaction_cost=TRANSACTION_COST),
        KaufmanAdaptiveMovingAverageStrategy(period=10, fast_period=2, slow_period=30,
                                             transaction_cost=TRANSACTION_COST),
        TripleExponentialMovingAverageStrategy(period=20, transaction_cost=TRANSACTION_COST),
        McGinleyDynamicStrategy(period=20, transaction_cost=TRANSACTION_COST),
        EhlersInstantaneousTrendlineStrategy(period=20, transaction_cost=TRANSACTION_COST),
        LinearRegressionStrategy(period=20, transaction_cost=TRANSACTION_COST),
        HurstExponentStrategy(period=20, transaction_cost=TRANSACTION_COST),
        FibonacciRetracementStrategy(period=20, transaction_cost=TRANSACTION_COST),
        FractalAdaptiveMovingAverageStrategy(period=16, transaction_cost=TRANSACTION_COST),
        VariableIndexDynamicAverageStrategy(period=14, transaction_cost=TRANSACTION_COST),
        AccelerationDecelerationStrategy(transaction_cost=TRANSACTION_COST),
        AlligatorBalanceStrategy(transaction_cost=TRANSACTION_COST),
        ATRStrategy(transaction_cost=TRANSACTION_COST),
        AutoRegressiveStrategy(transaction_cost=TRANSACTION_COST),
        ChandeMomentumOscillatorStrategy(transaction_cost=TRANSACTION_COST),
        ConnorsRSIStrategy(transaction_cost=TRANSACTION_COST),
        CyberCycleStrategy(transaction_cost=TRANSACTION_COST),
        DetrendedPriceOscillatorStrategy(transaction_cost=TRANSACTION_COST),
        DynamicMomentumIndexStrategy(transaction_cost=TRANSACTION_COST),
        EhlersSignalProcessingStrategy(transaction_cost=TRANSACTION_COST),
        ElderImpulseStrategy(transaction_cost=TRANSACTION_COST),
        ElderSafeZoneStrategy(transaction_cost=TRANSACTION_COST),
        ERStrategy(n=20, transaction_cost=TRANSACTION_COST),
        ErgodicCandlestickOscillatorStrategy(transaction_cost=TRANSACTION_COST),
        FisherInverseStrategy(transaction_cost=TRANSACTION_COST),
        FourierTransformStrategy(transaction_cost=TRANSACTION_COST),
        GatorOscillatorStrategy(transaction_cost=TRANSACTION_COST),
        GopalakrishnanRangeIndexStrategy(transaction_cost=TRANSACTION_COST),
        InertiaIndicatorStrategy(transaction_cost=TRANSACTION_COST),
        InertiaStrategy(transaction_cost=TRANSACTION_COST),
        IntradayMomentumIndexStrategy(transaction_cost=TRANSACTION_COST),
        KairiRelativeIndexStrategy(transaction_cost=TRANSACTION_COST),
        KalmanFilterStrategy(transaction_cost=TRANSACTION_COST),
        KnowSureThingStrategy(transaction_cost=TRANSACTION_COST),
        MachineLearningStrategy(transaction_cost=TRANSACTION_COST),
        ParabolicSARStrategy(transaction_cost=TRANSACTION_COST),
        PercentRankStrategy(transaction_cost=TRANSACTION_COST),
        ProjectionOscillatorStrategy(transaction_cost=TRANSACTION_COST),
        QQEStrategy(transaction_cost=TRANSACTION_COST),
        RelativeMomentumIndexStrategy(transaction_cost=TRANSACTION_COST),
        RelativeVigorIndexStrategy(transaction_cost=TRANSACTION_COST),
        StandardErrorBandsStrategy(transaction_cost=TRANSACTION_COST),
        # TEMAStrategy removed: duplicate of TripleExponentialMovingAverageStrategy (both named "TEMA Strategy")
        # TEMAStrategy(transaction_cost=TRANSACTION_COST),
        TrixStrategyAlt(transaction_cost=TRANSACTION_COST),
        VolatilityBreakoutStrategy(transaction_cost=TRANSACTION_COST),
        WaveletTransformStrategy(transaction_cost=TRANSACTION_COST),
        WilliamsAlligatorStrategy(transaction_cost=TRANSACTION_COST),
        # 成交量类策略
        OnBalanceVolumeStrategy(transaction_cost=TRANSACTION_COST),
        PercentageVolumeOscillatorStrategy(fast_period=12, slow_period=26, signal_period=9,
                                           transaction_cost=TRANSACTION_COST),
        VerticalHorizontalFilterStrategy(period=28, transaction_cost=TRANSACTION_COST),
        TwiggsMoneyFlowStrategy(period=21, transaction_cost=TRANSACTION_COST),
        ChaikinVolatilityStrategy(period=10, roc_period=10, transaction_cost=TRANSACTION_COST),
        ElderForceIndexStrategy(period=13, transaction_cost=TRANSACTION_COST),
        MoneyFlowIndexStrategy(period=14, overbought=80, oversold=20, transaction_cost=TRANSACTION_COST),
        MarketFacilitationIndexStrategy(transaction_cost=TRANSACTION_COST),
        # 价量类策略
        ChaikinMoneyFlowStrategy(period=20, transaction_cost=TRANSACTION_COST),
        AccumulationDistributionStrategy(transaction_cost=TRANSACTION_COST),
        ChaikinOscillatorStrategy(fast_period=3, slow_period=10, transaction_cost=TRANSACTION_COST),
        ForceIndexStrategy(period=13, transaction_cost=TRANSACTION_COST),
        EaseOfMovementStrategy(period=14, transaction_cost=TRANSACTION_COST),
        QstickStrategy(transaction_cost=TRANSACTION_COST),
        # 大盘类策略
        ArmsStrategy(period=14, transaction_cost=TRANSACTION_COST),
        McClellanOscillatorStrategy(transaction_cost=TRANSACTION_COST),
        VolumeWeightedAveragePriceStrategy(period=20, transaction_cost=TRANSACTION_COST),
        TripleScreenTradingSystemStrategy(transaction_cost=TRANSACTION_COST),

        DPOStrategy(n=20, transaction_cost=TRANSACTION_COST),
        ZigZagStrategy(deviation=5, transaction_cost=TRANSACTION_COST),
        FactorScoringStrategy(
            ma_period=20,
            rsi_period=14,
            macd_fast=12,
            macd_slow=26,
            macd_signal=9,
            bb_period=20,
            bb_std=2,
            williams_period=14,
            scoring_threshold=2,
            transaction_cost=TRANSACTION_COST
        ),
        # 新增的N字涨停选股策略
        NZhangTingStrategy(transaction_cost=TRANSACTION_COST),
    ]
    return strategies


def load_btc_data():
    # 从文件中加载比特币数据
    df = pd.read_csv("bitcoin_10_year_daily_data.csv")
    column_mapping = {
        'date': ['Date', 'time', '时间', '日期', '交易日期', '交_易_日_期'],
        'open': ['Open', '开盘价', '开_盘_价'],
        'high': ['High', '最高价', '最_高_价'],
        'low': ['Low', '最低价', '最_低_价'],
        'close': ['Close', '收盘价', '收_盘_价'],
        'volume': ['Volume', '成交量', '成_交_量'],
    }

    # 应用列名映射
    new_columns = {}
    for col in df.columns:
        # 查找最佳匹配
        matched = False
        for standard_name, possible_names in column_mapping.items():
            for possible_name in possible_names:
                if possible_name == col:
                    new_columns[col] = standard_name
                    matched = True
                    break
            if matched:
                break
        # 如果没有匹配到，保持原列名
        if not matched:
            new_columns[col] = col
    df.rename(columns=new_columns, inplace=True)
    
    # 转换日期列为datetime类型并设置为索引
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

    return df


def plot_top_strategies_performance(strategy_cumulative_returns, top_strategy_names, btc_data):
    """
    绘制表现最好的前几个策略的资金曲线
    
    Parameters:
    strategy_cumulative_returns (dict): 策略名称和对应的累计收益序列的字典
    top_strategy_names (list): 表现最好的策略名称列表
    btc_data (DataFrame): 比特币价格数据
    """
    # 创建图表和子图
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
    
    # 绘制每个策略的资金曲线（上方子图）
    colors = ['blue', 'red', 'green', 'orange', 'purple']  # 为前5个策略定义颜色
    
    # 确保有数据可以绘制
    has_data_to_plot = False
    
    # 绘制每个策略的资金曲线
    for i, strategy_name in enumerate(top_strategy_names):
        if strategy_name in strategy_cumulative_returns:
            cumulative_returns = strategy_cumulative_returns[strategy_name]
            # 确保有数据且非空
            if cumulative_returns is not None and len(cumulative_returns) > 0:
                ax1.plot(range(len(cumulative_returns)), cumulative_returns, 
                         label=f'{strategy_name}', linewidth=2, color=colors[i % len(colors)])
                has_data_to_plot = True
    
    ax1.set_title('Top 5 Strategies Performance Comparison', fontsize=16)
    ax1.set_ylabel('Cumulative Return', fontsize=12)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # 绘制比特币价格作为基准（下方子图）
    if 'close' in btc_data.columns and len(btc_data) > 0:
        btc_price = btc_data['close']
        ax2.plot(range(len(btc_price)), btc_price, 
                label='Bitcoin Price', linewidth=2, color='black')
        has_data_to_plot = True
    
    ax2.set_title('Bitcoin Price', fontsize=16)
    ax2.set_xlabel('Time Period', fontsize=12)
    ax2.set_ylabel('Price (USD)', fontsize=12)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    if has_data_to_plot:
        # 保存图表
        plt.tight_layout()
        plt.savefig('top_5_strategies_performance.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"\n资金曲线图已保存为 'top_5_strategies_performance.png'")
    else:
        print("没有足够的数据来绘制资金曲线")

def run_strategies_on_btc():
    strategies = get_all_strategies()
    btc_data = load_btc_data()
    btc_data = btc_data[-1000:]
    stock_code = 'btc_usdt'
    # 对每个策略运行分析
    all_results = []
    strategy_cumulative_returns = {}  # 存储每个策略的累计收益数据用于绘图
    
    for strategy in strategies:
        try:
            metrics = run_strategy(strategy, btc_data, stock_code=stock_code)
            if metrics is not None:
                # 存储结果
                result = {
                    'stock_code':stock_code ,
                    'strategy': strategy.name,
                    'cumulative_return': metrics['cumulative_return'],
                    'annual_return': metrics['annual_return'],
                    'volatility': metrics['volatility'],
                    'sharpe_ratio': metrics['sharpe_ratio'],
                    'max_drawdown': metrics['max_drawdown']
                }
                all_results.append(result)
                
                # 保存策略的累计收益数据用于绘图
                if hasattr(strategy, 'portfolio_value') and strategy.portfolio_value is not None:
                    strategy_cumulative_returns[strategy.name] = strategy.portfolio_value
        except Exception as e:
            print(f"运行策略 {strategy.name} 时出错: {e}")
            traceback.print_exc()

    # 汇总结果
    if all_results:
        results_df = pd.DataFrame(all_results)
        print(f"\n{'=' * 80}")
        print("策略表现汇总")
        print(f"{'=' * 80}")

        # 按策略分组，显示平均表现
        summary = results_df.groupby('strategy').agg({
            'cumulative_return': 'mean',
            'annual_return': 'mean',
            'volatility': 'mean',
            'sharpe_ratio': 'mean',
            'max_drawdown': 'mean'
        }).round(4)

        # 按夏普比率从高到低排序
        summary = summary.sort_values('sharpe_ratio', ascending=False)

        # 设置pandas显示选项，确保完整显示所有数据而不省略
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)

        print("\n各策略平均表现 (按夏普比率排序):")
        print(summary)

        # 找出表现最好的前5个策略（按夏普比率）
        top_5_strategies = summary.head(5)
        print(f"\n表现最好的前5个策略:")
        print(top_5_strategies)
        
        # 绘制前5名策略的资金曲线
        # plot_top_strategies_performance(strategy_cumulative_returns, top_5_strategies.index.tolist(), btc_data)
        
        # 找出表现最好的策略（按夏普比率）
        if not results_df.empty:
            best_strategy = results_df.loc[results_df['sharpe_ratio'].idxmax()]
            print(f"\n表现最好的策略:")
            print(f"策略: {best_strategy['strategy']}")
            print(f"股票: {best_strategy['stock_code']}")
            print(f"夏普比率: {best_strategy['sharpe_ratio']:.4f}")
            print(f"累计收益: {best_strategy['cumulative_return']:.2%}")
            print(f"年化收益: {best_strategy['annual_return']:.2%}")
            print(f"波动率: {best_strategy['volatility']:.2%}")
            print(f"最大回撤: {best_strategy['max_drawdown']:.2%}")


def main():
    """
    主函数
    """
    # 设置日志
    logger = setup_logging()
    logger.info("量化策略验证系统启动")
    print("量化策略验证系统")  # 仅在控制台打印一次

    # 运行所有股票的策略分析
    run_strategies_on_all_stocks()
    
    # 运行比特币策略分析
    print(f"\n{'='*80}")
    print("比特币策略分析")
    print(f"{'='*80}")
    run_strategies_on_btc()

if __name__ == "__main__":
    main()
   