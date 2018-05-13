from itertools import count

import numpy as np

from OnePy.constants import OrderStatus, OrderType
from OnePy.sys_module.metabase_env import OnePyEnvBase
from OnePy.sys_module.models.signals import SignalByTrigger


class OrderBase(OnePyEnvBase):

    counter = count(1)

    def __init__(self, signal, mkt_id):
        self.signal = signal
        self.ticker = signal.ticker
        self.size = signal.size

        self.order_id = next(self.counter)
        self.mkt_id = mkt_id

        self.first_cur_price = self._get_first_cur_price()  # 记录订单发生时刻的现价

        self.status = OrderStatus.Created

    @property
    def trading_date(self):
        return self.signal.datetime

    def _get_first_cur_price(self):
        if self.signal.is_absolute_signal():
            return self.signal.execute_price

        return self.env.feeds[self.ticker].execute_price

    @property
    def action_type(self):
        return self.signal.action_type


class PendingOrderBase(OrderBase):

    def __init__(self, signal, mkt_id, trigger_key):
        self.trigger_key = trigger_key
        super().__init__(signal, mkt_id)

    @property
    def action_type(self):
        return self._action_type

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

        if self.signal.execute_price:
            execute_price = self.signal.execute_price
        else:
            execute_price = self.signal.price
        self.env.logger.info(
            f'{self.signal.datetime}, '
            f'{self.signal.ticker}, '
            f'{self.order_type.value} '
            f'{self.action_type.value} '
            f'@ {self.target_price:.5f}, '
            f'{self.status.value}, '
            f'size: {self.size}')

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

    def __init__(self, signal, mkt_id, trigger_key):
        super().__init__(signal, mkt_id, trigger_key)
        self.latest_target_price = self.initialize_latest_target_price()

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

        if self.signal.execute_price:
            execute_price = self.signal.execute_price
        else:
            execute_price = self.signal.price
        self.env.logger.info(
            f'{self.signal.datetime}, '
            f'{self.signal.ticker}, '
            f'{self.order_type.value} '
            f'{self.action_type.value} '
            f'{self.status.value}, '
            f'size: {self.size}')

    @property
    def cur_open(self):
        return self.env.feeds[self.ticker].open

    def initialize_latest_target_price(self):
        if self.target_below:
            return self.first_cur_price - self.difference

        return self.first_cur_price + self.difference

    def target_below(self) -> bool:
        return False

    @property
    def difference(self):
        if self.pct:
            return abs(self.pct*self.first_cur_price)

        return abs(self.money/self.size)

    def with_high(self, diff):
        return np.random.uniform(self.cur_low, self.cur_high - diff)

    def with_low(self, diff):
        return np.random.uniform(self.cur_low + diff, self.cur_high)

    @property
    def target_price(self):

        if self.target_below:
            new = self.with_high(self.difference)  # TODO:有可能在触及高点前就成交了
            self.latest_target_price = max(self.latest_target_price, new)
        else:
            new = self.with_low(self.difference)  # TODO:有可能在触及高点前就成交了
            self.latest_target_price = min(self.latest_target_price, new)

        return self.latest_target_price
