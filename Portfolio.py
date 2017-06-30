import datetime
import numpy as np
import pandas as pd

from abc import ABCMeta, abstractmethod
from math import floor

from event import FillEvent, OrderEvent, events

from performance import create_sharpe_ratio, create_drawdowns
from fx_config import deposit_proportion, pip_config

class Portfolio(object):

    __metaclass__ = ABCMeta

    def __init__(self,events,bars,start_date,initial_capital,leverage):
        self.events = events

        self.leverage = leverage

        self.bars = bars
        self.symbol_list = self.bars.symbol_list

        self.start_date = start_date
        self.initial_capital = initial_capital

        self.log_list = self._construct_log_list()
        self.log_list2 = self._construct_log_list(True)

        self.all_positions = self._construct_all_positions()

        self.cur_posit = dict( (k,v) for k,v in [(s,0)
                                     for s in self.log_list2])
        self.all_holdings = self._construct_all_holdings()
        self.cur_holdings = self._construct_cur_holdings()

        self.current_trade_log=[]
        self.trade_log = []


    @abstractmethod
    def update_signal(self, signal):
        raise NotImplementedError('Should implement update_signal()')

    @abstractmethod
    def update_fill(self, fill):
        raise NotImplementedError('Should implement update_fill()')

    def _construct_log_list(self,avp=False):
        d = []
        if avp:
            for i in self.symbol_list:
                l = i + '_long'
                s = i + '_short'
                avpl = i + '_long_avp'
                avps = i + '_short_avp'
                d.append(l)
                d.append(s)
                d.append(avpl)
                d.append(avps)
            return d
        else:
            for i in self.symbol_list:
                l = i + '_long'
                s = i + '_short'
                d.append(l)
                d.append(s)
            return d

    # private function
    def _construct_all_positions(self):
        d = dict( (k,v) for k, v in [(s, 0) for s in self.log_list])
        d['datetime'] = self.start_date
        return [d]

    def _construct_all_holdings(self):
        d = dict( (k,v) for k,v in [(s,0.0) for s in self.log_list])
        d['datetime'] = self.start_date
        d['cash'] = self.initial_capital
        d['commission'] = 0.0
        d['total'] = self.initial_capital
        return [d]

    def _construct_cur_holdings(self):
        # construct a dict for current holdings
        d = dict( (k,v) for k,v in [(s,0.0) for s in self.log_list])
        d['datetime'] = self.start_date
        d['cash'] = self.initial_capital
        d['commission'] = 0.0
        d['deposit'] = 0.0
        d['total'] = self.initial_capital
        return d

    def compute_avg_price(self,old_lot,old_price,new_lot,new_price):
        total_lot = old_lot+new_lot
        if total_lot == 0:
            return 0
        else:
            price = (old_lot * old_price + new_lot * new_price) / total_lot
            return price


    def _update_positions_from_fill(self, fill):
        """
        Takes a FilltEvent object and updates the position matrix
        to reflect the new position.

        Parameters:
        fill - The FillEvent object to update the positions with.
        """
        # Check whether the fill is a buy or sell
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1

        if fill.signal_type == 'LONG' or fill.signal_type == 'EXITLONG':
            old_lot = self.cur_posit[fill.symbol+'_long']
            new_lot = self.cur_posit[fill.symbol+'_long'] + fill_dir*fill.quantity_l
            old_price = self.cur_posit[fill.symbol+'_long_avp']
            new_price = fill.price
            self.cur_posit[fill.symbol+'_long_avp'] = self.compute_avg_price(old_lot,old_price,new_lot,new_price)
            self.cur_posit[fill.symbol+'_long'] = new_lot


        # Short is the opposite of long, so -fill_dir
        if fill.signal_type == 'SHORT' or fill.signal_type == 'EXITSHORT':
            old_lot = self.cur_posit[fill.symbol+'_short']
            new_lot = self.cur_posit[fill.symbol+'_short'] - fill_dir*fill.quantity_s
            old_price = self.cur_posit[fill.symbol+'_short_avp']
            new_price = fill.price
            self.cur_posit[fill.symbol+'_short_avp'] = self.compute_avg_price(old_lot,old_price,new_lot,new_price)
            self.cur_posit[fill.symbol+'_short'] = new_lot

        if fill.signal_type == 'EXITALL':
            self.cur_posit[fill.symbol+'_long_avp'] = 0
            self.cur_posit[fill.symbol+'_short_avp'] = 0

            fill_dir = -1
            self.cur_posit[fill.symbol+'_long'] += fill_dir*fill.quantity_l
            self.cur_posit[fill.symbol+'_short'] += fill_dir*fill.quantity_s

    def _update_holdings_from_fill(self, fill):
        """
        Takes a FillEvent object and updates the holdings matrix
        to reflect the holdings value.

        Parameters:
        fill - The FillEvent object to update the holdings with.
        """
        # Check whether the fill is a buy or sell
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1

        # Update holdings list with new quantities
        fill_cost = fill.price * pip_config[fill.symbol]  # Close price

        if fill.signal_type == 'LONG':
            commission = fill.commission * fill.quantity_l
            self.cur_holdings['commission'] += commission
            self.cur_holdings['cash'] -= commission

        # Short is the opposite of long, so -fill_dir
        if fill.signal_type == 'SHORT':
            commission = fill.commission * fill.quantity_s
            self.cur_holdings['commission'] += commission
            self.cur_holdings['cash'] -= commission

        # if fill.signal_type == 'EXITLONG':
        # if fill.signal_type == 'EXITSHORT':
        # if fill.signal_type == 'EXITALL':

        # calculate_deposit
        t = {}
        for s in self.symbol_list:
            One_lot_depo = 100000.0 / self.leverage * deposit_proportion[s]
            # Approximation to the real value
            l_depo = self.cur_posit[s+'_long'] * One_lot_depo
            s_depo = self.cur_posit[s+'_short'] * One_lot_depo
            t[s] = l_depo + s_depo

        self.cur_holdings['deposit'] = sum(t.values())

    def _update_trade_log_from_fill(self,fill):
        d = {}
        cur_quantity_l = self.cur_posit[fill.symbol+'_long']
        cur_quantity_s = self.cur_posit[fill.symbol+'_short']

        cash = self.cur_holdings['cash'] - self.cur_holdings['deposit']

        if fill.signal_type == 'LONG':
            d['s_type'] = 'LONG'
            d['symbol'] = fill.symbol
            d['datetime'] = fill.timeindex
            d['price'] = fill.price
            d['qty'] = fill.quantity_l
            d['cur_positions'] = cur_quantity_l
            d['cash'] = cash
            d['total'] = self.cur_holdings['cash']

        if fill.signal_type == 'SHORT':
            d['s_type'] = 'SHORT'
            d['symbol'] = fill.symbol
            d['datetime'] = fill.timeindex
            d['price'] = fill.price
            d['qty'] = fill.quantity_s
            d['cur_positions'] = cur_quantity_s
            d['cash'] = cash
            d['total'] = self.cur_holdings['cash']


        if fill.signal_type == 'EXITLONG' or fill.signal_type == 'EXITALL':
            # if cur_quantity_l > 0 and cur_quantity_s == 0:
            d['s_type'] = 'EXIT_LONG'
            d['symbol'] = fill.symbol
            d['datetime'] = fill.timeindex
            d['price'] = fill.price
            d['qty'] = fill.quantity_l
            d['cur_positions'] = cur_quantity_l
            # d['pl_points'] = 0
            d['cash'] = cash
            d['total'] = self.cur_holdings['cash']

        if fill.signal_type == 'EXITSHORT' or fill.signal_type == 'EXITALL':
            # if cur_quantity_s > 0 and cur_quantity_l == 0:
            d['s_type'] = 'EXIT_SHORT'
            d['symbol'] = fill.symbol
            d['datetime'] = fill.timeindex
            d['price'] = fill.price
            d['qty'] = fill.quantity_s
            d['cur_positions'] = cur_quantity_s
            # d['pl_points'] = 0
            d['cash'] = cash
            d['total'] = self.cur_holdings['cash']

        if fill.signal_type == 'EXITALL':
            # if cur_quantity_s > 0 and cur_quantity_l > 0:
            d['s_type'] = 'EXIT_ALL'
            d['symbol'] = fill.symbol
            d['datetime'] = fill.timeindex
            d['price'] = fill.price
            d['qty'] = fill.quantity_s + fill.quantity_l
            d['cur_positions'] = 0
            # d['pl_points'] = 0
            d['cash'] = cash
            d['total'] = self.cur_holdings['cash']

        # update the trade_log
        self.current_trade_log = d

    def _update_timeindex(self):
        bars = {}
        for sym in self.symbol_list:
            bars[sym] = self.bars.get_latest_bars(sym, N=1)

        # Update positions
        dp = dict((k,v) for k,v in [(s,0) for s in self.log_list2])
        dp['datetime'] = bars[self.symbol_list[0]][0]['date']

        for s in self.log_list2:
            dp[s] = self.cur_posit[s]

        # Append the current positions
        self.all_positions.append(dp)

        # Update holdings
        dh = dict( (k,v) for k, v in [(s, 0) for s in self.log_list] )
        dh['datetime'] = bars[self.symbol_list[0]][0]['date']

        # Calculate cash
        for s in self.symbol_list:
            if len(self.bars.latest_bar_dict[s]) > 1:
                fill_cost = self.bars.latest_bar_dict[s][-1]['close'] * pip_config[s]  # Close price
                last_cost = self.bars.latest_bar_dict[s][-2]['close'] * pip_config[s]
                diff = (fill_cost - last_cost)
                profit = diff * self.cur_posit[s+'_long'] - diff * self.cur_posit[s+'_short']
                self.cur_holdings['cash'] += profit #- fill.commission

        dh['commission'] = self.cur_holdings['commission']

        # calculate_deposit
        t = {}
        for s in self.symbol_list:
            One_lot_depo = 100000.0 / self.leverage * deposit_proportion[s]
            # Approximation to the real value
            l_depo = self.cur_posit[s+'_long'] * One_lot_depo
            dh[s+'_long'] = l_depo

            s_depo = self.cur_posit[s+'_short'] * One_lot_depo
            dh[s+'_short'] = s_depo
            t[s] = l_depo + s_depo

        dh['deposit'] = sum(t.values())
        dh['total'] = self.cur_holdings['cash']
        dh['cash'] = dh['total'] - dh['deposit']
        # Append the current holdings
        self.all_holdings.append(dh)


