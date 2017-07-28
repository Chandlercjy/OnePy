Onepy  0.99.1
===========
Onepy is an event-driven algorithmic trading Python library.

知乎专栏：[OnePy-基于Python的量化回测框架](https://zhuanlan.zhihu.com/onepy)

更新日志：[Change Log](https://github.com/Chandlercjy/OnePy/blob/master/change_log.md)

Install
--------

Onepy is developed using **Python 3.x** and depends on:

- [pandas](https://github.com/pandas-dev/pandas)
- [plotly](https://github.com/plotly/plotly.py)
- [ta-lib](https://github.com/mrjbq7/ta-lib)
- [funcy](https://github.com/Suor/funcy)

You can install them by pip and make sure they are **up-to-date**：


```
pip install pandas
pip install TA-Lib
pip install plotly
pip install funcy

pip install OnePy_trader
pip install --upgrade OnePy_trader
```

Getting started
-------------

OnePy安装完成后复制以下代码运行即可，可以迅速了解本框架的主要功能，记得下载好data文件夹中的文件，设置好数据读取路径。
以Forex为例：
```python
import matplotlib.pyplot as plt
import OnePy as op

class MyStrategy(op.StrategyBase):
        # 可用参数：
        #     list格式： self.cash, self.position, self.margin,
        #                self.total, self.unre_profit
    def __init__(self,marketevent):
        super(MyStrategy,self).__init__(marketevent)

    def prenext(self):
        # print(self.unre_profit[-1])
        pass

    def next(self):
        """这里写主要的策略思路"""
        if self.i.SMA(period=30, index=-1) > self.i.SMA(period=50,index=-1):
            if self.unre_profit[-1] <= 0:
                self.Buy(0.1,limit=self.pips(200),           # 设置止盈为200个pips，不可为负
                             stop=self.pct(1),               # 设置止损为成交价的1%，不可为负
                             trailingstop=self.pips(60))     # 设置追踪止损，盈利时触发
        else:
            self.Sell(0.05,price=self.pips(50),      # 设置挂单，默认为第二天open价格加50点，也可为负数
                           limit=self.pips(200),
                           stop=self.pips(200),
                           trailingstop=self.pips(60))

            if self.unre_profit[-2] > self.unre_profit[-1] and self.unre_profit[-2] > 100:
                self.Exitall()                      # 设置浮亏浮盈大于100元且出现下降时清仓


go = op.OnePiece()

Forex = op.Forex_CSVFeed(datapath='data/EUR_USD30m.csv',    # 注意设置好文件存放路径
                         instrument='EUR_USD',
                         fromdate='2016-04-01',
                         todate='2016-05-01')


data_list = [Forex]

portfolio = op.PortfolioBase
strategy = MyStrategy
broker = op.SimulatedBroker


go.set_backtest(data_list,[strategy],portfolio,broker,'Forex')
go.set_commission(commission=30,margin=325,mult=10**5)    # 手续费为点差30pips，每手保证金为325，1pips为1/(10**5)
go.set_cash(10000)                 # 设置初始资金
# go.set_pricetype(‘close’)        # 设置成交价格为close，若不设置，默认为open
go.set_notify()                    # 打印交易日志


go.sunny()                         # 开始启动策略

# print(go.get_tlog())                # 打印交易日志
go.get_analysis('EUR_USD')            # 进行交易分析
go.plot(instrument='EUR_USD',notebook=False)   # 若在Jupyter notebook中运行，可将notebook设置为True
# 简易的画图，将后面想要画的选项后面的 1 删掉即可
# go.oldplot(['un_profit','re_profit','position1','cash1','total','margin1','avg_price1'])
```

结果：
```
+---------------------------+
| Final_Value  | 103503.906 |
| Total_return | 3.504%     |
| Max_Drawdown | 1.516%     |
| Duration     |      190.0 |
| Sharpe_Ratio |   1650.487 |
+---------------------------+

+-----------------------------------------------------------------+
| start                                 | 2012-04-01 22:00:00     |
| end                                   | 2012-05-01 23:30:00     |
| beginning_balance                     |                  100000 |
| ending_balance                        |              103503.906 |
| unrealized_profit                     |                  1330.0 |
| total_net_profit                      |                2173.906 |
| gross_profit                          |                  9542.1 |
| gross_loss                            |               -7368.194 |
| profit_factor                         |                   1.295 |
| return_on_initial_capital             |                   2.174 |
| annual_return_rate                    |                  51.955 |
| trading_period                        | 0 years 1 months 0 days |
| pct_time_in_market                    |                1122.809 |
| total_num_trades                      |                     829 |
| num_winning_trades                    |                     546 |
| num_losing_trades                     |                     281 |
| num_even_trades                       |                       2 |
| pct_profitable_trades                 |                  65.862 |
| avg_profit_per_trade                  |                   2.622 |
| avg_profit_per_winning_trade          |                  17.476 |
| avg_loss_per_losing_trade             |                 -26.221 |
| ratio_avg_profit_win_loss             |                   0.666 |
| largest_profit_winning_trade          |                   550.2 |
| largest_loss_losing_trade             |                  -317.6 |
| num_winning_points                    |                   0.806 |
| num_losing_points                     |                  -0.595 |
| total_net_points                      |                   0.212 |
| avg_points                            |                     0.0 |
| largest_points_winning_trade          |                    0.01 |
| largest_points_losing_trade           |                  -0.028 |
| avg_pct_gain_per_trade                |                    0.02 |
| largest_pct_winning_trade             |                   0.731 |
| largest_pct_losing_trade              |                  -2.069 |
| max_consecutive_winning_trades        |                      47 |
| max_consecutive_losing_trades         |                      19 |
| avg_bars_winning_trades               |                  12.119 |
| avg_bars_losing_trades                |                  18.815 |
| max_closed_out_drawdown               |                  -1.464 |
| max_closed_out_drawdown_start_date    | 2012-04-24 14:00:00     |
| max_closed_out_drawdown_end_date      | 2012-04-24 20:30:00     |
| max_closed_out_drawdown_recovery_date | 2012-04-25 13:00:00     |
| drawdown_recovery                     |                  -0.001 |
| drawdown_annualized_return            |                  -0.028 |
| max_intra_day_drawdown                |                  -1.412 |
| avg_yearly_closed_out_drawdown        |                  -0.942 |
| max_yearly_closed_out_drawdown        |                  -1.464 |
| avg_monthly_closed_out_drawdown       |                  -0.244 |
| max_monthly_closed_out_drawdown       |                  -1.464 |
| avg_weekly_closed_out_drawdown        |                  -0.086 |
| max_weekly_closed_out_drawdown        |                  -1.337 |
| avg_yearly_closed_out_runup           |                   1.517 |
| max_yearly_closed_out_runup           |                   2.147 |
| avg_monthly_closed_out_runup          |                   0.315 |
| max_monthly_closed_out_runup          |                   1.477 |
| avg_weekly_closed_out_runup           |                   0.103 |
| max_weekly_closed_out_runup           |                   1.122 |
| pct_profitable_years                  |                  97.404 |
| best_year                             |                   1.792 |
| worst_year                            |                  -0.376 |
| avg_year                              |                   0.761 |
| annual_std                            |                   0.377 |
| pct_profitable_months                 |                  51.585 |
| best_month                            |                   1.315 |
| worst_month                           |                   -1.27 |
| avg_month                             |                   0.069 |
| monthly_std                           |                   0.315 |
| pct_profitable_weeks                  |                  33.807 |
| best_week                             |                   1.048 |
| worst_week                            |                  -1.337 |
| avg_week                              |                   0.017 |
| weekly_std                            |                   0.197 |
| sharpe_ratio                          |                   0.574 |
| sortino_ratio                         |                   0.625 |
+-----------------------------------------------------------------+
```

![OnePy_plot](https://github.com/Chandlercjy/OnePy/blob/master/docs/OnePy_plot.jpg)


Main Features
-------------
#### OnePy 综合方面：

- 事件驱动回测设计 ✓
- Forex模式 ✓
- Futures模式
- Stock模式 ✓
- 多品种回测(同一模式下) ✓
- 多策略回测 ✓
- 设置手续费，保证金/手，杠杆大小 ✓
- 设置成交价格为close或者第二天open ✓
- 设置是否打印交易日志 ✓
- Plot 画图模块 ✓
- 设置Bar mode或者Tick mode
- Optimizer 参数优化模块


#### Tools 工具方面：

- To_MongoDB：自定义数据统一格式后存入数据库 ✓
- To_MongoDB：tickstory外汇数据CSV存入数据库 ✓
- To_MongoDB：tushare股票数据CSV存入数据库 ✓
- 实时采集数据存入MongoDB


#### Feed 数据方面：

- 自定义CSV数据读取 ✓
- tickstory外汇数据CSV读取 ✓
- Tushare股票数据CSV读取 ✓
- 期货数据CSV读取 ✓
- 从MongoDB数据库读取数据


#### Strategy 策略方面：

- 实现做多Buy，做空Sell指令，一键平仓指令 ✓
- 按百分比pct或基点pips，挂多单(above&below)和挂空单(above&below) ✓
- 按百分比pct或基点pips，止盈止损 ✓
- 按百分比pct或基点pips，移动止损 ✓
- 自定义打印交易信息 ✓
- 技术指标Indicator模块 ✓
- OCO指令
- 挂单到时过期
- 取消挂单指令

#### Portfolio 风控方面：

- 暂无


#### Broker 执行方面：

- 模拟发送指令 ✓
- 模拟检查指令是否发送成功 ✓
- 打印交易日志 notify ✓
- 手续费commission，百分比类型和固定类型 ✓
- oanda接口


#### Fill 日志方面：

- 计算保证金，仓位，总利润，总额，剩余现金，收益率，全部序列化 ✓
- 输出交易记录 ✓


#### Stats 分析方面：

- 交易结果超简单分析 ✓
- 交易记录详细分析 ✓
- 结合Benchmark分析

Alternatives
------------
- [vnpy](https://github.com/vnpy/vnpy)
- [Backtrader](https://github.com/mementum/backtrader/blob/master/README.rst)
- [PyAlgoTrade](https://github.com/gbeced/pyalgotrade)
- [Zipline](https://github.com/quantopian/zipline)
- [Ultra-Finance](https://code.google.com/archive/p/ultra-finance/)
- [ProfitPy](https://code.google.com/archive/p/profitpy/)
- [pybacktest](https://github.com/ematvey/pybacktest)
- [prophet](https://github.com/Emsu/prophet)
- [quant](https://github.com/maihde/quant)
- [AlephNull](https://github.com/CarterBain/AlephNull)
- [Trading with Python](http://www.tradingwithpython.com/)
- [visualize-wealth](https://github.com/benjaminmgross/visualize-wealth)
- [tia: Toolkit for integration and analysis](https://github.com/bpsmith/tia)
- [QuantSoftware Toolkit](http://wiki.quantsoftware.org/index.php?title=QuantSoftware_ToolKit)
- [Pinkfish](http://fja05680.github.io/pinkfish/)
- [bt](https://github.com/pmorissette/bt)
- [PyThalesians](https://github.com/thalesians/pythalesians)
- [QSTrader](https://github.com/mhallsmoore/qstrader/)
- [QSForex](https://github.com/mhallsmoore/qsforex)
- [pysystemtrade](https://github.com/robcarver17/pysystemtrade)
- [QTPyLib](https://github.com/ranaroussi/qtpylib)
- [RQalpha](https://github.com/ricequant/rqalpha)


后记
------
这个回测框架内部还存在很多问题，比如交易结果分析的公式是照搬Pinkfish的，准确性还有待考证，又比如在策略中同时发出做多，做空和一键平仓信号，结果不一定为全部平仓等。这些问题还需要在接下来的应用和思考中才能发现和修改。

所以此框架主要做学习之用，若想直接拿去回测思路还请三思。

另外本人接下来一段时间要回归书本汲取新的知识了，所以OnePy更新暂时告一段落。

如果你有什么想法欢迎随时和我交流。

Wechat：chenjiayicjy，添加请注明OnePy。
感恩。

Contact
-------
I'm very interested in your experience with **Onepy**.Please feel free to contact me via **chenjiayicjy@126.com**

**Chandler_Chan**
