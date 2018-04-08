from abc import ABCMeta, abstractmethod
from itertools import count

from OnePy.constants import OrderStatus, OrderType
from OnePy.environment import Environment
from OnePy.sys_module.models.signals import SignalByTrigger


class OrderBase(metaclass=ABCMeta):

    env = Environment
    counter = count(1)

    def __init__(self, signal, mkt_id):
        self.status = OrderStatus.Created
        self.signal = signal
        self.ticker = signal.ticker
        self.size = signal.size
        self.order_type = signal.order_type

        self.order_id = next(self.counter)
        self.mkt_id = mkt_id

        self.first_cur_price = self.get_first_cur_price()  # 记录订单发生时刻的现价

    @property
    def trading_date(self):
        return self.signal.datetime

    def get_first_cur_price(self):
        if self.signal.execute_price:
            return self.signal.execute_price

        return self.env.feeds[self.ticker].execute_price


class PendingOrderBase(OrderBase):

    def __init__(self, signal, mkt_id, trigger_key):
        super().__init__(signal, mkt_id)
        self.trigger_key = trigger_key

    @abstractmethod
    def target_below(self) -> bool:
        raise NotImplementedError

    @property
    def cur_high(self):
        return self.env.feeds[self.ticker].high

    @property
    def cur_low(self):
        return self.env.feeds[self.ticker].low

    @property
    def money(self):
        return self.signal.get(self.trigger_key)

    @property
    def pct(self):
        if 'pct' in self.trigger_key:
            return self.signal.get(self.trigger_key)

    @property
    def difference(self):
        if self.pct:
            return abs(self.pct*self.first_cur_price)

        return abs(self.money/self.size)

    @property
    def target_price(self):
        if self.trigger_key == 'price':
            return self.signal.price

        elif self.target_below:
            return self.below_price(self.difference)

        return self.above_price(self.difference)

    @property
    def is_triggered(self):
        if self.target_below:
            return self.cur_low_cross_target_price()

        return self.cur_high_cross_target_price()

    def cur_high_cross_target_price(self):
        return True if self.target_price < self.cur_high else False

    def cur_low_cross_target_price(self):
        return True if self.target_price > self.cur_low else False

    def is_with_mkt(self):
        return False if self.trigger_key == 'price' else True

    def below_price(self, diff):
        return self.first_cur_price - diff

    def above_price(self, diff):
        return self.first_cur_price + diff


class TrailingOrderBase(PendingOrderBase):

    env = Environment

    def __init__(self, signal, mkt_id, trigger_key):
        super().__init__(signal, mkt_id, trigger_key)
        self.latest_target_price = self.initialize_latest_target_price()

    @property
    def cur_open(self):
        return self.env.feeds[self.ticker].open

    def initialize_latest_target_price(self):
        if self.target_below:
            return self.first_cur_price - self.difference

        return self.first_cur_price + self.difference

    @abstractmethod
    def target_below(self) -> bool:
        return False

    @property
    def difference(self):
        if self.pct:
            return abs(self.pct*self.cur_open)

        return abs(self.money/self.size)

    def with_high(self, diff):
        return self.cur_high - diff

    def with_low(self, diff):
        return self.cur_low + diff

    @property
    def target_price(self):

        if self.target_below:
            new = self.with_high(self.difference)
            self.latest_target_price = max(self.latest_target_price, new)
        else:
            new = self.with_low(self.difference)
            self.latest_target_price = min(self.latest_target_price, new)

        return self.latest_target_price
