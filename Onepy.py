import pandas as pd
import itertools
import copy
import Queue
from threading import Thread
import multiprocessing

from statistics import stats
from performance import generate_perfect_log
from execution import SimulatedExecutionHandler
from event import events
from plotter import plotter

import os,sys
import matplotlib.pyplot as plt
import matplotlib.style as style
import threading

class OnePiece():
    def __init__(self, data, strategy, portfolio):
        self.events = events
        self.Feed = data
        self.strategy = strategy
        self.portfolio = portfolio
        self.broker = SimulatedExecutionHandler(commission=None)

        self.cur_holdings = self.portfolio.current_holdings
        self.cur_positions = self.portfolio.current_positions
        self.all_holdings = self.portfolio.all_holdings
        self.all_positions = self.portfolio.all_positions
        self.initial_capital = self.portfolio.initial_capital


        self._activate = {}
        self._activate['print_order'] = False
        self._activate['print_stats'] = False
        self._activate['full_stats'] = False

    def sunny(self):
        while True:
            try:
                event = self.events.get(False)
            except Queue.Empty:
                self.Feed.update_bars()
                self.portfolio._update_timeindex()
            else:
                if event is not None:
                    if event.type == 'Market':
                        self.strategy.luffy()

                    if event.type == 'Signal':
                        self.portfolio.update_signal(event)

                    if event.type == 'Order':
                        if (self.cur_holdings['cash'] > event.quantity_l*event.price and
                            self.cur_holdings['cash'] > event.quantity_s*event.price):

                            self.broker.execute_order(event)

                            # print order
                            if self._activate['print_order']:
                                event.print_order()

                    if event.type == 'Fill':
                        self.portfolio.update_fill(event)

                        if self._activate['print_order']:
                            event.print_executed()

                if self.Feed.continue_backtest == False:
                    print 'Final Portfolio Value: '+ str(self.all_holdings[-1]['total'])

                    if self._activate['print_stats']:
                        self.portfolio.create_equity_curve_df()
                        print self.portfolio.output_summary_stats()

                    if self._activate['full_stats']:
                        self.get_analysis()
                    break

    def print_trade(self):
        self._activate['print_order'] = True

    def print_stats(self,full=False):
        self._activate['print_stats'] = True
        if full:
            self._activate['full_stats'] = True

    def get_equity_curve(self):
        df = self.portfolio.create_equity_curve_df()
        df.index =pd.DatetimeIndex(df.index)
        df.drop('1993-08-07',inplace=True)
        return df

    def get_analysis(self):
        ori_tlog = self.get_log(True)
        tlog = self.get_log()
        dbal = self.get_equity_curve()
        start = self.get_equity_curve().index[0]
        end = self.get_equity_curve().index[-1]
        capital = self.initial_capital
        print stats(tlog,ori_tlog, dbal, start, end, capital)

    def get_log(self,exit=False):
        # Original log, include exit_order
        ori_tlog = pd.DataFrame(self.portfolio.trade_log)
        ori_tlog.set_index('datetime',inplace=True)
        ori_tlog.index =pd.DatetimeIndex(ori_tlog.index)
        # generate PnL, perfect log
        log,n = generate_perfect_log(tlog = ori_tlog,
                                   latest_bar_dict = self.Feed.latest_bar_dict)
        df = pd.DataFrame(log)
        df.set_index('datetime',inplace=True)
        df.index = pd.DatetimeIndex(df.index)
        df.sort_index(inplace=True)
        if exit:
            print 'Still_Opening_trades: ' + str(n)
            return ori_tlog[['symbol','s_type','price','qty',
                        'cur_positions','cash','total']]
        else:
            return df[['symbol','s_type','price','qty','cur_positions',
                       'exit_date','period','cash','PnL','total']]

