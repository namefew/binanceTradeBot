# 币安自动交易机器人 🤖

一个功能完整的加密货币自动交易系统,支持策略回测、实时交易和可视化分析。

## ✨ 主要功能

- **多策略支持**: 内置双均线、RSI、布林带等经典策略,支持自定义扩展
- **历史回测**: 在历史数据上测试策略表现
- **实时交易**: 自动化执行交易信号
- **绩效分析**: 计算收益率、最大回撤、夏普比率等关键指标
- **可视化界面**: Web界面展示资金曲线、交易历史和绩效仪表板
- **风险管理**: 支持仓位控制和止损止盈设置

## 📋 系统要求

- Python 3.8+
- 币安API账号 (测试网或实盘)

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

复制环境变量模板并填入你的币安API信息:

```bash
cp .env.example .env
```

编辑 `.env` 文件:

```env
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
BINANCE_TESTNET=true  # 测试网设为true,实盘设为false
```

> ⚠️ **重要提示**: 
> - 首次使用请务必在测试网上测试
> - 不要将 `.env` 文件提交到版本控制系统
> - 妥善保管你的API密钥

### 3. 运行Web界面 (推荐)

```bash
streamlit run app.py
```

浏览器会自动打开 http://localhost:8501

**功能:**
- 📊 回测结果: 选择策略、配置参数、查看绩效指标
- 📈 图表分析: 资金曲线、回撤分析、交易信号图
- 💹 实时行情: 查看当前价格和账户余额

### 4. 命令行回测

```bash
python backtest_cli.py
```

按照提示选择策略和参数,回测完成后会显示详细的绩效报告。

### 5. 实时交易

```bash
python trade_live.py
```

⚠️ **警告**: 这会使用真实资金交易!建议先在测试网充分测试。

## 📊 内置策略

### 1. 双均线交叉策略 (Moving Average Crossover)
- **原理**: 短期均线上穿长期均线时买入,下穿时卖出
- **参数**: 短期均线周期、长期均线周期
- **适用**: 趋势行情

### 2. RSI超买超卖策略
- **原理**: RSI低于超卖线买入,高于超买线卖出
- **参数**: RSI周期、超卖线、超买线
- **适用**: 震荡行情

### 3. 布林带策略 (Bollinger Bands)
- **原理**: 价格触及下轨买入,触及上轨卖出
- **参数**: 周期、标准差倍数
- **适用**: 震荡行情

## 🔧 自定义策略

创建新策略只需继承 `Strategy` 基类:

```python
from strategies.base_strategy import Strategy, Signal

class MyCustomStrategy(Strategy):
    def __init__(self):
        super().__init__(name="MyStrategy")
    
    def generate_signal(self, data, current_index):
        # 你的策略逻辑
        if your_buy_condition:
            return Signal.BUY
        elif your_sell_condition:
            return Signal.SELL
        return Signal.HOLD
```

## 📈 绩效指标说明

- **总收益率**: 整个回测期间的总收益百分比
- **年化收益率**: 换算成年化的收益率
- **最大回撤**: 从最高点到最低点的最大跌幅
- **夏普比率**: 风险调整后收益,越高越好 (>1为良好)
- **索提诺比率**: 只考虑下行风险的夏普比率
- **卡玛比率**: 年化收益/最大回撤
- **胜率**: 盈利交易占总交易的比例
- **盈利因子**: 总盈利/总亏损

## 📁 项目结构

```
binanceTradeBot/
├── api/                    # API客户端
│   └── binance_client.py   # 币安API封装
├── strategies/             # 交易策略
│   ├── base_strategy.py    # 策略基类
│   ├── ma_crossover.py     # 双均线策略
│   ├── rsi_strategy.py     # RSI策略
│   └── bollinger_bands.py  # 布林带策略
├── backtest/               # 回测引擎
│   └── engine.py           # 回测核心逻辑
├── trading/                # 实时交易
│   └── engine.py           # 交易引擎
├── utils/                  # 工具函数
│   └── performance.py      # 绩效分析
├── visualization/          # 可视化
│   └── charts.py           # 图表生成
├── app.py                  # Streamlit Web界面
├── backtest_cli.py         # 命令行回测
├── trade_live.py           # 实时交易启动
└── requirements.txt        # 依赖包
```

## ⚙️ 配置说明

### 环境变量 (.env)

```env
# 币安API配置
BINANCE_API_KEY=your_api_key
BINANCE_API_SECRET=your_secret
BINANCE_TESTNET=true

# 数据库配置
DATABASE_URL=sqlite:///trading.db

# 默认交易参数
DEFAULT_SYMBOL=BTCUSDT
DEFAULT_TIMEFRAME=1h
INITIAL_CAPITAL=10000

# 风控参数
MAX_POSITION_SIZE=0.1
STOP_LOSS_PERCENT=0.02
TAKE_PROFIT_PERCENT=0.05
MAX_DRAWDOWN_LIMIT=0.15
```

## 🛡️ 风险提示

1. **市场风险**: 加密货币市场波动极大,可能导致重大损失
2. **技术风险**: 网络延迟、API故障等技术问题可能影响交易
3. **策略风险**: 过往表现不代表未来收益,策略可能失效
4. **资金管理**: 只用你能承受损失的资金进行交易

**建议:**
- ✅ 先在测试网充分测试
- ✅ 从小资金开始实盘
- ✅ 设置合理的止损
- ✅ 定期监控和调整策略
- ❌ 不要投入全部资金
- ❌ 不要盲目相信任何策略

## 📝 开发指南

### 添加新策略

1. 在 `strategies/` 目录创建新文件
2. 继承 `Strategy` 基类
3. 实现 `generate_signal()` 方法
4. 在 `app.py` 和脚本中添加选项

### 修改回测参数

编辑 `backtest_cli.py` 中的配置变量:
- `INITIAL_CAPITAL`: 初始资金
- `COMMISSION_RATE`: 手续费率
- `POSITION_SIZE`: 仓位比例

## 🤝 贡献

欢迎提交Issue和Pull Request!

## 📄 许可证

MIT License

## 📞 支持

如有问题请提交Issue。

---

**免责声明**: 本项目仅供学习和研究使用,不构成投资建议。使用本软件进行交易的风险由用户自行承担。