################################# Others #################################

    def create_equity_curve_df(self):
        curve = pd.DataFrame(self.all_positions)
        df = pd.DataFrame(self.all_holdings)
        curve.set_index('datetime', inplace=True)
        df.set_index('datetime', inplace=True)

        curve['returns'] = df['cash'].pct_change()
        curve['equity_curve'] = (1.0+curve['returns']).cumprod()
        return curve

    def output_summary_stats(self):
        equity_curve = self.create_equity_curve_df()

        total_return = equity_curve['equity_curve'][-1]
        returns = equity_curve['returns']
        pnl = equity_curve['equity_curve']

        sharpe_ratio = create_sharpe_ratio(returns)
        max_dd, dd_duration = create_drawdowns(pnl)

        stats = [('Total Return', '%0.2f%%' % ((total_return - 1.0) * 100.0)),
                 ('sharpe Ratio', '%0.2f' % sharpe_ratio),
                 ('Max Drawdown', '%0.2f%%' % (max_dd * 100.0)),
                 ('Drawdown Duration', '%s' % dd_duration)]
        return stats

########### calculate for strategy ################

    def total_deposit(self):
        return self.cur_holdings['deposit']

    def short_profit(self):
        p = {}
        for s in self.symbol_list:
            price = self.bars.get_latest_bars(s)[0]['close']
            avp = self.cur_posit[s + '_short_avp']
            posit = self.cur_posit[s + '_short']
            p[s] = -(price - avp) * posit
        return sum(p.values())

    def long_profit(self):
        p = {}
        for s in self.symbol_list:
            price = self.bars.get_latest_bars(s)[0]['close']
            avp = self.cur_posit[s + '_long_avp']
            posit = self.cur_posit[s + '_long']
            p[s] = (price - avp) * posit
        return sum(p.values())

    def short_lots(self):
        l = {}
        for s in self.symbol_list:
            l[s] = self.cur_posit[s+'_short']
        return sum(l.values())

    def long_lots(self):
        l = {}
        for s in self.symbol_list:
            l[s] = self.cur_posit[s+'_long']
        return sum(l.values())

    def deposit_ratio(self):
        return 100.0 * self.cur_holdings['deposit'] / self.cur_holdings['cash']

