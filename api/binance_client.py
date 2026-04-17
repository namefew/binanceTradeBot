"""
币安API客户端
提供行情数据获取和交易执行功能
"""
import os
from typing import Optional, List, Dict
from datetime import datetime
import pandas as pd
from binance.client import Client
from binance.enums import *
from dotenv import load_dotenv

load_dotenv()


class BinanceClient:
    """币安API客户端封装"""
    
    def __init__(self, testnet: bool = None):
        """
        初始化币安客户端
        
        Args:
            testnet: 是否使用测试网，默认从环境变量读取
        """
        self.api_key = os.getenv('BINANCE_API_KEY')
        self.api_secret = os.getenv('BINANCE_API_SECRET')
        
        if testnet is None:
            testnet = os.getenv('BINANCE_TESTNET', 'true').lower() == 'true'
        
        # 初始化客户端
        if testnet:
            self.client = Client(self.api_key, self.api_secret, testnet=True)
        else:
            self.client = Client(self.api_key, self.api_secret)
        
        self.testnet = testnet
    
    # ==================== 行情数据 ====================
    
    def get_klines(self, symbol: str, interval: str, 
                   start_str: str = None, end_str: str = None,
                   limit: int = 1000) -> pd.DataFrame:
        """
        获取K线数据
        
        Args:
            symbol: 交易对，如 BTCUSDT
            interval: 时间周期，如 1m, 5m, 15m, 1h, 4h, 1d
            start_str: 开始时间，格式: '2023-01-01'
            end_str: 结束时间
            limit: 获取条数，最大1000
            
        Returns:
            DataFrame包含: open_time, open, high, low, close, volume, close_time
        """
        # 构建参数字典，只添加非None的参数
        params = {
            'symbol': symbol,
            'interval': interval,
        }
        
        if start_str:
            params['startTime'] = int(pd.to_datetime(start_str).timestamp() * 1000)
        if end_str:
            params['endTime'] = int(pd.to_datetime(end_str).timestamp() * 1000)
        if limit:
            params['limit'] = limit
        
        klines = self.client.get_klines(**params)
        
        df = pd.DataFrame(klines, columns=[
            'open_time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        
        # 转换时间戳
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
        
        # 转换数值类型
        numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'quote_volume']
        for col in numeric_cols:
            df[col] = df[col].astype(float)
        
        return df
    
    def get_ticker_price(self, symbol: str) -> float:
        """获取最新价格"""
        ticker = self.client.get_symbol_ticker(symbol=symbol)
        return float(ticker['price'])
    
    def get_account_balance(self) -> Dict:
        """获取账户余额"""
        account = self.client.get_account()
        balances = {}
        for balance in account['balances']:
            asset = balance['asset']
            free = float(balance['free'])
            locked = float(balance['locked'])
            if free > 0 or locked > 0:
                balances[asset] = {
                    'free': free,
                    'locked': locked,
                    'total': free + locked
                }
        return balances
    
    def get_symbol_info(self, symbol: str) -> Dict:
        """获取交易对信息"""
        exchange_info = self.client.get_exchange_info()
        for s in exchange_info['symbols']:
            if s['symbol'] == symbol:
                return s
        return None
    
    def get_all_symbols(self, quote_asset: str = 'USDT') -> List[str]:
        """
        获取所有交易对列表
        
        Args:
            quote_asset: 计价资产，默认 USDT（如 BTCUSDT, ETHUSDT）
            
        Returns:
            交易对列表，如 ['BTCUSDT', 'ETHUSDT', ...]
        """
        try:
            exchange_info = self.client.get_exchange_info()
            symbols = []
            
            for s in exchange_info['symbols']:
                # 只返回指定计价资产的交易对
                if s['status'] == 'TRADING' and s['quoteAsset'] == quote_asset:
                    symbols.append(s['symbol'])
            
            # 按字母顺序排序
            symbols.sort()
            return symbols
        except Exception as e:
            print(f"获取交易对列表失败: {e}")
            return []
    
    # ==================== 交易功能 ====================
    
    def create_order(self, symbol: str, side: str, order_type: str,
                     quantity: float = None, quote_order_qty: float = None,
                     price: float = None, stop_price: float = None) -> Dict:
        """
        创建订单
        
        Args:
            symbol: 交易对
            side: BUY 或 SELL
            order_type: MARKET, LIMIT, STOP_LOSS_LIMIT等
            quantity: 数量（市价单可选）
            quote_order_qty: 报价资产数量（用于市价买单）
            price: 限价单价格
            stop_price: 止损价格
            
        Returns:
            订单信息
        """
        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
        }
        
        if quantity:
            params['quantity'] = quantity
        if quote_order_qty:
            params['quoteOrderQty'] = quote_order_qty
        if price:
            params['price'] = price
        if stop_price:
            params['stopPrice'] = stop_price
        
        try:
            order = self.client.create_order(**params)
            return order
        except Exception as e:
            print(f"订单创建失败: {e}")
            raise
    
    def market_buy(self, symbol: str, quote_order_qty: float) -> Dict:
        """市价买入"""
        return self.create_order(
            symbol=symbol,
            side=SIDE_BUY,
            order_type=ORDER_TYPE_MARKET,
            quote_order_qty=quote_order_qty
        )
    
    def market_sell(self, symbol: str, quantity: float) -> Dict:
        """市价卖出"""
        return self.create_order(
            symbol=symbol,
            side=SIDE_SELL,
            order_type=ORDER_TYPE_MARKET,
            quantity=quantity
        )
    
    def limit_buy(self, symbol: str, quantity: float, price: float) -> Dict:
        """限价买入"""
        return self.create_order(
            symbol=symbol,
            side=SIDE_BUY,
            order_type=ORDER_TYPE_LIMIT,
            quantity=quantity,
            price=price,
            time_in_force=TIME_IN_FORCE_GTC
        )
    
    def limit_sell(self, symbol: str, quantity: float, price: float) -> Dict:
        """限价卖出"""
        return self.create_order(
            symbol=symbol,
            side=SIDE_SELL,
            order_type=ORDER_TYPE_LIMIT,
            quantity=quantity,
            price=price,
            time_in_force=TIME_IN_FORCE_GTC
        )
    
    def cancel_order(self, symbol: str, order_id: int) -> Dict:
        """取消订单"""
        return self.client.cancel_order(symbol=symbol, orderId=order_id)
    
    def get_order_status(self, symbol: str, order_id: int) -> Dict:
        """查询订单状态"""
        return self.client.get_order(symbol=symbol, orderId=order_id)
    
    def get_open_orders(self, symbol: str = None) -> List[Dict]:
        """获取当前挂单"""
        if symbol:
            return self.client.get_open_orders(symbol=symbol)
        return self.client.get_open_orders()
    
    def get_trade_history(self, symbol: str, limit: int = 500) -> List[Dict]:
        """获取交易历史"""
        return self.client.get_my_trades(symbol=symbol, limit=limit)
    
    # ==================== 辅助方法 ====================
    
    def get_server_time(self) -> datetime:
        """获取服务器时间"""
        server_time = self.client.get_server_time()
        return datetime.fromtimestamp(server_time['serverTime'] / 1000)
    
    def ping(self) -> bool:
        """测试连接"""
        try:
            self.client.ping()
            return True
        except Exception as e:
            print(f"连接测试失败: {e}")
            return False
