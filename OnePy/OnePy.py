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

        while True:
            try:
                event = events.get(False)
            except Queue.Empty:
                Feed.load_all_feed(self.feed_list)


                for f in self.feed_list:
                    f._check_onoff = True        # 开启检查挂单
            else:
                if event is not None:
                    if event.type == 'Market':
                        self._pass_fill(event) # 将fill的数据传送到各模块

                        for s in self.strategy_list:
                            s(event).run_strategy()

                    if event.type == 'Signal':
                        self.portfolio(event).run_portfolio()

                    if event.type == 'Order':
                        self.broker.run_broker(event)

                    if event.type == 'Fill':
                        self.fill.run_fill(event)

                        for f in self.feed_list:    # 判断属于哪个feed_list
                            if event.instrument == f.instrument \
                            and f._check_onoff:
                                """检查之前在fill中有没有挂单成交等"""
                                self.fill.check_trade_list(f)
                                self.fill.check_order_list(f)
                                f._check_onoff = False       # 每个bar只检查一次挂单

                    if event.type == 'Pend':
                        pass

                if Feed.check_finish_backtest(self.feed_list):
                    print 'Final Portfolio Value: ' + str(self.fill.total_list[-1]['total'])
                    break

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

    def set_backtest(self, feed_list,strategy_list,portfolio,broker,target='Forex'):
        '''因为各个模块之间相互引用，所以要按照顺序add和set模块'''

        # check target
        if target != 'Forex' and target != 'Futures' and target != 'Stock':
            raise SyntaxError('Target should be one of "Forex","Futures","Stock"')

        if not isinstance(feed_list,list): feed_list = [feed_list]
        if not isinstance(strategy_list,list): strategy_list = [strategy_list]

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

    def set_cash(self,cash=100000):
        self.fill.initial_cash = cash

    def set_hedge(self,on=True):
        self.hedge_mode = True

    def set_notify(self,onoff=True):
        self.broker._notify_onoff = onoff

################### middle #######################
    def _pass_fill(self,marketevent):
        """因为Strategy模块用到的是marketevent，所以通过marketevent传进去"""
        e = marketevent
        e.fill = self.fill
        e.cash = [i['cash'] for i in self.fill.cash_list]
        e.position = [i['position'] for i in self.fill.position_dict[e.instrument]]
        e.margin = [i['margin'] for i in self.fill.margin_dict[e.instrument]]
        e.profit = [i['profit'] for i in self.fill.profit_dict[e.instrument]]
        e.total = [i['total'] for i in self.fill.total_list]
        e.avg_price = [i['avg_price'] for i in self.fill.avg_price_dict[e.instrument]]

        self.portfolio.fill = self.fill
        self.broker.fill = self.fill



################### after #######################
