#coding=utf8

import pandas as pd
import itertools
import copy
import Queue

from event import events
from fill import Fill

import os,sys
import matplotlib.pyplot as plt
import matplotlib.style as style

import feed as Feed
import plotter

from tools.print_formater import dict_to_table
from collections import OrderedDict

class OnePiece():
    def __init__(self):
        self.feed_list = []
        self.strategy_list = []

        self.portfolio = None
        self.broker = None

        self.live_mode = False
        self.target = None     # Forex, Futures, Stock
        self.fill = Fill()
        self.hedge_mode = False

    def sunny(self):
        # run_once function
        Feed.run_first(self.feed_list)
        self.fill.run_first(self.feed_list)

        while 1:
            try:
                event = events.get(False)
            except Queue.Empty:
                Feed.load_all_feed(self.feed_list)
                self.fill.update_timeindex(self.feed_list)

                for f in self.feed_list:
                    f._check_onoff = True        # 开启检查挂单
            else:
                if event.type is 'Market':
                    self._pass_to_market(event) # 将fill的数据传送到各模块

                    for s in self.strategy_list:
                        s(event).run_strategy()

                if event.type is 'Signal':
                    self.portfolio(event).run_portfolio()

                if event.type is 'Order':
                    self.broker.run_broker(event)

                if event.type is 'Fill':
                    self.fill.run_fill(event)
                    self._check_limit_stop_above_below(event)

                if self._check_finish_backtest(self.feed_list):
                    self._output_summary()
                    break

################### In Loop #######################
    def _check_limit_stop_above_below(self,fillevent):
        for f in self.feed_list:    # 判断属于哪个feed_list
            if fillevent.instrument is f.instrument and f._check_onoff:
                # 检查之前在fill中有没有挂单成交等
                self.fill.check_trade_list(f)
                self.fill.check_order_list(f)
                f._check_onoff = False       # 每个bar只检查一次挂单


################### before #######################
    def _adddata(self, feed_list):
        [self.feed_list.append(data) for data in feed_list]

    def _set_portfolio(self, portfolio):
        self.portfolio = portfolio

    def _addstrategy(self, strategy_list):
        [self.strategy_list.append(st) for st in strategy_list]

    def _set_broker(self,broker):
        self.broker = broker()

    def _set_target(self,target):
        self.broker.target = target   # 将target传递给broker使用
        for f in self.feed_list:
            f.target = target

    def set_backtest(self, feed_list,strategy_list,
                        portfolio,broker,target='Forex'):

        # check target
        if target not in ['Forex', 'Futures', 'Stock']:
            raise SyntaxError('Target should be one of "Forex","Futures","Stock"')

        if not isinstance(feed_list,list): feed_list = [feed_list]
        if not isinstance(strategy_list,list): strategy_list = [strategy_list]

        # 因为各个模块之间相互引用，所以要按照顺序add和set模块
        self.target = target
        self._adddata(feed_list)
        self._set_portfolio(portfolio)
        self._addstrategy(strategy_list)
        self._set_broker(broker)
        self._set_target(target)

    def set_commission(self,commission,margin,mult,commtype='fixed'):
        if self.live_mode:
            raise SyntaxError("Can't set commission in live_mode")
        self.broker.commission = commission
        self.broker.commtype = commtype
        self.broker.margin = margin
        self.broker.mult = mult

        for st in self.strategy_list:
            st._mult = mult

        self.fill._mult = mult

    def set_pricetype(self,pricetype ='close'):
        for st in self.strategy_list:
            st.pricetype = pricetype
        self.fill.pricetype = pricetype

    def set_cash(self,cash=100000):
        self.fill.initial_cash = cash

    def set_hedge(self,on=True):
        self.hedge_mode = True

    def set_notify(self,onoff=True):
        self.broker._notify_onoff = onoff

################### middle #######################
    def _pass_to_market(self,marketevent):
        """因为Strategy模块用到的是marketevent，所以通过marketevent传进去"""
        m = marketevent
        m.fill = self.fill
        self.portfolio.fill = self.fill
        self.broker.fill = self.fill

    def _check_finish_backtest(self,feed_list):
        # if finish, sum(backtest) = 0 + 0 + 0 = 0 -> False
        backtest = [i.continue_backtest for i in feed_list]
        return not sum(backtest)


################### after #######################
    def _output_summary(self):
        from statistics import create_drawdowns, create_sharpe_ratio
        total = pd.DataFrame(self.fill.total_list)[1:]
        total.set_index('date',inplace=True)
        pct_returns = total.pct_change()
        m,d = create_drawdowns(pct_returns['total'])
        d = OrderedDict()
        d['Final_Value'] = round(self.fill.total_list[-1]['total'],3)
        d['Total_return'] = round(d['Final_Value']/self.fill.initial_cash-1,5)
        d['Total_return'] = str(d['Total_return']*100)+'%'
        d['Max_Drawdown'],d['Duration']=create_drawdowns(pct_returns['total'])
        d['Max_Drawdown'] = str(d['Max_Drawdown'])+'%'
        d['Sharpe_Ratio'] = round(create_sharpe_ratio(pct_returns),3)
        print dict_to_table(d)


    def oldplot(self,name,instrument=None):
        if instrument is None:
            instrument = self.feed_list[0].instrument
        fig = plotter.matplotlib(self.fill)
        fig.plot(name,instrument)


    def plot(self,instrument,engine='plotly',notebook=False):
        data = plotter.plotly(instrument = instrument,
                        feed_list = self.feed_list,
                        fill = self.fill)
        data.plot(instrument=instrument,engine=engine,notebook=notebook)
