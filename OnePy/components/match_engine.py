from collections import deque

from dataclasses import dataclass

from OnePy.constants import OrderType
from OnePy.environment import Environment


@dataclass
class TradeLog(object):

    enter_date: str = None
    exit_date: str = None

    order_type: str = None
    execute_type: str = None

    entry_price: float = None
    size: float = None
    pl_points: float = None
    re_profit: float = None
    commission: float = None
    cumulative_total: float = None

    buy: float = None
    sell: float = None


class TradeLogFactory(object):

    @classmethod
    def generate(cls, buy, sell, size):
        if buy.order_type == OrderType.Short_sell:
            direction = -1
        else:
            direction = 1

        log = TradeLog()
        log.enter_date = buy.trading_date
        log.exit_date = sell.trading_date

        log.order_type = buy.order_type
        log.execute_type = sell.order_type

        log.entry_price = buy.first_cur_price
        log.size = size
        log.pl_points = (sell.first_cur_price -
                         buy.first_cur_price)*direction
        log.re_profit = log.pl_points*size
        log.commission = None
        log.cumulative_total = None
        log.buy = buy
        log.sell = sell

        return log


class MatchEngine(object):
    env = Environment

    def __init__(self):
        self.long_log_pure = deque()
        self.long_log_with_trigger = deque()
        self.short_log_pure = deque()
        self.short_log_with_trigger = deque()
        self.finished_log = []
        self.total_long = 0
        self.total_short = 0

    def match_order(self, order):
        if order.order_type == OrderType.Buy:
            order.track_size = order.size

            if order.is_pure():
                self.long_log_pure.append(order)
            else:
                self.long_log_with_trigger.append(order)

        elif order.order_type == OrderType.Sell:

            self.consume_sell('long', order)
            self.total_long += self.finished_log[-1].re_profit

        elif order.order_type == OrderType.Short_sell:
            order.track_size = order.size

            if order.is_pure():
                self.short_log_pure.append(order)
            else:
                self.short_log_with_trigger.append(order)

        elif order.order_type == OrderType.Short_cover:
            self.consume_sell('short', order)
            self.total_short += self.finished_log[-1].re_profit

    def consume_sell(self, long_or_short, order):
        if long_or_short == 'long':
            log_pure = self.long_log_pure
            log_with_trigger = self.long_log_with_trigger
        elif long_or_short == 'short':
            log_pure = self.short_log_pure
            log_with_trigger = self.short_log_with_trigger

        sell_size = order.size

        if order.signal.mkt_id:
            for i in log_with_trigger:
                if i.mkt_id == order.signal.mkt_id:
                    self.append_finished(i, order, sell_size)

                    break

        else:

            while True:
                try:
                    buy_order = log_pure.popleft()
                    buy_size = buy_order.track_size
                    diff = buy_order.track_size = buy_size - sell_size

                    if diff > 0:
                        self.append_finished(buy_order, order, sell_size)
                        log_pure.appendleft(buy_order)

                        break
                    elif diff == 0:
                        self.append_finished(buy_order, order, sell_size)

                        break
                    else:
                        self.append_finished(buy_order, order, buy_size)
                        sell_size -= buy_size
                except IndexError:
                    # TODO: 需要改动mkt order对应的挂单
                    buy_order = log_with_trigger.popleft()
                    buy_size = buy_order.track_size
                    diff = buy_order.track_size = buy_size - sell_size

                    if diff > 0:
                        self.append_finished(buy_order, order, sell_size)
                        log_with_trigger.appendleft(buy_order)

                        break
                    elif diff == 0:
                        self.append_finished(buy_order, order, sell_size)

                        break
                    else:
                        self.append_finished(buy_order, order, buy_size)
                        sell_size -= buy_size

    def append_finished(self, buy_order, sell_order, size):
        log = TradeLogFactory.generate(buy_order, sell_order, size)
        self.finished_log.append(log)
