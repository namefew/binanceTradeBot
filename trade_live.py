"""
实时交易启动脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.binance_client import BinanceClient
from strategies.ma_crossover import MovingAverageCrossover
from strategies.rsi_strategy import RSIStrategy
from strategies.bollinger_bands import BollingerBandsStrategy
from trading.engine import TradingEngine


def main():
    print("=" * 60)
    print("币安交易机器人 - 实时交易系统")
    print("=" * 60)
    print("\n⚠️  警告: 这将使用真实资金进行交易！")
    print("建议先在测试网上进行测试\n")
    
    # 确认使用测试网还是实盘
    use_testnet = input("是否使用测试网? (y/n, 默认y): ").strip().lower()
    if use_testnet == '' or use_testnet == 'y':
        testnet = True
        print("使用测试网模式")
    else:
        testnet = False
        print("⚠️  使用实盘模式 - 请谨慎操作！")
        confirm = input("确认继续? (输入yes确认): ").strip().lower()
        if confirm != 'yes':
            print("已取消")
            return
    
    # 配置参数
    print("\n=== 配置交易参数 ===")
    symbol = input("交易对 (默认BTCUSDT): ").strip() or "BTCUSDT"
    timeframe = input("时间周期 (默认1h): ").strip() or "1h"
    
    print("\n选择策略:")
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
    
    position_size = float(input("仓位比例 (默认0.1): ") or "0.1")
    check_interval = int(input("检查间隔秒数 (默认60): ") or "60")
    
    print(f"\n=== 启动交易引擎 ===")
    print(f"策略: {strategy.name}")
    print(f"交易对: {symbol}")
    print(f"时间周期: {timeframe}")
    print(f"仓位比例: {position_size * 100}%")
    print(f"检查间隔: {check_interval}秒")
    
    # 创建客户端和交易引擎
    try:
        client = BinanceClient(testnet=testnet)
        
        # 测试连接
        if not client.ping():
            print("错误: 无法连接到币安API")
            return
        
        print("✓ API连接成功")
        
        # 显示账户信息
        balances = client.get_account_balance()
        print(f"\n当前账户余额:")
        for asset, info in balances.items():
            print(f"  {asset}: {info['total']:.6f}")
        
        # 创建交易引擎
        engine = TradingEngine(
            strategy=strategy,
            symbol=symbol,
            timeframe=timeframe,
            client=client,
            position_size=position_size,
            check_interval=check_interval
        )
        
        print("\n按 Ctrl+C 停止交易引擎\n")
        
        # 启动交易引擎
        engine.start()
        
    except KeyboardInterrupt:
        print("\n用户中断")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n交易引擎已停止")


if __name__ == "__main__":
    main()
