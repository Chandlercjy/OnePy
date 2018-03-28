from abc import ABCMeta, abstractmethod
from copy import copy
from itertools import count

from OnePy.environment import Environment
from OnePy.sys_model.signals import SignalByTrigger
from OnePy.variables import GlobalVariables


class OrderBase(metaclass=ABCMeta):

    env = Environment()
    gvar = GlobalVariables()
    counter = count(1)

    def __init__(self, signal, mkt_id, trigger_key):
        self.signal = signal
        self.ticker = signal.ticker
        self.units = signal.units
        self.order_type = signal.order_type
        self.trigger_key = trigger_key
        self.first_cur_price = self.cur_price  # 记录订单发生时刻的现价

        self.order_id = next(self.counter)
        self.mkt_id = mkt_id

    def cur_price(self):
        return self.env.feeds[self.ticker].cur_price


class PendingOrderBase(OrderBase):

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
        return self.signal.get(f'{self.trigger_key}_pct')

    @property
    def difference(self):
        if self.pct:
            return abs(self.pct*self.first_cur_price)

        return abs(self.money/self.units)

    @property
    def target_price(self):
        if self.target_below:
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
        return False if self.trigger_key else True

    def below_price(self, diff):
        return self.signal.price - diff

    def above_price(self, diff):
        return self.signal.price + diff

    def _generate_bare_signal(self):
        return SignalByTrigger(order_type=self.order_type,
                               units=self.units,
                               ticker=self.ticker,
                               execute_price=self.target_price,
                               datetime=self.env.feeds[self.ticker].date,
                               exec_type=self.__class__.__name__)

    def _generate_full_signal(self):
        full_signal = copy(self.signal)
        full_signal.execute_price = self.target_price
        full_signal.exec_type = self.__class__.__name__

        return full_signal

    def get_triggered_signal(self):
        if self.is_triggered():
            if self.is_with_mkt():
                return self._generate_bare_signal()
            else:
                return self._generate_full_signal()


class TrailingOrderBase(PendingOrderBase):

    env = Environment()
    gvar = GlobalVariables()

    def __init__(self, signal, mkt_id, trigger_key):
        super().__init__(signal, mkt_id, trigger_key)
        self.latest_target_price = self.initialize_latest_target_price()

    def initialize_latest_target_price(self):
        if self.target_below:
            return self.cur_price - self.difference

        return self.cur_price + self.difference

    @abstractmethod
    def target_below(self) -> bool:
        return NotImplementedError

    @property
    def difference(self):
        if self.pct:
            return abs(self.pct*self.cur_price)

        return abs(self.money/self.units)

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
