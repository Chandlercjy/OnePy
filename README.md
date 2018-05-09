# Onepy 2.1

Onepy is an event-driven algorithmic trading Python library.

知乎专栏：[OnePy-基于 Python 的量化回测框架](https://zhuanlan.zhihu.com/onepy)

更新日志：[Change Log](CHANGE_LOG.md)

1.x 版本请查看[OnePy 1.52](https://github.com/Chandlercjy/OnePy/tree/master)

## Install

Onepy is developed using Python 3.6.x. You can install by pip and make sure they
are up-to-date

```{python}
pip install pandas
pip install plotly
pip install funcy
pip install arrow
pip install pymongo
pip install dataclasses # 将在python 3.7中成为标准库

pip install OnePy_trader
pip install --upgrade OnePy_trader
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

## Road Map

![执行过程](docs/OnePy_执行过程.png)

## Contact

I'm very interested in your experience with **Onepy**.Please feel free to
contact me via **chenjiayicjy@gmail.com**

**Chandler_Chan**
