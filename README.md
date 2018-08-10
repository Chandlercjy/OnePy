# Onepy 2.2

Onepy is an event-driven algorithmic trading Python library.

知乎专栏：[OnePy-基于 Python 的量化回测框架](https://zhuanlan.zhihu.com/onepy)

更新日志：[Change Log](CHANGE_LOG.md)

## Install

Onepy is developed using Python 3.6.x. You can install by pip and make sure they
are up-to-date

```{python}
pip install pandas
pip install plotly
pip install funcy
pip install arrow
pip install pymongo
pip install retry
pip install dataclasses # 将在python 3.7中成为标准库
pip install OnePy_trader
# pip的OnePy_trader有可能有时不是最新，建议将库克隆到本地使用。
```

## Getting Started

请参考 examples 中的 Tutorial.

```python
import OnePy as op
from OnePy.builtin_module.recorders.stock_recorder import StockRecorder
from OnePy.custom_module.cleaner_sma import SMA


class SmaStrategy(op.StrategyBase):

    def __init__(self):

        super().__init__()
        self.sma1 = SMA(3, 40).calculate
        self.sma2 = SMA(5, 40).calculate

        self.sma3 = SMA(15, 40).calculate
        self.sma4 = SMA(30, 60).calculate

    def handle_bar(self):
        if self.sma1('000001') > self.sma2('000001'):
            self.buy(100, '000001', takeprofit=15,
                     stoploss=100, trailingstop_pct=0.1)
        else:
            self.sell(100, '000001')

        if self.sma3('000001') < self.sma4('000001'):
            self.short_sell(100, '000001', takeprofit=15,
                            stoploss=100, trailingstop_pct=0.1)
        else:
            self.short_cover(100, '000001')


# op.data_readers.CSVReader('./000001.csv', '000001',
            # fromdate='2017-05-25', todate='2018-03-09')

op.data_readers.MongodbReader(
    database='tushare', collection='000001', ticker='000001',
    fromdate='2017-05-25', todate='2018-03-09')

SmaStrategy()

op.RiskManagerBase()
op.StockBroker()

StockRecorder().set_setting(initial_cash=100000,
                            comm=1, comm_pct=None, margin_rate=0.1)
go = op.OnePiece()
# go.show_log(file=False)
go.sunny()
# go.output.show_setting()
# go.output.plot('000001')
print(go.output.trade_log())
```

```
+--------------------------+
| Final_Value  | $99695.40 |
| Total_return | -0.30460% |
| Max_Drawdown | 0.58500%  |
| Duration     |     362.0 |
| Sharpe_Ratio | -0.67837  |
+--------------------------+
```

![Plot](docs/readme_plot.png) ![Log](docs/readme_log.png)

## Main Features

#### OnePy 综合方面:

*   事件驱动回测设计 ✓
*   Stock 模式 ✓
*   多股票回测 ✓
*   多策略回测 ✓
*   设置手续费, 保证金/手, 杠杆大小 ✓
*   设置成交价格为 close 或者第二天 open ✓
*   设置是否打印交易日志 ✓
*   Plot 画图模块 ✓

#### Tools 工具方面:

*   To_MongoDB:自定义数据统一格式后存入数据库 ✓
*   To_MongoDB:tushare 股票数据 CSV 存入数据库 ✓
*   直接 tushare 的 api 数据存入 MongoDB ✓

#### DataHandler 数据方面:

*   CSV 数据读取 ✓
*   MongoDB 数据读取 ✓

#### Strategy 策略方面:

*   做多 Buy & Sell, 做空 Shortsell & Shortcover 指令 ✓
*   按百分比或盈亏多少钱, 设置止盈 Limit、止损 Stop 和 Trailingstop 移动止损 ✓
*   按百分比或者指定价格, 建立挂单。 ✓
*   技术指标 Cleaner 模块 ✓

#### Broker 执行方面:

*   模拟发送指令 ✓
*   模拟检查指令是否发送成功 ✓
*   打印交易日志 ✓
*   手续费 commission, 百分比类型和固定类型 ✓

#### Recorder 日志方面:

*   计算保证金, 仓位, 浮动利润, 已平仓利润, 总资金, 剩余现金, 收益率, 市值, 全部
        时间序列化 ✓
*   输出交易记录, 包括出场时间, 入场时间, 盈亏点数, 盈亏利润等 ✓

#### 延展性方面:

*   在 Environment 中存有原始所有信号信息, 生成的订单信息, 便于分析 ✓
*   自定义扩展事件源 ✓
*   自定义数据源, 返回迭代器给 OnePy 即可 ✓
*   自定义策略模块 ✓
*   自定义技术指标模块 ✓
*   自定义风控模块 ✓
*   自定义经纪商模块 ✓
*   自定义日志记录模块 ✓

## Road Map

![执行过程](docs/OnePy_执行过程.png)

## Contact

I'm very interested in your experience with **Onepy**.Please feel free to
contact me via **chenjiayicjy@gmail.com**

**Chandler_Chan**
