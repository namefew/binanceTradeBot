"""
命令行回测脚本
用于快速运行策略回测
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.binance_client import BinanceClient
from strategies.ma_crossover import MovingAverageCrossover
from strategies.rsi_strategy import RSIStrategy
from strategies.bollinger_bands import BollingerBandsStrategy
from backtest.engine import BacktestEngine
from utils.performance import PerformanceAnalyzer
from visualization.charts import ChartGenerator


def main():
    print("=" * 60)
    print("币安交易机器人 - 回测系统")
    print("=" * 60)
    
    # 配置参数
    SYMBOL = "BTCUSDT"
    TIMEFRAME = "1h"
    DAYS = 90
    INITIAL_CAPITAL = 10000
    COMMISSION_RATE = 0.001
    POSITION_SIZE = 0.1
    
    print(f"\n配置信息:")
    print(f"  交易对: {SYMBOL}")
    print(f"  时间周期: {TIMEFRAME}")
    print(f"  回测天数: {DAYS}")
    print(f"  初始资金: ${INITIAL_CAPITAL}")
    print(f"  手续费率: {COMMISSION_RATE * 100}%")
    print(f"  仓位比例: {POSITION_SIZE * 100}%")
    
    # 选择策略
    print("\n请选择策略:")
    print("1. 双均线交叉策略")
    print("2. RSI超买超卖策略")
    print("3. 布林带策略")
    
    choice = input("\n请输入策略编号 (1-3): ").strip()
    
    if choice == '1':
        short_window = int(input("短期均线周期 (默认10): ") or "10")
        long_window = int(input("长期均线周期 (默认30): ") or "30")
        strategy = MovingAverageCrossover(short_window=short_window, long_window=long_window)
        
    elif choice == '2':
        period = int(input("RSI周期 (默认14): ") or "14")
        oversold = float(input("超卖线 (默认30): ") or "30")
        overbought = float(input("超买线 (默认70): ") or "70")
        strategy = RSIStrategy(period=period, oversold=oversold, overbought=overbought)
        
    elif choice == '3':
        period = int(input("布林带周期 (默认20): ") or "20")
        num_std = float(input("标准差倍数 (默认2.0): ") or "2.0")
        strategy = BollingerBandsStrategy(period=period, num_std=num_std)
        
    else:
        print("无效选择，使用默认策略（双均线交叉）")
        strategy = MovingAverageCrossover()
    
    print(f"\n已选择策略: {strategy.name}")
    
    # 加载数据
    print("\n正在加载历史数据...")
    try:
        client = BinanceClient(testnet=True)
        data = client.get_klines(
            symbol=SYMBOL,
            interval=TIMEFRAME,
            limit=1000
        )
        
        if data.empty:
            print("错误: 未能获取数据")
            return
        
        print(f"成功加载 {len(data)} 条K线数据")
        print(f"时间范围: {data['open_time'].min()} 至 {data['open_time'].max()}")
        
    except Exception as e:
        print(f"加载数据失败: {e}")
        return
    
    # 运行回测
    print("\n开始回测...")
    engine = BacktestEngine(
        strategy=strategy,
        initial_capital=INITIAL_CAPITAL,
        commission_rate=COMMISSION_RATE,
        position_size=POSITION_SIZE
    )
    
    result = engine.run(data)
    
    # 显示结果
    print("\n" + "=" * 60)
    print("回测结果")
    print("=" * 60)
    
    metrics = result.summary()
    for key, value in metrics.items():
        print(f"{key}: {value}")
    
    # 计算详细绩效指标
    trades_for_analysis = [{
        'signal': t.signal,
        'price': t.price,
        'timestamp': t.timestamp
    } for t in result.trades]
    
    analyzer = PerformanceAnalyzer(result.equity_curve, result.timestamps)
    detailed_metrics = analyzer.get_all_metrics(trades_for_analysis)
    
    print("\n详细绩效指标:")
    for key, value in detailed_metrics.items():
        print(f"  {key}: {value}")
    
    # 保存图表
    save_charts = input("\n是否保存图表? (y/n): ").strip().lower()
    if save_charts == 'y':
        try:
            import plotly.io as pio
            
            # 资金曲线
            equity_fig = ChartGenerator.plot_equity_curve(
                result.equity_curve,
                result.timestamps,
                f"资金曲线 - {strategy.name}"
            )
            pio.write_html(equity_fig, "equity_curve.html")
            print("✓ 资金曲线已保存为 equity_curve.html")
            
            # 回撤曲线
            dd_fig = ChartGenerator.plot_drawdown(
                result.equity_curve,
                result.timestamps
            )
            pio.write_html(dd_fig, "drawdown.html")
            print("✓ 回撤曲线已保存为 drawdown.html")
            
            # 交易信号图
            trade_fig = ChartGenerator.plot_trades_with_price(
                data, trades_for_analysis,
                f"交易信号 - {strategy.name}"
            )
            pio.write_html(trade_fig, "trades.html")
            print("✓ 交易信号图已保存为 trades.html")
            
            print("\n所有图表已保存到当前目录")
        
        except Exception as e:
            print(f"保存图表失败: {e}")
    
    print("\n回测完成！")


if __name__ == "__main__":
    main()
