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


class TradeLogFactory(object):

    @classmethod
    def generate(cls, buy, sell, size):

        log = TradeLog()
        log.enter_date = buy.trading_date
        log.exit_date = sell.trading_date

        log.order_type = buy.order_type
        log.execute_type = sell.order_type

        log.entry_price = buy.real_execute_price
        log.size = size
        log.pl_points = sell.real_execute_price - buy.real_execute_price
        log.re_profit = log.pl_points*size
        log.commission = None
        log.cumulative_total = None

        return log


class MatchEngine(object):
    env = Environment

    def __init__(self):
        self.long_log = deque()
        self.short_log = deque()
        self.finished_log = []
        self.total_long = 0
        self.total_short = 0

    def match_order(self, order):
        if order.order_type == OrderType.Buy:
            order.track_size = order.size
            self.long_log.append(order)
        elif order.order_type == OrderType.Sell:
            self.consume_sell(self.long_log, order)
            self.total_long += self.finished_log[-1].re_profit
        elif order.order_type == OrderType.Short_sell:
            order.track_size = order.size
            self.short_log.append(order)
        elif order.order_type == OrderType.Short_cover:
            self.consume_sell(self.short_log, order)
            self.total_short += self.finished_log[-1].re_profit

    def consume_sell(self, long_or_short_log, order):
        """
        若是buy，则添加到long_log
        若是sell，先提取一个buy，
            diff =  buy - sell

            if diff > 0: 把sell弄掉了，buy还剩一些
                ok, 添加记录到finished，有entry和exit date
                将剩一点点的buy插回去
            elif diff == 0: 刚好都清除
                ok, 添加记录到finished，有entry和exit date
            elif diff < 0 : sell还有剩余,还需要继续sell
                添加记录到finished，有entry和exit date
                然后重复继续提取buy
        """

        sell_size = order.size

        while True:
            buy_order = long_or_short_log.popleft()
            buy_size = buy_order.track_size
            diff = buy_order.track_size = buy_size - sell_size

            if diff > 0:
                self.append_finished(buy_order, order, sell_size)
                long_or_short_log.appendleft(buy_order)

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
