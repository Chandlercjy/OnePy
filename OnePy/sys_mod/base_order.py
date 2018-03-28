from abc import ABCMeta, abstractmethod, abstractproperty
from copy import copy
from itertools import count

from OnePy.components.trailing_order_checker import TrailingOrderChecker


class OrderBase(metaclass=ABCMeta):

    env = None
    gvar = None
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


class MarketOrder(OrderBase):

    @property
    def execute_price(self):
        """
        price_pct已经在orderGenerator中转换过，
        所以不用考，但是要考虑如果是其他单转化为市价单，
        那price就会不一样
        """

        if self.is_absolute_mkt():
            return self.signal.execute_price

        return self.env.feeds[self.ticker].execute_price

    def is_absolute_mkt(self):
        return True if self.signal.execute_price else False


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

    @abstractproperty
    def target_price(self):
        raise NotImplemented

    @abstractmethod
    def is_triggered(self):
        raise NotImplemented

    @property
    def in_the_middle(self):
        if self.cur_low < self.target_price < self.cur_high:
            return True


class LimitBuyOrder(PendingOrderBase):
    """
    如果是挂单，只需要判断是不是触发，
    如果触发，就返回执行市价单，而且是必成的那种,而且带着其他挂单
    如果是跟随mkt的挂单，则需要判断是否触发，
        如果触发，就发送一个裸的必成市价单，即要清空signal，剩裸price

    而且如果触发了，要从list中删除
    """
    @property
    def target_price(self):
        if self.trigger_key:
            result = self.below_price(abs(self.money/self.units))

            return result

    def is_triggered(self):
        if self.target_price > self.cur_low:
            return True


class LimitSellOrder(PendingOrderBase):

    @property
    def target_price(self):
        if self.trigger_key:
            result = self.above_price(abs(self.money/self.units))

            return result

    def is_triggered(self):
        if self.target_price < self.cur_high:
            return True


class StopBuyOrder(PendingOrderBase):

    @property
    def target_price(self):
        if self.trigger_key:
            result = self.above_price(abs(self.money/self.units))

            return result

    def is_triggered(self):
        if self.target_price < self.cur_high:
            return True


class StopSellOrder(PendingOrderBase):

    @property
    def target_price(self):
        if self.trigger_key:
            result = self.below_price(abs(self.money/self.units))

            return result

    def is_triggered(self):
        if self.target_price > self.cur_low:
            return True


class LimitShortSellOrder(PendingOrderBase):

    @property
    def target_price(self):
        if self.trigger_key:
            result = self.above_price(abs(self.money/self.units))

            return result

    def is_triggered(self):
        if self.target_price < self.cur_price:
            return True


class StopShortSellOrder(PendingOrderBase):

    @property
    def target_price(self):
        if self.trigger_key:
            result = self.above_price(abs(self.money/self.units))

            return result

    def is_triggered(self):
        if self.target_price < self.cur_price:
            return True


class LimitCoverShortOrder(PendingOrderBase):

    @property
    def target_price(self):
        if self.trigger_key:
            result = self.above_price(abs(self.money/self.units))

            return result

    def is_triggered(self):
        if self.target_price < self.cur_price:
            return True


class StopCoverShortOrder(PendingOrderBase):

    @property
    def target_price(self):
        if self.trigger_key:
            result = self.above_price(abs(self.money/self.units))

            return result

    def is_triggered(self):
        if self.target_price < self.cur_price:
            return True


class TrailingOrderBase(PendingOrderBase):
    pass


class TralingStopBuyOrder(TrailingOrderBase):

    @property
    def target_price(self):
        if self.trigger_key:
            result = self.above_price(abs(self.money/self.units))

            return result

    def is_triggered(self):
        if self.target_price < self.cur_price:
            return True


class TrailingStopSellOrder(TrailingOrderBase):

    @property
    def target_price(self):
        if self.trigger_key:
            result = self.above_price(abs(self.money/self.units))

            return result

    def is_triggered(self):
        if self.target_price < self.cur_price:
            return True


class TrailingStopShortSellOrder(TrailingOrderBase):

    @property
    def target_price(self):
        if self.trigger_key:
            result = self.above_price(abs(self.money/self.units))

            return result

    def is_triggered(self):
        if self.target_price < self.cur_price:
            return True
