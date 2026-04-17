"""
Streamlit Web界面
提供可视化的回测结果展示和策略管理
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.binance_client import BinanceClient
from strategies.ma_crossover import MovingAverageCrossover
from strategies.rsi_strategy import RSIStrategy
from strategies.bollinger_bands import BollingerBandsStrategy
from backtest.engine import BacktestEngine
from utils.performance import PerformanceAnalyzer
from visualization.charts import ChartGenerator
from main import get_all_strategies


def load_data(client: BinanceClient, symbol: str, timeframe: str, 
              days: int = 90) -> pd.DataFrame:
    """加载历史数据"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    data = client.get_klines(
        symbol=symbol,
        interval=timeframe,
        start_str=start_date.strftime('%Y-%m-%d'),
        end_str=end_date.strftime('%Y-%m-%d'),
        limit=1000
    )
    
    return data


def run_backtest(strategy, data: pd.DataFrame, initial_capital: float,
                 commission_rate: float, position_size: float):
    """运行回测"""
    engine = BacktestEngine(
        strategy=strategy,
        initial_capital=initial_capital,
        commission_rate=commission_rate,
        position_size=position_size
    )
    
    result = engine.run(data)
    return result


def main():
    st.set_page_config(page_title="币安交易机器人", layout="wide")
    
    st.title("🤖 币安自动交易机器人")
    
    # 侧边栏配置
    st.sidebar.header("配置参数")
    
    # 获取所有可用策略
    all_strategies = get_all_strategies()
    strategy_names = [s.name for s in all_strategies]
    
    # 策略分类
    category_mapping = {
        "经典策略": ["Moving Average", "RSI Strategy", "Bollinger Bands", "MACD", "KD "],
        "价格动量": ["ADX", "PSAR", "Ichimoku", "Supertrend", "Hull", "Vortex", "Aroon", "Trix", "Momentum"],
        "价格反转": ["Williams", "Stochastic", "CCI", "CMO", "ROC", "Fisher", "Awesome", "Fractal", "ZigZag"],
        "成交量": ["Volume", "OBV", "MFI", "PVO", "Force Index", "Money Flow"],
        "价量结合": ["Chaikin Money Flow", "Accumulation Distribution", "Ease of Movement", "Qstick"],
        "市场指标": ["Arms", "McClellan", "Triple Screen"],
        "其他": []  # 剩余的策略
    }
    
    # 选择策略分类
    selected_category = st.sidebar.selectbox(
        "策略分类", 
        list(category_mapping.keys()),
        index=0
    )
    
    # 根据分类过滤策略
    if selected_category == "其他":
        # 显示所有未分类的策略
        filtered_strategies = []
        categorized_names = []
        for names in category_mapping.values():
            categorized_names.extend(names)
        
        for i, name in enumerate(strategy_names):
            if not any(cat_name in name for cat_name in categorized_names):
                filtered_strategies.append((i, name))
    else:
        # 显示指定分类的策略
        keywords = category_mapping[selected_category]
        filtered_strategies = [
            (i, name) for i, name in enumerate(strategy_names)
            if any(keyword in name for keyword in keywords)
        ]
    
    # 如果没有找到策略，显示所有策略
    if not filtered_strategies:
        filtered_strategies = list(enumerate(strategy_names))
    
    # 选择具体策略
    strategy_options = {name: idx for idx, name in filtered_strategies}
    selected_strategy_name = st.sidebar.selectbox(
        "选择策略", 
        list(strategy_options.keys()),
        index=0
    )
    selected_strategy_idx = strategy_options[selected_strategy_name]
    strategy = all_strategies[selected_strategy_idx]
    
    # 交易参数
    # 获取所有可用交易对
    @st.cache_data(ttl=3600)  # 缓存1小时
    def get_available_symbols():
        try:
            client = BinanceClient(testnet=True)
            return client.get_all_symbols('USDT')
        except Exception as e:
            st.error(f"获取交易对列表失败: {e}")
            return ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']  # 默认返回几个常用交易对
    
    available_symbols = get_available_symbols()
    
    # 显示可用交易对数量
    st.sidebar.info(f"📊 可用交易对: {len(available_symbols)} 个")
    
    # 添加搜索框
    symbol_search = st.sidebar.text_input("🔍 搜索交易对", placeholder="输入 BTC, ETH 等关键词")
    
    # 根据搜索结果过滤
    if symbol_search:
        filtered_symbols = [s for s in available_symbols if symbol_search.upper() in s]
        if not filtered_symbols:
            st.sidebar.warning(f"未找到包含 '{symbol_search}' 的交易对")
            filtered_symbols = available_symbols
    else:
        filtered_symbols = available_symbols
    
    symbol = st.sidebar.selectbox(
        "交易对", 
        filtered_symbols,
        index=filtered_symbols.index('BTCUSDT') if 'BTCUSDT' in filtered_symbols else 0
    )
    timeframe = st.sidebar.selectbox("时间周期", ["1m", "5m", "15m", "1h", "4h", "1d"], index=3)
    days = st.sidebar.slider("回测天数", 30, 365, 90)
    
    # 资金参数
    initial_capital = st.sidebar.number_input("初始资金 (USDT)", min_value=100.0, value=10000.0, step=100.0)
    position_size = st.sidebar.slider("仓位比例", 0.01, 1.0, 0.1, 0.01)
    commission_rate = st.sidebar.number_input("手续费率", 0.0, 0.01, 0.001, 0.0001)
    
    # 显示当前策略信息
    st.sidebar.subheader("当前策略")
    st.sidebar.info(f"**{strategy.name}**")
    st.sidebar.caption("使用默认参数，如需自定义请修改策略代码")
    
    # 主界面
    tab1, tab2, tab3, tab4 = st.tabs(["📊 回测结果", "📈 图表分析", "🚀 批量回测", "💹 实时行情"])
    
    with tab1:
        st.header("回测结果")
        
        if st.button("开始回测", type="primary"):
            with st.spinner("正在加载数据..."):
                try:
                    client = BinanceClient(testnet=True)
                    data = load_data(client, symbol, timeframe, days)
                    
                    if data.empty:
                        st.error("未能获取数据，请检查网络连接或API配置")
                        return
                    
                    st.success(f"成功加载 {len(data)} 条K线数据")
                    
                    # 运行回测
                    with st.spinner("正在运行回测..."):
                        result = run_backtest(
                            strategy, data, initial_capital, 
                            commission_rate, position_size
                        )
                    
                    # 显示绩效指标
                    st.subheader("绩效指标")
                    metrics = result.summary()
                    
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("总收益率", metrics['总收益率'])
                    col2.metric("最大回撤", metrics['最大回撤'])
                    col3.metric("夏普比率", metrics['夏普比率'])
                    col4.metric("胜率", metrics['胜率'])
                    
                    col5, col6, col7, col8 = st.columns(4)
                    col5.metric("初始资金", f"${metrics['初始资金']}")
                    col6.metric("最终资金", f"${metrics['最终资金']}")
                    col7.metric("交易次数", metrics['总交易次数'])
                    col8.metric("盈利因子", f"{result.winning_trades}/{result.losing_trades}")
                    
                    # 保存结果到session state
                    st.session_state['backtest_result'] = result
                    st.session_state['data'] = data
                    
                except Exception as e:
                    st.error(f"回测失败: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
        
        # 如果有回测结果，显示详细信息
        if 'backtest_result' in st.session_state:
            result = st.session_state['backtest_result']
            data = st.session_state['data']
            
            # 交易记录
            st.subheader("交易记录")
            if result.trades:
                trades_df = pd.DataFrame([{
                    '时间': t.timestamp,
                    '信号': t.signal,
                    '价格': f"{t.price:.2f}",
                    '数量': f"{t.quantity:.6f}",
                    '手续费': f"{t.commission:.4f}"
                } for t in result.trades])
                
                st.dataframe(trades_df, use_container_width=True)
            else:
                st.info("没有产生任何交易")
    
    with tab2:
        st.header("图表分析")
        
        if 'backtest_result' in st.session_state:
            result = st.session_state['backtest_result']
            data = st.session_state['data']
            
            # K线蜡烛图
            st.subheader("🕯️ K线蜡烛图与交易信号")
            trades_for_chart = [{
                'timestamp': t.timestamp,
                'signal': t.signal,
                'price': t.price,
                'quantity': t.quantity,
                'commission': t.commission
            } for t in result.trades]
            
            candlestick_fig = ChartGenerator.plot_candlestick_with_trades(
                data, trades_for_chart,
                f"K线图 - {strategy.name}"
            )
            st.plotly_chart(candlestick_fig, use_container_width=True)
            
            # 资金曲线
            st.subheader("💹 资金曲线")
            equity_fig = ChartGenerator.plot_equity_curve(
                result.equity_curve,
                result.timestamps,
                f"资金曲线 - {strategy.name}"
            )
            st.plotly_chart(equity_fig, use_container_width=True)
            
            # 回撤曲线
            st.subheader("回撤分析")
            dd_fig = ChartGenerator.plot_drawdown(
                result.equity_curve,
                result.timestamps
            )
            st.plotly_chart(dd_fig, use_container_width=True)
            
            # 交易信号图
            st.subheader("交易信号")
            trades_for_chart = [{
                'timestamp': t.timestamp,
                'signal': t.signal,
                'price': t.price
            } for t in result.trades]
            
            trade_fig = ChartGenerator.plot_trades_with_price(
                data, trades_for_chart,
                f"交易信号 - {strategy.name}"
            )
            st.plotly_chart(trade_fig, use_container_width=True)
            
            # 绩效仪表板
            st.subheader("绩效仪表板")
            analyzer = PerformanceAnalyzer(result.equity_curve, result.timestamps)
            all_metrics = analyzer.get_all_metrics(trades_for_chart)
            
            dashboard_fig = ChartGenerator.plot_performance_dashboard(
                result.equity_curve,
                result.timestamps,
                all_metrics
            )
            st.plotly_chart(dashboard_fig, use_container_width=True)
        
        else:
            st.info("请先在「回测结果」标签页运行回测")
    
    with tab3:
        st.header("🚀 批量回测")
        st.markdown("按类别批量测试所有策略，快速对比绩效")
        
        # 批量回测配置
        col1, col2 = st.columns(2)
        with col1:
            batch_days = st.slider("回测天数", 30, 365, 90, key="batch_days")
        with col2:
            batch_capital = st.number_input("初始资金", min_value=100.0, value=10000.0, step=100.0, key="batch_capital")
        
        if st.button("开始批量回测", type="primary", key="batch_backtest"):
            with st.spinner(f"正在加载数据（{batch_days}天）..."):
                try:
                    client = BinanceClient(testnet=True)
                    data = load_data(client, symbol, timeframe, batch_days)
                    
                    if data.empty:
                        st.error("未能获取数据")
                        return
                    
                    st.success(f"✓ 成功加载 {len(data)} 条K线数据")
                    
                    # 获取所有策略
                    all_strategies = get_all_strategies()
                    
                    # 根据当前选择的分类过滤策略
                    if selected_category == "其他":
                        categorized_names = []
                        for names in category_mapping.values():
                            categorized_names.extend(names)
                        filtered_indices = [
                            i for i, name in enumerate(strategy_names)
                            if not any(cat_name in name for cat_name in categorized_names)
                        ]
                    else:
                        keywords = category_mapping[selected_category]
                        filtered_indices = [
                            i for i, name in enumerate(strategy_names)
                            if any(keyword in name for keyword in keywords)
                        ]
                    
                    if not filtered_indices:
                        st.warning("该分类下没有策略")
                        return
                    
                    # 批量回测
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    results = []
                    total = len(filtered_indices)
                    
                    for idx, strategy_idx in enumerate(filtered_indices):
                        strategy = all_strategies[strategy_idx]
                        status_text.text(f"正在测试: {strategy.name} ({idx+1}/{total})")
                        
                        try:
                            engine = BacktestEngine(
                                strategy=strategy,
                                initial_capital=batch_capital,
                                commission_rate=commission_rate,
                                position_size=position_size
                            )
                            result = engine.run(data)
                            
                            # 计算收益率
                            total_return = (result.final_capital / result.initial_capital - 1) * 100
                            
                            results.append({
                                '策略名称': strategy.name,
                                '初始资金': result.initial_capital,
                                '最终资金': result.final_capital,
                                '总收益率(%)': round(total_return, 2),
                                '交易次数': result.total_trades,
                                '最大回撤(%)': round(result.max_drawdown * 100, 2),
                                '夏普比率': round(result.sharpe_ratio, 2),
                                '胜率(%)': round(result.win_rate * 100, 2) if hasattr(result, 'win_rate') else 0
                            })
                        except Exception as e:
                            results.append({
                                '策略名称': strategy.name,
                                '初始资金': batch_capital,
                                '最终资金': 0,
                                '总收益率(%)': 0,
                                '交易次数': 0,
                                '最大回撤(%)': 0,
                                '夏普比率': 0,
                                '胜率(%)': 0,
                                '错误': str(e)
                            })
                        
                        progress_bar.progress((idx + 1) / total)
                    
                    status_text.text("✅ 批量回测完成！")
                    
                    # 保存结果
                    st.session_state['batch_results'] = pd.DataFrame(results)
                    st.session_state['batch_data'] = data
                    
                except Exception as e:
                    st.error(f"批量回测失败: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
        
        # 显示批量回测结果
        if 'batch_results' in st.session_state:
            batch_df = st.session_state['batch_results']
            
            st.subheader("📊 策略对比表格")
            
            # 按收益率排序
            sorted_df = batch_df.sort_values('总收益率(%)', ascending=False).reset_index(drop=True)
            
            # 高亮显示前3名
            def highlight_top3(row):
                if row.name < 3 and row['总收益率(%)'] > 0:
                    return ['background-color: #90EE90'] * len(row)
                elif row['总收益率(%)'] < 0:
                    return ['background-color: #FFB6C6'] * len(row)
                else:
                    return [''] * len(row)
            
            styled_df = sorted_df.style.apply(highlight_top3, axis=1)
            st.dataframe(styled_df, use_container_width=True)
            
            # 统计信息
            st.subheader("📈 统计分析")
            col1, col2, col3, col4 = st.columns(4)
            
            profitable = len(batch_df[batch_df['总收益率(%)'] > 0])
            unprofitable = len(batch_df[batch_df['总收益率(%)'] <= 0])
            avg_return = batch_df['总收益率(%)'].mean()
            best_strategy = batch_df.loc[batch_df['总收益率(%)'].idxmax()]
            
            col1.metric("盈利策略数", f"{profitable}/{len(batch_df)}")
            col2.metric("亏损策略数", unprofitable)
            col3.metric("平均收益率", f"{avg_return:.2f}%")
            col4.metric("最佳策略", f"{best_strategy['策略名称']}\n{best_strategy['总收益率(%)']:.2f}%")
            
            # 可视化对比
            st.subheader("📉 收益率对比图")
            top_n = st.slider("显示前N个策略", 5, 50, 20)
            top_strategies = sorted_df.head(top_n)
            
            fig = go.Figure()
            colors = ['#2ecc71' if r > 0 else '#e74c3c' for r in top_strategies['总收益率(%)']]
            
            fig.add_trace(go.Bar(
                x=top_strategies['策略名称'],
                y=top_strategies['总收益率(%)'],
                marker_color=colors,
                text=top_strategies['总收益率(%)'].apply(lambda x: f'{x:.2f}%'),
                textposition='auto'
            ))
            
            fig.update_layout(
                title=f"前{top_n}个策略收益率对比",
                xaxis_title="策略名称",
                yaxis_title="收益率 (%)",
                template='plotly_white',
                height=500,
                xaxis_tickangle=-45
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 交易次数 vs 收益率散点图
            st.subheader("🔍 交易频率与收益关系")
            scatter_fig = go.Figure()
            
            scatter_fig.add_trace(go.Scatter(
                x=batch_df['交易次数'],
                y=batch_df['总收益率(%)'],
                mode='markers',
                marker=dict(
                    size=10,
                    color=[('#2ecc71' if r > 0 else '#e74c3c') for r in batch_df['总收益率(%)']],
                    opacity=0.7
                ),
                text=batch_df['策略名称'],
                hovertemplate='<b>%{text}</b><br>交易次数: %{x}<br>收益率: %{y:.2f}%<extra></extra>'
            ))
            
            scatter_fig.update_layout(
                title="交易次数 vs 收益率",
                xaxis_title="交易次数",
                yaxis_title="收益率 (%)",
                template='plotly_white',
                height=500
            )
            
            st.plotly_chart(scatter_fig, use_container_width=True)
    
    with tab4:
        st.header("实时行情")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            refresh = st.checkbox("自动刷新", value=False)
        
        with col2:
            if st.button("刷新"):
                st.rerun()
        
        try:
            client = BinanceClient(testnet=True)
            
            # 获取当前价格
            current_price = client.get_ticker_price(symbol)
            st.metric(f"{symbol} 当前价格", f"${current_price:.2f}")
            
            # 获取账户余额
            st.subheader("账户余额")
            balances = client.get_account_balance()
            
            if balances:
                balance_df = pd.DataFrame([{
                    '资产': asset,
                    '可用': f"{info['free']:.6f}",
                    '冻结': f"{info['locked']:.6f}",
                    '总计': f"{info['total']:.6f}"
                } for asset, info in balances.items()])
                
                st.dataframe(balance_df, use_container_width=True)
            else:
                st.info("无余额信息（测试网）")
            
            # 最新K线
            st.subheader("最新K线")
            recent_data = client.get_klines(symbol, timeframe, limit=10)
            
            if not recent_data.empty:
                kline_df = recent_data[['open_time', 'open', 'high', 'low', 'close', 'volume']].copy()
                kline_df['open_time'] = kline_df['open_time'].dt.strftime('%Y-%m-%d %H:%M')
                kline_df.columns = ['时间', '开盘', '最高', '最低', '收盘', '成交量']
                
                st.dataframe(kline_df, use_container_width=True)
        
        except Exception as e:
            st.error(f"获取实时数据失败: {str(e)}")


if __name__ == "__main__":
    main()
