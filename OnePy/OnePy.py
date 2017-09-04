import queue
from collections import OrderedDict

import pandas as pd

from OnePy import plotter
from OnePy.analysis.statistics import (stats, create_trade_log,
                                       create_drawdowns,
                                       create_sharpe_ratio)
from OnePy.broker.backtestbroker import BacktestBroker
from OnePy.event import events
from OnePy.fill import BacktestFill
from OnePy.utils.print_formater import dict_to_table


class OnePiece(object):
    def __init__(self):
        self.feed_list = []
        self.strategy_list = []
        self.portfolio = None
        self.broker = None
        self.fill = None

        self.hedge_mode = False
        self.live_mode = False

    def sunny(self):
        """主循环，OnePy的核心"""
        run_first(self.feed_list, self.fill)

        while 1:
            try:
                event = events.get(False)
            except queue.Empty:
                load_all_feed(self.feed_list)
                if not self.__check_finish_backtest():  # 防止重复更新
                    self.__update_timeindex()
                    self.__check_pending_order()

            else:
                if event.type == "Market":
                    self.__pass_to_market(event)  # 将fill的数据传送到各模块

                    for strategy in self.strategy_list:
                        strategy(event).run_strategy()

                elif event.type == "Signal":
                    self.portfolio.run_portfolio(event)

                elif event.type == "Order":
                    self.broker.run_broker(event)

                elif event.type == "Fill":
                    self.fill.run_fill(event)

                if self.__check_finish_backtest():
                    self.__output_summary()
                    break

    def __update_timeindex(self):
        """每次新行情之后，根据新行情更新仓位、现金、保证金等账户基本信息"""
        self.fill.update_timeindex(self.feed_list)
        date_dict = {}
        if len(self.feed_list) > 1:  # 检查若多个feed的话，日期是否相同：
            for i, f in enumerate(self.feed_list):
                date_dict[str(i)] = f.cur_bar.cur_date
            if len(set(list(date_dict.values())).difference()) > 1:
                raise SyntaxError("The date of feed is not identical!")
            else:
                pass

    def __check_pending_order(self):
        """检查挂单、止盈止损、移动止损是否成交"""
        for feed in self.feed_list:  # 判断属于哪个feed_list
            self.fill.check_trade_list(feed)
            self.fill.check_order_list(feed)

    def __pass_to_market(self, marketevent):
        """传递账户基本信息给各模块提供使用"""
        marketevent.fill = self.fill
        self.portfolio.fill = self.fill
        self.broker.fill = self.fill

    def __check_finish_backtest(self):
        """检查回测是否结束"""
        backtest = [i.continue_backtest for i in self.feed_list]  # if finish, sum(backtest) = 0 + 0 + 0 = 0 -> False
        return not sum(backtest)

    def __adddata(self, feed_list):  # Before
        """添加行情到行情列表"""
        for data in feed_list:
            self.feed_list.append(data)

    def __addstrategy(self, strategy_list):
        """添加策略到列表"""
        for strategy in strategy_list:
            self.strategy_list.append(strategy)

    def __set_portfolio(self, portfolio):
        """添加风控模块"""
        self.portfolio = portfolio()

    def __set_broker(self, broker):
        """添加broker模块"""
        self.broker = broker()

    def __set_fill(self, fill):
        """添加交易计算模块"""
        self.fill = fill()

    def __set_target(self, target):
        """设置交易品种的种类"""
        for feed in self.feed_list:
            feed.target = target

    def set_backtest(self, feed_list, strategy_list, portfolio, target="Forex"):
        """设置回测,feed_list和strategy_list可为单个"""
        # check target
        if target not in ["Forex", "Futures", "Stock"]:
            raise SyntaxError("Target should be one of 'Forex','Futures','Stock'")

        if not isinstance(feed_list, list):
            feed_list = [feed_list]
        if not isinstance(strategy_list, list):
            strategy_list = [strategy_list]

        # 因为各个模块之间相互引用，所以要按照一思浓分顺序add和set模块
        self.__adddata(feed_list)
        self.__addstrategy(strategy_list)
        self.__set_portfolio(portfolio)
        self.__set_broker(BacktestBroker)
        self.__set_fill(BacktestFill)
        self.__set_target(target)
        self.set_executemode("open")
        self.set_trailingstopprice("open")
        self.set_buffer(10)

    def set_buffer(self, buffer_days=10):
        """设置buffer天数，用于计算indicator提前preload"""
        for feed in self.feed_list:
            feed.set_buffer_days(buffer_days)

    def set_commission(self, commission, margin, mult, commtype="FIX", instrument=None):
        """
        Forex: commission 表示点差，如commission = 2，表示点差为2
               commtype 默认为固定FIX，不可修改
               margin 表示每手需要多少保证金，如某平台，400倍杠杆每手EUR/USD需要325美金
               mult 处理pips，比如EUR/USD 为1.1659，每pips为0.0001，则 mult=10**5，
                    因为 10**5*0.0001 = 10美金，表示每盈利一个pips，每手赚10美金

        Futures： commission 手续费，可为 ‘FIX’ 或者 ’PCT‘
                  commtype 分为 ‘FIX’ 或者 "PCT",即固定或者按百分比收
                           比如‘FIX’情况下，commission = 12表示每手卖出或者买入，收12元
                              "PCT"情况下，commission = 0.01 表示每手收取 1%
                  margin 表示保证金比率，比如为0.08，表示保证金率为8%
                  mult 表示每个合约的吨数，用于盈亏计算

        Stock： commission 手续费
                comtype 默认为百分比 ‘PCT’，不可修改。
                        比如 commission = 0.01 表示收取购买总市值的 1%
                margin 无
                mult 无
        """

        def check_commtype(feed):
            if feed.target == "Forex":
                feed.set_commtype("FIX")
            elif feed.target == "Stock":
                feed.set_commtype("PCT")

        for feed in self.feed_list:
            if feed.instrument is instrument or len(self.feed_list) == 1:
                feed.set_per_comm(commission)
                feed.set_commtype(commtype)
                feed.set_per_margin(margin)
                feed.set_mult(mult)
                check_commtype(feed)

    def set_executemode(self, executemode="open"):
        """ "open" or "close"， 设置成交价为当天收盘价close还是第二天开盘价open"""
        for feed in self.feed_list:
            feed.set_executemode(executemode)

    def set_trailingstopprice(self, trailingstopprice="open"):
        """ "open" or "close"， 设置以当天收盘价close还是第二天开盘价open计算移动止损"""
        for feed in self.feed_list:
            feed.set_trailingstop_executemode(trailingstopprice)

    def set_cash(self, cash=100000):
        """设置初始资金"""
        self.fill.set_cash(cash)

    def set_notify(self):
        """设置交易提醒"""
        self.broker.set_noify()

    def __output_summary(self):  # After
        """在最后输出简要回测结果"""
        total = pd.DataFrame(self.fill.balance.dict())
        total.set_index("date", inplace=True)
        pct_returns = total.pct_change()
        total = total / self.fill.initial_cash
        max_drawdown, duration = create_drawdowns(total["balance"])
        d = OrderedDict()
        d["Final_Value"] = round(self.fill.balance[-1], 3)
        d["Total_return"] = round(d["Final_Value"] / self.fill.initial_cash - 1, 5)
        d["Total_return"] = str(d["Total_return"] * 100) + "%"
        d["Max_Drawdown"], d["Duration"] = max_drawdown, duration
        d["Max_Drawdown"] = str(d["Max_Drawdown"] * 100) + "%"
        d["Sharpe_Ratio"] = round(create_sharpe_ratio(pct_returns), 3)
        print(dict_to_table(d))

    def get_tlog(self, instrument):
        """获取交易记录，返回DataFrame"""
        completed_list = self.fill.completed_list
        for feed in self.feed_list:
            if feed.instrument is instrument:
                return create_trade_log(completed_list, feed.target, feed.commtype, feed.mult)

    def get_analysis(self, instrument):
        """输出详细交易结果分析"""
        # pd.set_option("display.max_rows", len(x))
        ohlc_data = pd.DataFrame(self.feed_list[0].bar_dict[instrument])
        ohlc_data.set_index("date", inplace=True)
        ohlc_data.index = pd.DatetimeIndex(ohlc_data.index)

        dbal = self.fill.balance.df()

        start = dbal.index[0]
        end = dbal.index[-1]
        capital = self.fill.initial_cash
        tlog = self.get_tlog(instrument)
        tlog = tlog[tlog["units"] != 0]
        tlog.reset_index(drop=True, inplace=True)
        analysis = stats(ohlc_data, tlog, dbal, start, end, capital)
        print(dict_to_table(analysis))

    def plot(self, instrument, engine="plotly", notebook=False):
        """画图"""
        data = plotter.plotly(instrument=instrument,
                              feed_list=self.feed_list,
                              fill=self.fill)
        data.plot(instrument=instrument, engine=engine, notebook=notebook)


def run_first(feed_list, fill):
    """对所有 feed 和 fill 内各项数据进行初始化"""
    for feed in feed_list:
        feed.run_once()
        instrument = feed.instrument
        fill.position.initialize(instrument, 0)
        fill.margin.initialize(instrument, 0)
        fill.avg_price.initialize(instrument, 0)
        fill.unrealizedPL.initialize(instrument, 0)
        fill.realizedPL.initialize(instrument, 0)
        fill.commission.initialize(instrument, 0)
    fill.cash.initialize("all", fill.initial_cash)
    fill.balance.initialize("all", fill.initial_cash)


def load_all_feed(feed_list):
    """读取新行情"""
    for feed in feed_list:
        feed.start()
        feed.prenext()
        feed.next()
