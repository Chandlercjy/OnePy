from abc import ABCMeta, abstractmethod
from copy import copy
from itertools import count

from OnePy.environment import Environment
from OnePy.variables import GlobalVariables


class OrderBase(metaclass=ABCMeta):

    env = Environment()
    gvar = GlobalVariables()
    counter = count(1)

    def __init__(self, signal, mkt_id, trigger_key):
        self.signal = signal
        self.ticker = signal.ticker
        self.price = signal.price
        self.units = signal.units
        self.order_type = signal.order_type
        self.trigger_key = trigger_key

        self.order_id = next(self.counter)
        self.mkt_id = mkt_id

        self.for_trail = None

    def cur_price(self):
        return self.env.feeds[self.ticker].cur_price


class PendingOrderBase(OrderBase):
    @property
    def cur_high(self):
        return self.env.feeds[self.ticker].high

    @property
    def cur_low(self):
        return self.env.feeds[self.ticker].low

    def get_triggered_signal(self):
        if self.is_triggered():
            if self.is_with_mkt():
                return self._generate_bare_signal()
            else:
                return self._generate_full_signal()

    def _generate_bare_signal(self):
        return SignalByTrigger(order_type=self.signal.order_type,
                               units=self.signal.units,
                               ticker=self.signal.ticker,
                               execute_price=self.target_price,
                               datetime=self.env.feeds[ticker].date,
                               exec_type=self.__class__.__name__)

    def _generate_full_signal(self):
        full_signal = copy(self.signal)
        full_signal.execute_price = self.target_price
        full_signal.exec_type = self.__class__.__name__

        return full_signal

    def is_with_mkt(self):
        return False if self.trigger_key else True

    def below_price(self, diff):
        return self.price - diff

    def above_price(self, diff):
        return self.price + diff

    def money(self):
        return self.signal[self.trigger_key]

    @abstractmethod
    def target_price(self):
        raise NotImplemented

    @abstractmethod
    def is_triggered(self):
        raise NotImplemented

    @property
    def in_the_middle(self):
        if self.cur_low < self.target_price < self.cur_high:
            return True


class TrailingOrderBase(PendingOrderBase):
    pass