#################### DIY portfolio ###################
class NaivePortfolio(Portfolio):
    def __init__(self, bars, start_date='1993-08-07', initial_capital=100000.0,leverage=200,):
        super(NaivePortfolio, self).__init__(events,bars,start_date,initial_capital,leverage)

    def _generate_naive_order(self, signal):
        """
        Simply transacts an OrderEvent object as a constant quantity
        sizing of the signal object, without risk management or
        position sizing considerations.

        Parameters:
        signal - The SignalEvent signal information.
        """
        order = None

        symbol = signal.symbol
        signal_type = signal.signal_type
        lots = signal.lots
        dt = signal.datetime
        price = signal.price
        cash = self.cur_holdings['cash']
        One_lot_depo = 100000.0 / self.leverage * deposit_proportion[symbol]


        if signal.percent:
            mkt_quantity = round(lots * 0.01 * cash / One_lot_depo , 2)
        else:
            mkt_quantity = lots

        cur_quantity_l = self.cur_posit[symbol+'_long']
        cur_quantity_s = self.cur_posit[symbol+'_short']
        order_type = 'MKT'

        if signal_type == 'LONG':
            order = OrderEvent(dt, signal_type, symbol, price,
                               order_type,
                               quantity_l = mkt_quantity,
                               quantity_s = 0,
                               direction = 'BUY')
        if signal_type == 'SHORT':
            order = OrderEvent (dt, signal_type, symbol,price,
                                order_type,
                                quantity_l = 0,
                                quantity_s = mkt_quantity,
                                direction = 'SELL')

        if signal_type == 'EXITLONG' and cur_quantity_l > 0:
            # check whether to exit all long
            if mkt_quantity >= cur_quantity_l:
                mkt_quantity = cur_quantity_l
            order = OrderEvent(dt, signal_type, symbol, price,
                               order_type,
                               quantity_l = mkt_quantity,
                               quantity_s = 0,
                               direction = 'SELL')

        if signal_type == 'EXITSHORT' and cur_quantity_s > 0:
            # check whether to exit all short
            if mkt_quantity >= cur_quantity_s:
                mkt_quantity = cur_quantity_s
            order = OrderEvent(dt, signal_type, symbol, price,
                               order_type,
                               quantity_l = 0,
                               quantity_s = mkt_quantity,
                               direction = 'BUY')


        # ALL LONG
        if signal_type == 'EXITALL':
            if cur_quantity_l > 0 and cur_quantity_s == 0:
                order = OrderEvent(dt, signal_type, symbol, price,
                                   order_type,
                                   quantity_l = cur_quantity_l,
                                   quantity_s = 0,
                                   direction = 'SELL')
        # ALL SHORT
            if cur_quantity_s > 0 and cur_quantity_l == 0:
                order = OrderEvent(dt, signal_type, symbol, price,
                                   order_type,
                                   quantity_l = 0,
                                   quantity_s = cur_quantity_s,
                                   direction = 'BUY')
        # SHORT & LONG
            if cur_quantity_s > 0 and cur_quantity_l > 0:
                order = OrderEvent(dt, signal_type, symbol, price,
                                   order_type,
                                   quantity_l = cur_quantity_l,
                                   quantity_s = cur_quantity_s,
                                   direction = 'BUY&SELL')
        return order

    def update_signal(self, signal):
        if signal.type == 'Signal':
            order_event = self._generate_naive_order(signal)
            self.events.put(order_event)

    def update_fill(self, fill):
        """
        Updates the portfolio current positions and holdings
        from a FillEvent.
        """
        self._update_positions_from_fill(fill)
        self._update_holdings_from_fill(fill)
        self._update_trade_log_from_fill(fill)

        if fill.quantity_s != 0 or fill.quantity_l != 0:
            # Append the trade_log
            self.trade_log.append(self.current_trade_log)

class MyPortfolio(Portfolio):
    def __init__(self, bars, start_date='start_date', initial_capital=100000.0):
        super(MyPortfolio, self).__init__(events,bars,start_date,initial_capital)
