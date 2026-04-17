"""
实时交易引擎
根据策略信号执行实际交易
"""
import time
import logging
from datetime import datetime
from typing import Optional
from api.binance_client import BinanceClient
from strategies.base_strategy import Strategy, Signal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TradingEngine:
    """实时交易引擎"""
    
    def __init__(self, strategy: Strategy, symbol: str, timeframe: str,
                 client: Optional[BinanceClient] = None,
                 position_size: float = 0.1, check_interval: int = 60):
        """
        初始化交易引擎
        
        Args:
            strategy: 交易策略
            symbol: 交易对，如 BTCUSDT
            timeframe: 时间周期，如 1m, 5m, 1h
            client: 币安客户端，未提供则创建新实例
            position_size: 每次交易使用的资金比例
            check_interval: 检查信号的间隔（秒）
        """
        self.strategy = strategy
        self.symbol = symbol
        self.timeframe = timeframe
        self.client = client or BinanceClient()
        self.position_size = position_size
        self.check_interval = check_interval
        self.is_running = False
        self.last_signal_time = None
    
    def start(self):
        """启动交易引擎"""
        logger.info(f"启动交易引擎 - 策略: {self.strategy.name}, 交易对: {self.symbol}")
        self.is_running = True
        
        # 获取初始账户信息
        balances = self.client.get_account_balance()
        logger.info(f"当前账户余额: {balances}")
        
        try:
            while self.is_running:
                self._check_and_trade()
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            logger.info("交易引擎被用户中断")
        except Exception as e:
            logger.error(f"交易引擎异常: {e}", exc_info=True)
        finally:
            self.stop()
    
    def stop(self):
        """停止交易引擎"""
        logger.info("停止交易引擎...")
        self.is_running = False
    
    def _check_and_trade(self):
        """检查信号并执行交易"""
        try:
            # 获取最新K线数据
            data = self.client.get_klines(
                symbol=self.symbol,
                interval=self.timeframe,
                limit=100
            )
            
            if data.empty:
                logger.warning("未能获取K线数据")
                return
            
            # 生成信号
            current_index = len(data) - 1
            signal = self.strategy.generate_signal(data, current_index)
            
            current_price = data['close'].iloc[current_index]
            timestamp = datetime.now()
            
            # 避免重复信号
            if self.last_signal_time and (timestamp - self.last_signal_time).seconds < self.check_interval:
                return
            
            # 执行交易
            if signal == Signal.BUY:
                self._execute_buy(current_price)
                self.last_signal_time = timestamp
                logger.info(f"[{timestamp}] 买入信号 @ {current_price}")
                
            elif signal == Signal.SELL:
                self._execute_sell(current_price)
                self.last_signal_time = timestamp
                logger.info(f"[{timestamp}] 卖出信号 @ {current_price}")
            
            else:
                logger.debug(f"[{timestamp}] 持有信号 @ {current_price}")
        
        except Exception as e:
            logger.error(f"检查交易信号时出错: {e}", exc_info=True)
    
    def _execute_buy(self, price: float):
        """执行买入操作"""
        try:
            # 获取账户余额
            balances = self.client.get_account_balance()
            
            # 假设使用USDT购买
            usdt_balance = balances.get('USDT', {}).get('free', 0)
            
            if usdt_balance <= 0:
                logger.warning("USDT余额不足")
                return
            
            # 计算买入金额
            buy_amount = usdt_balance * self.position_size
            
            # 获取交易对信息以确定精度
            symbol_info = self.client.get_symbol_info(self.symbol)
            if not symbol_info:
                logger.error("无法获取交易对信息")
                return
            
            # 执行市价买入
            order = self.client.market_buy(self.symbol, buy_amount)
            logger.info(f"买入订单已提交: {order}")
            
            # 更新策略状态
            quantity = float(order.get('executedQty', 0))
            self.strategy.on_trade_executed(Signal.BUY, price, quantity)
        
        except Exception as e:
            logger.error(f"执行买入失败: {e}", exc_info=True)
    
    def _execute_sell(self, price: float):
        """执行卖出操作"""
        try:
            # 获取账户余额
            balances = self.client.get_account_balance()
            
            # 提取基础资产符号（如BTCUSDT -> BTC）
            base_asset = self.symbol.replace('USDT', '').replace('BUSD', '').replace('BNB', '')
            base_balance = balances.get(base_asset, {}).get('free', 0)
            
            if base_balance <= 0:
                logger.warning(f"{base_asset}余额不足")
                return
            
            # 执行市价卖出
            order = self.client.market_sell(self.symbol, base_balance)
            logger.info(f"卖出订单已提交: {order}")
            
            # 更新策略状态
            quantity = float(order.get('executedQty', 0))
            self.strategy.on_trade_executed(Signal.SELL, price, quantity)
        
        except Exception as e:
            logger.error(f"执行卖出失败: {e}", exc_info=True)
    
    def get_status(self) -> dict:
        """获取交易引擎状态"""
        balances = self.client.get_account_balance()
        return {
            'strategy': self.strategy.name,
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'is_running': self.is_running,
            'position': self.strategy.position,
            'cash': self.strategy.cash,
            'balances': balances
        }
