from collections import defaultdict, deque

import pandas as pd
from dataclasses import dataclass, field

from OnePy.constants import OrderType
from OnePy.environment import Environment


@dataclass
class TradeLog(object):
    env = Environment

    buy: float = None
    sell: float = None
    size: float = None

    ticker: str = field(init=False)
    ohlc: float = field(init=False)

    entry_date: str = field(init=False)
    exit_date: str = field(init=False)

    order_type: str = field(init=False)
    execute_type: str = field(init=False)

    entry_price: float = field(init=False)
    exit_price: float = field(init=False)
    pl_points: float = field(init=False)
    re_pnl: float = field(init=False)

    # commission: float = field(init=False)
    # cumulative_total: float = field(init=False)

    def generate(self):
        self.ticker = self.buy.ticker

        self.entry_date = self.buy.trading_date
        self.entry_price = self.buy.first_cur_price
        self.order_type = self.buy.order_type

        self.exit_date = self.sell.trading_date
        self.exit_price = self.sell.first_cur_price
        self.execute_type = self.sell.order_type

        self.pl_points = (self.sell.first_cur_price -
                          self.buy.first_cur_price)*self.earn_short()
        self.re_pnl = self.pl_points*self.size

        return self

    def earn_short(self):
        return -1 if self.buy.order_type == OrderType.Short_sell else 1


class MatchEngine(object):
    env = Environment

    def __init__(self):
        self.long_log_pure = defaultdict(deque)
        self.long_log_with_trigger = defaultdict(deque)
        self.short_log_pure = defaultdict(deque)
        self.short_log_with_trigger = defaultdict(deque)
        self.finished_log = []

    def _append_finished(self, buy_order, sell_order, size):
        log = TradeLog(buy_order, sell_order, size).generate()
        self.finished_log.append(log)

    def _search_father(self, order, log_with_trigger):
        for i in log_with_trigger:
            if i.mkt_id == order.father_mkt_id:
                self._append_finished(i, order, order.size)
                log_with_trigger.remove(i)

                break

    def _del_in_mkt_dict(self, mkt_id):
        if mkt_id in self.env.orders_pending_mkt_dict:
            del self.env.orders_pending_mkt_dict[mkt_id]

    def _pair_one_by_one(self, order_list, sell_size, order, counteract=False):
        buy_order = order_list.popleft()
        buy_size = buy_order.track_size
        diff = buy_order.track_size = buy_size - sell_size

        if diff > 0:
            self._append_finished(buy_order, order, sell_size)
            order_list.appendleft(buy_order)

            if counteract:  # 修改dict中订单size
                for order in self.env.orders_pending_mkt_dict[buy_order.mkt_id]:
                    order.size = buy_order.track_size

        elif diff == 0:
            self._append_finished(buy_order, order, sell_size)

            if counteract:
                self._del_in_mkt_dict(buy_order.mkt_id)

        else:
            self._append_finished(buy_order, order, buy_size)
            sell_size -= buy_size

            if counteract:
                self._del_in_mkt_dict(buy_order.mkt_id)
            self._pair_one_by_one(order_list, sell_size, order)

    def _pair_order(self, long_or_short, order):  # order should be sell or short cover
        if long_or_short == 'long':
            log_pure = self.long_log_pure[order.ticker]
            log_with_trigger = self.long_log_with_trigger[order.ticker]
        elif long_or_short == 'short':
            log_pure = self.short_log_pure[order.ticker]
            log_with_trigger = self.short_log_with_trigger[order.ticker]

        sell_size = order.size

        if order.father_mkt_id:
            self._search_father(order, log_with_trigger)

        else:

            try:
                self._pair_one_by_one(log_pure, sell_size, order)
            except IndexError:
                self._pair_one_by_one(log_with_trigger, sell_size, order, True)

    def match_order(self, order):
        if order.order_type == OrderType.Buy:
            order.track_size = order.size

            if order.is_pure():
                self.long_log_pure[order.ticker].append(order)
            else:
                self.long_log_with_trigger[order.ticker].append(order)
        elif order.order_type == OrderType.Short_sell:
            order.track_size = order.size

            if order.is_pure():
                self.short_log_pure[order.ticker].append(order)
            else:
                self.short_log_with_trigger[order.ticker].append(order)

        elif order.order_type == OrderType.Sell:
            self._pair_order('long', order)

        elif order.order_type == OrderType.Short_cover:
            self._pair_order('short', order)

    def generate_trade_log(self):

        log_dict = defaultdict(list)
        execute_price = []

        for log in self.finished_log:
            log_dict['ticker'].append(log.ticker)
            log_dict['entry_date'].append(log.entry_date)
            log_dict['entry_price'].append(log.entry_price)
            log_dict['order_type'].append(log.order_type)
            log_dict['size'].append(log.size)
            log_dict['exit_date'].append(log.exit_date)
            log_dict['exit_price'].append(log.exit_price)

            # log_dict['execute_type'].append ( log.execute_type)

            log_dict['pl_points'].append(log.pl_points)
            log_dict['re_pnl'].append(log.re_pnl)

        return pd.DataFrame(log_dict)