####################### from portfolio ###############################

    def get_current_holdings(self):
        return pd.DataFrame(self.cur_holdings)

    def get_current_positions(self):
        return pd.DataFrame(self.cur_positions)

    def get_all_holdings(self):
        df = pd.DataFrame(self.all_holdings)
        df.set_index('datetime',inplace=True)
        df.drop('1993-08-07',inplace=True)
        df.index =pd.DatetimeIndex(df.index)
        return df

    def get_all_positions(self):
        df = pd.DataFrame(self.all_positions)
        df.set_index('datetime',inplace=True)
        df.drop('1993-08-07',inplace=True)
        df.index =pd.DatetimeIndex(df.index)
        return df

    def get_symbol_list(self):
        return self.portfolio.symbol_list

    def get_initial_capital(self):
        return self.initial_capital

    def plot(self,symbol,engine='plotly',notebook=False):
        data = plotter(latest_bar_dict = self.Feed.latest_bar_dict,
                        enquity_curve = self.get_equity_curve(),
                        tlog = self.get_log(),
                        positions = self.get_all_positions(),
                        holdings = self.get_all_holdings())
        data.plot(symbol=symbol,engine=engine,notebook=notebook)

    def plot_log(self,symbol,engine='plotly',notebook=False):
        data = plotter(latest_bar_dict = self.Feed.latest_bar_dict,
                        enquity_curve = self.get_equity_curve(),
                        tlog = self.get_log(),
                        positions = self.get_all_positions(),
                        holdings = self.get_all_holdings())
        data.plot_log(symbol=symbol,engine=engine,notebook=notebook)

######################### For Optimize ###############################

def params_generator(*args):
    d = {}
    for i in range(len(args)):
        d[i] = args[i]

    if len(args) == 1:
        return itertools.product(d[0])
    if len(args) == 2:
        return itertools.product(d[0],d[1])
    if len(args) == 3:
        return itertools.product(d[0],d[1],d[2])
    if len(args) == 4:
        return itertools.product(d[0],d[1],d[2],d[3])
    if len(args) == 5:
        return itertools.product(d[0],d[1],d[2],d[3],d[4])
    if len(args) == 6:
        return itertools.product(d[0],d[1],d[2],d[3],d[4],d[5])
    if len(args) == 7:
        return itertools.product(d[0],d[1],d[2],d[3],d[4],d[5],d[6])
    if len(args) == 8:
        return itertools.product(d[0],d[1],d[2],d[3],d[4],d[5],d[6],d[7])
    if len(args) == 9:
        return itertools.product(d[0],d[1],d[2],d[3],d[4],d[5],d[6],d[7],d[8])
    if len(args) == 10:
        return itertools.product(d[0],d[1],d[2],d[3],d[4],d[5],d[6],d[7],d[8],d[9])

def optimizer(strategyclass,portfolioclass,feed,params_generator,pkl_name=None):
    log = {}
    if pkl_name is None:
        pkl_name = 'optimizer_log'

    pkl_path = os.path.join(sys.path[0],'%s.pkl' % pkl_name)
    pd.to_pickle(log, pkl_path)

    while True:
        try:
            p_list = params_generator.next()
        except:
            break
        else:
            backup = copy.deepcopy(feed)
            data = backup
            strategy = strategyclass(data,p_list)
            portfolio = portfolioclass(data)
            go = OnePiece(data, strategy, portfolio)

            def combine():
                go.sunny()
                print p_list
                log = pd.read_pickle(pkl_path)
                log[p_list] = go.get_all_holdings().iat[-1,-1]
                pd.to_pickle(log, pkl_path)
            p = multiprocessing.Process(target=combine)
            p.daemon=True
            p.start()
    p.join()

def opti_analysis(pkl_path):
    log = pd.read_pickle(pkl_path)
    log = dict((v,k) for k,v in log.iteritems())

    df = pd.DataFrame(log).T
    df.reset_index(inplace=True)
    df.rename(columns={'index':'Capital'},inplace=True)

    style.use('ggplot')
    df[['Capital']].plot(table=df)
    plt.show()

######################################################################
