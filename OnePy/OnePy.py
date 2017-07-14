import pandas as pd
import itertools
import copy
import Queue

from event import events

import os,sys
import matplotlib.pyplot as plt
import matplotlib.style as style

import feed as Feed

class OnePiece():
    def __init__(self):
        self.feed_list = []
        self.strategy_list = []

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
                        for i in self.feed_list:
                            print i.cur_bar_dict

                    if event.type == 'Signal':
                        pass

                    if event.type == 'Order':
                        pass

                    if event.type == 'Fill':
                        pass

                if Feed.check_finish_backtest(self.feed_list):
                    print 'Final Portfolio Value: '
                    break

################### before #######################
    def adddata(self, *args):
        [self.feed_list.append(data) for data in args]

    def addstrategy(self, *arg):
        [self.strategy_list.append(strategy) for strategy in args]



################### middle #######################






################### after #######################
