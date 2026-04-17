"""
机器学习策略
使用简单的机器学习模型预测价格走势
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy
from strategies.technical_indicators import TechnicalIndicators

class MachineLearningStrategy(BaseStrategy):
    """
    机器学习策略
    使用简单的机器学习模型预测价格走势
    """
    
    def __init__(self, period=20, transaction_cost=0.001, position_size=1.0):
        super().__init__("Machine Learning Strategy", transaction_cost, indicator_short_name="Machine Learning", position_size=position_size)
        self.period = period
    
    def generate_signals(self):
        """
        生成交易信号
        """
        # 简单的机器学习模型 (线性回归简化版)
        price = self.data['close']
        
        # 构建特征
        features = pd.DataFrame(index=price.index)
        features['returns'] = price.pct_change()
        features['sma'] = price.rolling(window=self.period//2).mean() / price - 1
        features['volatility'] = features['returns'].rolling(window=self.period).std()
        features['rsi'] = TechnicalIndicators.rsi(price, 14) / 100
        macd_line, signal_line, _ = TechnicalIndicators.macd(price)
        features['macd'] = macd_line - signal_line
        
        # 简单线性组合预测
        weights = np.array([0.3, 0.2, 0.2, 0.15, 0.15])  # 预设权重
        features.dropna(inplace=True)
        
        # 预测信号
        prediction = np.zeros(len(features))
        feature_values = features.values
        
        for i in range(len(features)):
            if i < len(weights):
                prediction[i] = np.dot(feature_values[i], weights[:len(feature_values[i])])
            else:
                prediction[i] = np.dot(feature_values[i], weights)
        
        predictions = pd.Series(prediction, index=features.index)
        
        # 生成信号
        self.signals = pd.Series(0, index=self.data.index)
        
        # 当预测为正时买入
        # 当预测为负时卖出
        
        # 确保索引对齐
        aligned_predictions = predictions.reindex(self.signals.index, fill_value=0)
        
        buy_mask = aligned_predictions > 0
        sell_mask = aligned_predictions < 0
        
        self.signals[buy_mask] = 1
        self.signals[sell_mask] = -1