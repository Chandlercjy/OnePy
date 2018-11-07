import abc
from itertools import count
from typing import Union

from OnePy.constants import ActionType, OrderStatus, OrderType
from OnePy.sys_module.metabase_env import OnePyEnvBase
from OnePy.sys_module.models.signals import (Signal, SignalByTrigger,
                                             SignalCancelBase)


class OrderBase(OnePyEnvBase, abc.ABC):
    _action_type: ActionType = None
    order_type: OrderType = None

    counter = count(1)

    def __init__(self, signal: Signal, mkt_id: int) -> None:
        self.signal: Signal = signal
        self.strategy_name = signal.strategy_name
        self.ticker: str = signal.ticker
        self.size: int = signal.size

        self.order_id: int = next(self.counter)
        self.mkt_id: int = mkt_id
        self.first_cur_price: float = self._get_first_cur_price()  # 记录订单发生时刻的现价

        self.status = OrderStatus.Created  # type:OrderStatus
        self.trading_date = self.signal.datetime
        self._status: OrderStatus = None

    def _get_first_cur_price(self) -> float:
        if isinstance(self.signal, SignalByTrigger):
            return self.signal.execute_price

        return self.env.feeds[self.ticker].execute_price

    @abc.abstractproperty
    def action_type(self) -> ActionType:
        raise NotImplementedError

    @abc.abstractproperty
    def status(self) -> OrderStatus:
        raise NotImplementedError

    @status.setter
    def status(self, value: OrderStatus) -> None:
        self._status = value
        raise NotImplementedError


class PendingOrderBase(OrderBase):

    def __init__(self, signal: Signal, mkt_id: int, trigger_key: str) -> None:
        self.trigger_key = trigger_key
        super().__init__(signal, mkt_id)
        self.trading_date = self.env.feeds[signal.ticker].next_ohlc['date']

    @property
    def action_type(self) -> ActionType:
        return self._action_type

    @property
    def status(self) -> OrderStatus:
        return self._status

    @status.setter
    def status(self, value: OrderStatus):
        self._status = value

        self.env.logger.info(
            f'{self.signal.datetime}, '
            f'{self.ticker}, '
            f'{self.order_type.value} '
            f'{self.action_type.value} '
            f'@ {self.target_price:.5f}, '
            f'{self.status.value}, '
            f'size: {self.size}')

    def target_below(self) -> bool:
        raise NotImplementedError

    @property
    def cur_high(self) -> float:
        return self.env.feeds[self.ticker].high

    @property
    def cur_low(self) -> float:
        return self.env.feeds[self.ticker].low

    @property
    def money(self) -> float:
        return getattr(self.signal, self.trigger_key)

    @property
    def pct(self) -> Union[float, bool]:
        if 'pct' in self.trigger_key:
            return getattr(self.signal, self.trigger_key)

        return False

    @property
    def difference(self) -> float:
        if 'pct' in self.trigger_key:
            return abs(self.pct*self.first_cur_price)

        return abs(self.money/self.size)

    @property
    def target_price(self) -> float:
        if self.trigger_key == 'price':
            return self.signal.price
        elif self.target_below:
            return self.below_price(self.difference)

        return self.above_price(self.difference)

    @property
    def is_triggered(self) -> bool:
        if self.target_below:
            return self.cur_low_cross_target_price()

        return self.cur_high_cross_target_price()

    def cur_high_cross_target_price(self) -> bool:
        return True if self.target_price < self.cur_high else False

    def cur_low_cross_target_price(self) -> bool:
        return True if self.target_price > self.cur_low else False

    def is_with_mkt(self) -> bool:
        return False if self.trigger_key == 'price' else True

    def below_price(self, diff) -> float:
        return self.first_cur_price - diff

    def above_price(self, diff) -> float:
        return self.first_cur_price + diff


class TrailingOrderBase(PendingOrderBase):

    def __init__(self, signal: Signal, mkt_id: int, trigger_key: str) -> None:
        super().__init__(signal, mkt_id, trigger_key)
        self.latest_target_price = self.initialize_latest_target_price()

    @property
    def status(self) -> OrderStatus:
        return self._status

    @status.setter
    def status(self, value: OrderStatus):
        self._status = value
        self.env.logger.info(
            f'{self.signal.datetime}, '
            f'{self.ticker}, '
            f'{self.order_type.value} '
            f'{self.action_type.value} '
            f'{self.status.value}, '
            f'size: {self.size}')

    @property
    def cur_open(self) -> float:
        return self.env.feeds[self.ticker].open

    def initialize_latest_target_price(self):
        if self.target_below:
            return self.first_cur_price - self.difference

        return self.first_cur_price + self.difference

    def target_below(self) -> bool:
        raise NotImplementedError

    @property
    def target_price(self) -> float:
        if self.env.instrument == 'A_shares':  # A股要做跳高跳空成交处理
            if self.target_below and self.cur_open < self.latest_target_price:
                return self.cur_open
            elif not self.target_below and self.cur_open > self.latest_target_price:
                return self.cur_open

        return self.latest_target_price  # 外汇不需要，因为这种订单类型

    @property
    def is_triggered(self) -> bool:
        if self.target_below:
            if self.cur_low_cross_target_price():
                return True
            else:
                if self.action_type == ActionType.Sell:
                    new = self.cur_open - self.difference  # 悲观
                else:
                    new = self.cur_high - self.difference  # 悲观

                self.latest_target_price = max(self.latest_target_price, new)

                return False
        else:
            if self.cur_high_cross_target_price():
                return True
            else:
                if self.action_type == ActionType.Sell:
                    new = self.cur_low + self.difference  # 悲观
                else:
                    new = self.cur_open + self.difference  # 悲观
                self.latest_target_price = min(self.latest_target_price, new)

                return False

    def cur_high_cross_target_price(self) -> bool:
        return True if self.latest_target_price < self.cur_high else False

    def cur_low_cross_target_price(self) -> bool:
        return True if self.latest_target_price > self.cur_low else False


class CancelOrderBase(OnePyEnvBase):

    counter = count(1)

    def __init__(self, signal: SignalCancelBase) -> None:
        self.signal: Signal = signal
        self.strategy_name = signal.strategy_name
        self.ticker: str = signal.ticker
        self.long_or_short = signal.long_or_short
        self.order_id: int = next(self.counter)
        self.first_cur_price: float = self._get_first_cur_price()  # 记录订单发生时刻的现价
        self.trading_date = self.signal.datetime
        self.action_type = signal.action_type
        self._status = OrderStatus.Created  # type:OrderStatus

    def _get_first_cur_price(self) -> float:
        return self.env.feeds[self.ticker].execute_price

    @property
    def status(self) -> OrderStatus:
        return self._status

    @status.setter
    def status(self, value: OrderStatus) -> None:
        self._status = value
        self.env.logger.info(
            f'{self.signal.datetime}, '
            f'{self.ticker}, '
            f'{self.long_or_short} '
            f'{self.action_type.value} '
            f'{self.status.value}, '
        )
