"""
可视化工具
绘制资金曲线、交易信号等图表
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import List, Dict
from datetime import datetime


class ChartGenerator:
    """图表生成器"""
    
    @staticmethod
    def plot_equity_curve(equity_curve: List[float], 
                          timestamps: List[datetime] = None,
                          title: str = "资金曲线") -> go.Figure:
        """
        绘制资金曲线
        
        Args:
            equity_curve: 权益曲线数据
            timestamps: 时间戳列表
            title: 图表标题
            
        Returns:
            Plotly图表对象
        """
        fig = go.Figure()
        
        x_data = timestamps if timestamps else list(range(len(equity_curve)))
        
        fig.add_trace(go.Scatter(
            x=x_data,
            y=equity_curve,
            mode='lines',
            name='权益',
            line=dict(color='#1f77b4', width=2),
            fill='tozeroy',
            fillcolor='rgba(31, 119, 180, 0.1)'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title='时间' if timestamps else '时间点',
            yaxis_title='资金',
            template='plotly_white',
            hovermode='x unified',
            height=500
        )
        
        return fig
    
    @staticmethod
    def plot_candlestick_with_trades(data: pd.DataFrame,
                                     trades: List[Dict],
                                     title: str = "K线图与交易信号") -> go.Figure:
        """
        绘制K线蜡烛图并叠加交易信号
        
        Args:
            data: K线数据，包含open_time, open, high, low, close字段
            trades: 交易记录列表
            title: 图表标题
            
        Returns:
            Plotly图表对象
        """
        # 创建子图：K线图 + 成交量
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3],
            subplot_titles=(title, '成交量')
        )
        
        # 1. 绘制K线蜡烛图
        fig.add_trace(go.Candlestick(
            x=data['open_time'],
            open=data['open'],
            high=data['high'],
            low=data['low'],
            close=data['close'],
            name='K线',
            increasing_line_color='#26a69a',  # 涨 - 绿色
            decreasing_line_color='#ef5350',  # 跌 - 红色
            increasing_fillcolor='#26a69a',
            decreasing_fillcolor='#ef5350'
        ), row=1, col=1)
        
        # 2. 标记买入和卖出点
        buy_signals = [t for t in trades if t.get('signal') == 'BUY' or str(t.get('signal')).upper() == 'SIGNAL.BUY']
        sell_signals = [t for t in trades if t.get('signal') == 'SELL' or str(t.get('signal')).upper() == 'SIGNAL.SELL']
        
        # 买入信号
        if buy_signals:
            buy_times = [t.get('timestamp') for t in buy_signals]
            buy_prices = [t.get('price') for t in buy_signals]
            buy_quantities = [t.get('quantity', 0) for t in buy_signals]
            buy_commissions = [t.get('commission', 0) for t in buy_signals]
            
            fig.add_trace(go.Scatter(
                x=buy_times,
                y=buy_prices,
                mode='markers+text',
                name='🟢 买入',
                marker=dict(
                    symbol='arrow-up',
                    size=22,
                    color='#00ff00',
                    line=dict(width=3, color='white')
                ),
                text=['💰买'] * len(buy_times),
                textposition='bottom center',
                textfont=dict(size=12, color='#00ff00', family='Arial Black'),
                hovertemplate='<b>🟢 买入信号</b><br>' +
                             '<b>时间</b>: %{x}<br>' +
                             '<b>价格</b>: $%{y:.2f}<br>' +
                             '<b>数量</b>: %{customdata[0]:.6f}<br>' +
                             '<b>手续费</b>: $%{customdata[1]:.4f}<extra></extra>',
                customdata=list(zip(buy_quantities, buy_commissions))
            ), row=1, col=1)
        
        # 卖出信号
        if sell_signals:
            sell_times = [t.get('timestamp') for t in sell_signals]
            sell_prices = [t.get('price') for t in sell_signals]
            sell_quantities = [t.get('quantity', 0) for t in sell_signals]
            sell_commissions = [t.get('commission', 0) for t in sell_signals]
            
            fig.add_trace(go.Scatter(
                x=sell_times,
                y=sell_prices,
                mode='markers+text',
                name='🔴 卖出',
                marker=dict(
                    symbol='arrow-down',
                    size=22,
                    color='#ff0000',
                    line=dict(width=3, color='white')
                ),
                text=['💸卖'] * len(sell_times),
                textposition='top center',
                textfont=dict(size=12, color='#ff0000', family='Arial Black'),
                hovertemplate='<b>🔴 卖出信号</b><br>' +
                             '<b>时间</b>: %{x}<br>' +
                             '<b>价格</b>: $%{y:.2f}<br>' +
                             '<b>数量</b>: %{customdata[0]:.6f}<br>' +
                             '<b>手续费</b>: $%{customdata[1]:.4f}<extra></extra>',
                customdata=list(zip(sell_quantities, sell_commissions))
            ), row=1, col=1)
        
        # 3. 绘制成交量柱状图
        colors = ['#26a69a' if data['close'].iloc[i] >= data['open'].iloc[i] else '#ef5350' 
                  for i in range(len(data))]
        
        fig.add_trace(go.Bar(
            x=data['open_time'],
            y=data['volume'],
            name='成交量',
            marker_color=colors,
            opacity=0.7
        ), row=2, col=1)
        
        # 更新布局
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(size=18, family='Arial Black')
            ),
            template='plotly_white',
            height=800,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=12)
            ),
            xaxis_rangeslider_visible=False,  # 隐藏范围滑块
            plot_bgcolor='rgba(240, 240, 240, 0.3)',
            hovermode='x unified'
        )
        
        # 更新坐标轴
        fig.update_xaxes(title_text="⏰ 时间", row=2, col=1)
        fig.update_yaxes(title_text="💰 价格 (USDT)", row=1, col=1)
        fig.update_yaxes(title_text="📊 成交量", row=2, col=1)
        
        return fig
    
    @staticmethod
    def plot_trades_with_price(data: pd.DataFrame, 
                               trades: List[Dict],
                               title: str = "交易信号图") -> go.Figure:
        """
        绘制价格图和交易信号（优化版）
        
        Args:
            data: K线数据，包含open_time, close等字段
            trades: 交易记录列表，包含timestamp, signal, price字段
            title: 图表标题
            
        Returns:
            Plotly图表对象
        """
        fig = make_subplots(rows=1, cols=1)
        
        # 绘制收盘价 - 使用渐变色彩
        fig.add_trace(go.Scatter(
            x=data['open_time'],
            y=data['close'],
            mode='lines',
            name='收盘价',
            line=dict(color='#2c3e50', width=2.5),
            hovertemplate='<b>时间</b>: %{x}<br><b>价格</b>: $%{y:.2f}<extra></extra>'
        ))
        
        # 标记买入和卖出点
        buy_signals = [t for t in trades if t.get('signal') == 'BUY' or str(t.get('signal')).upper() == 'SIGNAL.BUY']
        sell_signals = [t for t in trades if t.get('signal') == 'SELL' or str(t.get('signal')).upper() == 'SIGNAL.SELL']
        
        # 买入信号 - 绿色向上箭头，带标注
        if buy_signals:
            buy_times = [t.get('timestamp') for t in buy_signals]
            buy_prices = [t.get('price') for t in buy_signals]
            buy_quantities = [t.get('quantity', 0) for t in buy_signals]
            buy_commissions = [t.get('commission', 0) for t in buy_signals]
            
            # 添加买入标记点
            fig.add_trace(go.Scatter(
                x=buy_times,
                y=buy_prices,
                mode='markers+text',
                name='🟢 买入',
                marker=dict(
                    symbol='arrow-up', 
                    size=20, 
                    color='#27ae60',
                    line=dict(width=3, color='white')
                ),
                text=['💰BUY'] * len(buy_times),
                textposition='bottom center',
                textfont=dict(size=11, color='#27ae60', family='Arial Black'),
                hovertemplate='<b>🟢 买入信号</b><br>' +
                             '<b>时间</b>: %{x}<br>' +
                             '<b>价格</b>: $%{y:.2f}<br>' +
                             '<b>数量</b>: %{customdata[0]:.6f}<br>' +
                             '<b>手续费</b>: $%{customdata[1]:.4f}<br>' +
                             '<extra></extra>',
                customdata=list(zip(buy_quantities, buy_commissions))
            ))
        
        # 卖出信号 - 红色向下箭头，带标注
        if sell_signals:
            sell_times = [t.get('timestamp') for t in sell_signals]
            sell_prices = [t.get('price') for t in sell_signals]
            sell_quantities = [t.get('quantity', 0) for t in sell_signals]
            sell_commissions = [t.get('commission', 0) for t in sell_signals]
            
            # 添加卖出标记点
            fig.add_trace(go.Scatter(
                x=sell_times,
                y=sell_prices,
                mode='markers+text',
                name='🔴 卖出',
                marker=dict(
                    symbol='arrow-down', 
                    size=20, 
                    color='#e74c3c',
                    line=dict(width=3, color='white')
                ),
                text=['💸SELL'] * len(sell_times),
                textposition='top center',
                textfont=dict(size=11, color='#e74c3c', family='Arial Black'),
                hovertemplate='<b>🔴 卖出信号</b><br>' +
                             '<b>时间</b>: %{x}<br>' +
                             '<b>价格</b>: $%{y:.2f}<br>' +
                             '<b>数量</b>: %{customdata[0]:.6f}<br>' +
                             '<b>手续费</b>: $%{customdata[1]:.4f}<br>' +
                             '<extra></extra>',
                customdata=list(zip(sell_quantities, sell_commissions))
            ))
        
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(size=16, family='Arial Black')
            ),
            xaxis_title='⏰ 时间',
            yaxis_title='💰 价格 (USDT)',
            template='plotly_white',
            hovermode='x unified',
            height=650,
            legend=dict(
                orientation="h", 
                yanchor="bottom", 
                y=1.02, 
                xanchor="right", 
                x=1,
                font=dict(size=12)
            ),
            plot_bgcolor='rgba(240, 240, 240, 0.5)',
            xaxis=dict(
                gridcolor='rgba(128, 128, 128, 0.2)',
                showgrid=True
            ),
            yaxis=dict(
                gridcolor='rgba(128, 128, 128, 0.2)',
                showgrid=True
            )
        )
        
        return fig
    
    @staticmethod
    def plot_drawdown(equity_curve: List[float],
                      timestamps: List[datetime] = None,
                      title: str = "回撤曲线") -> go.Figure:
        """
        绘制回撤曲线
        
        Args:
            equity_curve: 权益曲线数据
            timestamps: 时间戳列表
            title: 图表标题
            
        Returns:
            Plotly图表对象
        """
        # 计算回撤（显示为负值，更符合常规）
        peak = equity_curve[0]
        drawdowns = []
        
        for value in equity_curve:
            if value > peak:
                peak = value
            # 回撤 = (当前值 - 峰值) / 峰值 * 100，显示为负值
            dd = (value - peak) / peak * 100
            drawdowns.append(dd)
        
        x_data = timestamps if timestamps else list(range(len(drawdowns)))
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=x_data,
            y=drawdowns,
            mode='lines',
            name='回撤',
            line=dict(color='#d62728', width=2),
            fill='tozeroy',
            fillcolor='rgba(214, 39, 40, 0.2)'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title='时间' if timestamps else '时间点',
            yaxis_title='回撤 (%)',
            template='plotly_white',
            hovermode='x unified',
            height=400
        )
        
        return fig
    
    @staticmethod
    def plot_performance_dashboard(equity_curve: List[float],
                                   timestamps: List[datetime],
                                   metrics: Dict,
                                   title: str = "绩效仪表板") -> go.Figure:
        """
        绘制绩效仪表板
        
        Args:
            equity_curve: 权益曲线
            timestamps: 时间戳
            metrics: 绩效指标字典
            title: 仪表板标题
            
        Returns:
            Plotly图表对象
        """
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('资金曲线', '回撤曲线', '绩效指标', ''),
            specs=[[{"type": "scatter"}, {"type": "scatter"}],
                   [{"type": "table"}, None]]
        )
        
        # 1. 资金曲线
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=equity_curve,
            mode='lines',
            name='权益',
            line=dict(color='#1f77b4', width=2),
            showlegend=False
        ), row=1, col=1)
        
        # 2. 回撤曲线
        peak = equity_curve[0]
        drawdowns = []
        for value in equity_curve:
            if value > peak:
                peak = value
            # 回撤显示为负值
            dd = (value - peak) / peak * 100
            drawdowns.append(dd)
        
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=drawdowns,
            mode='lines',
            name='回撤',
            line=dict(color='#d62728', width=2),
            fill='tozeroy',
            fillcolor='rgba(214, 39, 40, 0.2)',
            showlegend=False
        ), row=1, col=2)
        
        # 3. 绩效指标表格
        metrics_text = [[k, v] for k, v in metrics.items()]
        
        fig.add_trace(go.Table(
            header=dict(values=['指标', '数值'],
                       fill_color='#1f77b4',
                       align='left',
                       font=dict(color='white', size=12)),
            cells=dict(values=list(zip(*metrics_text)),
                      fill_color='lavender',
                      align='left',
                      font=dict(size=11))
        ), row=2, col=1)
        
        fig.update_layout(
            title=title,
            template='plotly_white',
            height=800,
            showlegend=False
        )
        
        fig.update_xaxes(title_text="时间", row=1, col=1)
        fig.update_yaxes(title_text="资金", row=1, col=1)
        fig.update_xaxes(title_text="时间", row=1, col=2)
        fig.update_yaxes(title_text="回撤 (%)", row=1, col=2)
        
        return fig
