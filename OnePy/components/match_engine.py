from collections import deque

from dataclasses import dataclass, field

from OnePy.constants import OrderType
from OnePy.environment import Environment


@dataclass
class TradeLog(object):

    buy: float = None
    sell: float = None
    size: float = None

    enter_date: str = field(init=False)
    exit_date: str = field(init=False)

    order_type: str = field(init=False)
    execute_type: str = field(init=False)

    entry_price: float = field(init=False)
    pl_points: float = field(init=False)
    re_profit: float = field(init=False)

    commission: float = field(init=False)
    cumulative_total: float = field(init=False)

    def generate(self):

        self.enter_date = self.buy.trading_date
        self.exit_date = self.sell.trading_date
        self.order_type = self.buy.order_type

        self.execute_type = self.sell.order_type
        self.entry_price = self.buy.first_cur_price

        self.pl_points = (self.sell.first_cur_price -
                          self.buy.first_cur_price)*self.earn_short()
        self.re_profit = self.pl_points*self.size

        return self

    def earn_short(self):
        return -1 if self.buy.order_type == OrderType.Short_sell else 1


class MatchEngine(object):
    env = Environment

    def __init__(self):
        self.long_log_pure = deque()
        self.long_log_with_trigger = deque()
        self.short_log_pure = deque()
        self.short_log_with_trigger = deque()
        self.finished_log = []

    def match_order(self, order):
        if order.order_type == OrderType.Buy:
            order.track_size = order.size

            if order.is_pure():
                self.long_log_pure.append(order)
            else:
                self.long_log_with_trigger.append(order)
        elif order.order_type == OrderType.Short_sell:
            order.track_size = order.size

            if order.is_pure():
                self.short_log_pure.append(order)
            else:
                self.short_log_with_trigger.append(order)

        elif order.order_type == OrderType.Sell:
            self.pair_order('long', order)

        elif order.order_type == OrderType.Short_cover:
            self.pair_order('short', order)

    def pair_order(self, long_or_short, order):  # order should be sell or short cover
        if long_or_short == 'long':
            log_pure = self.long_log_pure
            log_with_trigger = self.long_log_with_trigger
        elif long_or_short == 'short':
            log_pure = self.short_log_pure
            log_with_trigger = self.short_log_with_trigger

        sell_size = order.size

        if order.father_mkt_id:
            self.search_father(order, log_with_trigger)

        else:

            try:
                self.pair_one_by_one(log_pure, sell_size, order)
            except IndexError:
                # TODO: 需要改动mkt order对应的挂单
                self.pair_one_by_one(log_with_trigger, sell_size, order)

    def pair_one_by_one(self, order_list, sell_size, order):
        buy_order = order_list.popleft()
        buy_size = buy_order.track_size
        diff = buy_order.track_size = buy_size - sell_size

        if diff > 0:
            self.append_finished(buy_order, order, sell_size)
            order_list.appendleft(buy_order)

        elif diff == 0:
            self.append_finished(buy_order, order, sell_size)

        else:
            self.append_finished(buy_order, order, buy_size)
            sell_size -= buy_size
            self.pair_one_by_one(order_list, sell_size, order)

    def search_father(self, order, log_with_trigger):
        for i in log_with_trigger:
            if i.mkt_id == order.father_mkt_id:
                self.append_finished(i, order, order.size)
                log_with_trigger.remove(i)

                break

    def append_finished(self, buy_order, sell_order, size):
        log = TradeLog(buy_order, sell_order, size).generate()
        self.finished_log.append(log)
