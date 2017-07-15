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
        self.fill = Fill()

    def sunny(self):

        # run_once function
        Feed.run_first(self.feed_list)

        while True:
            try:
                event = events.get(False)
            except Queue.Empty:
                Feed.load_all_feed(self.feed_list)

            else:
                if event is not None:
                    if event.type == 'Market':
                        [s(event).run_strategy() for s in self.strategy_list]

                    if event.type == 'Signal':
                        self.portfolio(self.feed_list).run_portfolio(event)

                    if event.type == 'Order':
                        self.broker.run_broker(event)

                    if event.type == 'Fill':
                        self.fill._update_info(event)

                    if event.type == 'Pend':
                        pass

                if Feed.check_finish_backtest(self.feed_list):
                    print 'Final Portfolio Value: '
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

    def set_backtest(self, feed_list,strategy_list,portfolio,broker):
        '''因为各个模块之间相互引用，所以要按照顺序add和set模块'''
        self._adddata(feed_list)
        self._set_portfolio(portfolio)
        self._addstrategy(strategy_list)
        self._set_broker(broker)




################### middle #######################






################### after #######################
