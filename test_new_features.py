"""
测试新功能：批量回测和策略追踪
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.binance_client import BinanceClient
from main import get_all_strategies
from backtest.engine import BacktestEngine
from data.data_source import load_data
from datetime import datetime, timedelta
import json

def test_batch_backtest():
    """测试批量回测功能"""
    print("=" * 80)
    print("测试1: 批量回测所有策略")
    print("=" * 80)
    
    # 获取所有策略
    all_strategies = get_all_strategies()
    print(f"\n找到 {len(all_strategies)} 个策略\n")
    
    # 加载数据（只加载一次）
    print("正在加载数据...")
    client = BinanceClient(testnet=True)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    data = client.get_klines(
        symbol='BTCUSDT',
        interval='1h',
        start_str=start_date.strftime('%Y-%m-%d'),
        end_str=end_date.strftime('%Y-%m-%d'),
        limit=1000
    )
    
    if data.empty:
        print("❌ 数据加载失败")
        return
    
    print(f"✅ 成功加载 {len(data)} 条K线数据\n")
    
    # 测试前5个策略
    test_count = min(5, len(all_strategies))
    print(f"测试前 {test_count} 个策略:\n")
    
    results = []
    for i in range(test_count):
        strategy = all_strategies[i]
        print(f"[{i+1}/{test_count}] 测试: {strategy.name}")
        
        try:
            engine = BacktestEngine(
                strategy=strategy,
                initial_capital=10000,
                commission_rate=0.001,
                position_size=0.1
            )
            result = engine.run(data)
            
            total_return = (result.final_capital / result.initial_capital - 1) * 100
            
            results.append({
                '策略': strategy.name,
                '收益率': f"{total_return:.2f}%",
                '交易次数': result.total_trades,
                '最大回撤': f"{result.max_drawdown*100:.2f}%"
            })
            
            print(f"  ✅ 完成 - 收益率: {total_return:.2f}%, 交易: {result.total_trades}次")
        except Exception as e:
            print(f"  ❌ 失败: {str(e)}")
    
    # 显示结果汇总
    print("\n" + "=" * 80)
    print("结果汇总:")
    print("=" * 80)
    for r in results:
        print(f"{r['策略']:<40} | 收益: {r['收益率']:>8} | 交易: {r['交易次数']:>3}次 | 回撤: {r['最大回撤']}")
    
    print("\n✅ 批量回测测试完成！\n")


def test_strategy_tracking():
    """测试策略追踪功能"""
    print("=" * 80)
    print("测试2: 策略追踪")
    print("=" * 80)
    
    # 选择一个策略
    all_strategies = get_all_strategies()
    strategy = all_strategies[0]  # 使用第一个策略
    
    print(f"\n选择策略: {strategy.name}")
    print("交易对: BTCUSDT")
    print("时间周期: 1h")
    print("回测天数: 7天\n")
    
    # 加载数据
    client = BinanceClient(testnet=True)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    data = client.get_klines(
        symbol='BTCUSDT',
        interval='1h',
        start_str=start_date.strftime('%Y-%m-%d'),
        end_str=end_date.strftime('%Y-%m-%d'),
        limit=1000
    )
    
    if data.empty:
        print("❌ 数据加载失败")
        return
    
    print(f"✅ 加载 {len(data)} 条K线数据\n")
    
    # 运行回测
    print("运行策略...")
    engine = BacktestEngine(
        strategy=strategy,
        initial_capital=10000,
        commission_rate=0.001,
        position_size=0.1
    )
    result = engine.run(data)
    
    print(f"✅ 策略运行完成\n")
    
    # 创建追踪记录
    tracking_record = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'strategy': strategy.name,
        'symbol': 'BTCUSDT',
        'timeframe': '1h',
        'days': 7,
        'initial_capital': 10000,
        'final_capital': result.final_capital,
        'total_return': (result.final_capital / 10000 - 1) * 100,
        'max_drawdown': result.max_drawdown * 100,
        'sharpe_ratio': result.sharpe_ratio,
        'total_trades': result.total_trades,
        'win_rate': result.win_rate * 100 if hasattr(result, 'win_rate') else 0
    }
    
    # 保存到文件
    history_file = 'tracking_history.json'
    history = []
    
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except:
            history = []
    
    history.append(tracking_record)
    
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    
    print("📊 追踪结果:")
    print(f"  初始资金: ${tracking_record['initial_capital']}")
    print(f"  最终资金: ${tracking_record['final_capital']:.2f}")
    print(f"  总收益率: {tracking_record['total_return']:.2f}%")
    print(f"  最大回撤: {tracking_record['max_drawdown']:.2f}%")
    print(f"  夏普比率: {tracking_record['sharpe_ratio']:.2f}")
    print(f"  交易次数: {tracking_record['total_trades']}")
    print(f"  胜率: {tracking_record['win_rate']:.2f}%")
    print(f"\n✅ 已保存到 {history_file}")
    
    # 显示历史记录
    if len(history) > 1:
        print(f"\n📈 历史追踪记录 ({len(history)} 条):")
        for i, record in enumerate(history[-5:], 1):  # 显示最后5条
            print(f"  {i}. {record['timestamp']} - 收益: {record['total_return']:.2f}%")


if __name__ == "__main__":
    print("\n🧪 开始测试新功能...\n")
    
    # 测试批量回测
    test_batch_backtest()
    
    # 测试策略追踪
    test_strategy_tracking()
    
    print("\n" + "=" * 80)
    print("✅ 所有测试完成！")
    print("=" * 80)
