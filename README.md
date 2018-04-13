Onepy 
===========
Onepy is an event-driven algorithmic trading Python library.

知乎专栏：[OnePy-基于Python的量化回测框架](https://zhuanlan.zhihu.com/onepy)

更新日志：[Change Log](https://github.com/Chandlercjy/OnePy/blob/master/change_log.md)

Install
--------

Onepy is developed using **Python 3.x**.
You can install by pip and make sure they are **up-to-date**：

```
pip install pandas
pip install TA-Lib
pip install plotly
pip install funcy
pip install arrow
pip install pymongo

pip install OnePy_trader==1.52.1
```

Getting started
-------------

OnePy安装完成后复制以下代码运行即可，可以迅速了解本框架的主要功能。
记得下载好data文件夹中的文件，设置好数据读取路径。
以Forex为例：

```python
import OnePy as op


class MyStrategy(op.StrategyBase):
    def __init__(self, marketevent):
        super(MyStrategy, self).__init__(marketevent)

    def prenext(self):
        """以下条件均可用于next中进行策略逻辑判断"""
        # print(self.position[-1])
        # print(self.margin[-1])
        # print(self.avg_price[-1])
        # print(self.unrealizedPL[-1])
        # print(self.realizedPL[-1])
        # print(self.commission[-1])
        # print(self.cash[-1])
        # print(self.balance[-1])
        pass

    def next(self):
        """这里写主要的策略思路"""
        if self.i.SMA(period=30, index=-1) > self.i.SMA(period=50, index=-1):
            if self.unrealizedPL[-1] <= 0:
                self.buy(0.1, takeprofit=self.pips(200),  # 设置止盈为200个pips，不可为负
                         stoploss=self.pct(1),  # 设置止损为成交价的1%，不可为负
                         trailingstop=self.pips(60))  # 设置追踪止损，盈利时触发
        else:
            self.sell(0.05, price=self.pips(50),  # 设置挂单，默认为第二天open价格加50点，也可为负数
                      takeprofit=self.pips(200),
                      stoploss=self.pips(200),
                      trailingstop=self.pips(60))

            if self.unrealizedPL[-2] > self.unrealizedPL[-1] and self.unrealizedPL[-2] > 100:
                self.exitall()  # 设置浮亏浮盈大于100元且出现下降时清仓


go = op.OnePiece()

Forex = op.ForexCSVFeed(datapath='../data/EUR_USD30m.csv', instrument='EUR_USD',
                        fromdate='2012-04-01', todate='2012-05-01')

# 注意若要用MongoDB_Backtest_Feed，先运行tests里面的csv_to_MongoDB.py，推荐用MongoDB
# Forex = op.MongoDB_Backtest_Feed(database='EUR_USD', collection='M30', instrument='EUR_USD',
#                                  fromdate='2012-04-01', todate='2012-05-01')

data_list = [Forex]

portfolio = op.Portfolio
strategy = MyStrategy

go.set_backtest(data_list, [strategy], portfolio, 'Forex')
go.set_commission(commission=10, margin=325, mult=100000)
go.set_cash(100000)  # 设置初始资金
# go.set_pricetype(‘close’)        # 设置成交价格为close，若不设置，默认为open
# go.set_notify()  # 打印交易日志

go.sunny()  # 开始启动策略

print(go.get_tlog('EUR_USD'))  # 打印交易日志
go.get_analysis('EUR_USD')
go.plot(instrument='EUR_USD', notebook=False)

```

结果：

```
+------------------------+
| Final_Value  | 92619.2 |
| Total_return | -7.381% |
| Max_Drawdown | 9.261%  |
| Duration     |   989.0 |
| Sharpe_Ratio |  -0.474 |
+------------------------+
+------------------------------------------------------------------+
| start                                 | 2012-04-01 22:00:00      |
| end                                   | 2012-04-30 23:30:00      |
| beginning_balance                     |                   100000 |
| ending_balance                        |                  92619.2 |
| unrealized_profit                     |                -10032.85 |
| total_net_profit                      |                  2652.05 |
| gross_profit                          |                  2774.75 |
| gross_loss                            |                     -7.7 |
| profit_factor                         |                  360.357 |
| return_on_initial_capital             |                    2.652 |
| annual_return_rate                    |                  -61.848 |
| trading_period                        | 0 years 0 months 29 days |
| pct_time_in_market                    |                  469.595 |
| total_num_trades                      |                       69 |
| num_winning_trades                    |                       64 |
| num_losing_trades                     |                        5 |
| num_even_trades                       |                        0 |
| pct_profitable_trades                 |                   92.754 |
| avg_profit_per_trade                  |                   38.436 |
| avg_profit_per_winning_trade          |                   43.355 |
| avg_loss_per_losing_trade             |                    -1.54 |
| ratio_avg_profit_win_loss             |                   28.153 |
| largest_profit_winning_trade          |                     80.5 |
| largest_loss_losing_trade             |                     -2.5 |
| num_winning_points                    |                    0.119 |
| num_losing_points                     |                   -0.326 |
| total_net_points                      |                   -0.207 |
| avg_points                            |                   -0.003 |
| largest_points_winning_trade          |                    0.007 |
| largest_points_losing_trade           |                   -0.016 |
| avg_pct_gain_per_trade                |                   -0.227 |
| largest_pct_winning_trade             |                    0.533 |
| largest_pct_losing_trade              |                   -1.219 |
| max_consecutive_winning_trades        |                       54 |
| max_consecutive_losing_trades         |                        2 |
| avg_bars_winning_trades               |                   70.672 |
| avg_bars_losing_trades                |                     46.8 |
| max_closed_out_drawdown               |                   -9.259 |
| max_closed_out_drawdown_start_date    | 2012-04-02 09:00:00      |
| max_closed_out_drawdown_end_date      | 2012-04-19 13:00:00      |
| max_closed_out_drawdown_recovery_date | Not Recovered Yet        |
| drawdown_recovery                     |                   -0.047 |
| drawdown_annualized_return            |                     0.15 |
| max_intra_day_drawdown                |                   -9.544 |
| avg_yearly_closed_out_drawdown        |                   -4.166 |
| max_yearly_closed_out_drawdown        |                   -6.346 |
| avg_monthly_closed_out_drawdown       |                   -0.814 |
| max_monthly_closed_out_drawdown       |                   -3.743 |
| avg_weekly_closed_out_drawdown        |                   -0.273 |
| max_weekly_closed_out_drawdown        |                   -2.997 |
| avg_yearly_closed_out_runup           |                    2.997 |
| max_yearly_closed_out_runup           |                    5.455 |
| avg_monthly_closed_out_runup          |                    0.673 |
| max_monthly_closed_out_runup          |                    4.458 |
| avg_weekly_closed_out_runup           |                    0.239 |
| max_weekly_closed_out_runup           |                     2.79 |
| pct_profitable_years                  |                   28.816 |
| best_year                             |                    2.843 |
| worst_year                            |                   -6.277 |
| avg_year                              |                   -1.436 |
| annual_std                            |                    2.093 |
| pct_profitable_months                 |                    42.54 |
| best_month                            |                    4.458 |
| worst_month                           |                   -3.727 |
| avg_month                             |                   -0.147 |
| monthly_std                           |                     1.17 |
| pct_profitable_weeks                  |                   40.814 |
| best_week                             |                     2.79 |
| worst_week                            |                   -2.997 |
| avg_week                              |                   -0.037 |
| weekly_std                            |                    0.535 |
| sharpe_ratio                          |                   -0.474 |
| sortino_ratio                         |                   -0.466 |
+------------------------------------------------------------------+
```

![Trade_log](https://github.com/Chandlercjy/OnePy/blob/master/docs/Trade_log.jpg)
![OnePy_plot](https://github.com/Chandlercjy/OnePy/blob/master/docs/OnePy_plot.jpg)


Main Features
-------------
#### OnePy 综合方面：

- 事件驱动回测设计 ✓
- Forex模式 ✓
- Futures模式 ✓
- Stock模式 ✓
- 多品种回测(同一模式下) ✓
- 多策略回测 ✓
- 设置手续费，保证金/手，杠杆大小 ✓
- 设置成交价格为close或者第二天open ✓
- 设置是否打印交易日志 ✓
- Plot 画图模块 ✓
- Optimizer 参数优化模块


#### Tools 工具方面：

- To_MongoDB：自定义数据统一格式后存入数据库 ✓
- To_MongoDB：tickstory外汇数据CSV存入数据库 ✓
- To_MongoDB：tushare股票数据CSV存入数据库 ✓
- 直接tushare的api数据存入MongoDB ✓


#### Feed 数据方面：

- 自定义CSV数据读取 ✓
- tickstory外汇数据CSV读取 ✓
- Tushare股票数据CSV读取 ✓
- 期货数据CSV读取 ✓
- 从MongoDB数据库读取数据 ✓


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
这个回测框架内部还存在很多问题，主要做学习之用，若想直接拿去回测思路还请三思。

如果你有什么想法欢迎随时和我交流。

感恩。

Contact
-------
I'm very interested in your experience with **Onepy**.Please feel free to contact me via **chenjiayicjy@gmail.com**

**Chandler_Chan**
