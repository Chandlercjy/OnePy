from itertools import count
from typing import Union

from dataclasses import dataclass, field

from OnePy.constants import ActionType, OrderType
from OnePy.sys_module.components.exceptions import (OrderConflictError,
                                                    PctRangeError)
from OnePy.sys_module.metabase_env import OnePyEnvBase


@dataclass
class Signal(OnePyEnvBase):

    counter = count(1)

    strategy_name: str
    action_type: ActionType
    size: int
    ticker: str
    takeprofit: float = None
    takeprofit_pct: float = None
    stoploss: float = None
    stoploss_pct: float = None
    trailingstop: float = None
    trailingstop_pct: float = None
    price: float = None
    price_pct: float = None

    signal_id: int = None
    datetime: str = field(init=False)

    def __post_init__(self):
        self.datetime = self.env.sys_date
        self.next_datetime = self.env.feeds[self.ticker].next_ohlc['date']
        self.signal_id = next(self.counter)
        self._check_all_conflict()
        self._save_signals()

    def _save_signals(self):
        self.env.signals_normal_cur.append(self)

        if self.env.is_save_original:
            self.env.signals_normal.append(self)

    def _check_all_conflict(self):
        self._check_size()
        self._check_conflict(self.price, self.price_pct, name='price')
        self._check_conflict(
            self.takeprofit, self.takeprofit_pct, name='takeprofit')
        self._check_conflict(self.stoploss, self.stoploss_pct, name='stoploss')
        self._check_conflict(
            self.trailingstop, self.trailingstop_pct, name='trailingstop')

    def _check_size(self):
        if self.size <= 0:
            raise Exception("size should be Positive")

    @staticmethod
    def _check_conflict(obj: float, obj_pct: float, name: str):
        if obj and obj_pct:
            raise OrderConflictError("$ and pct can't be set together")

        if obj_pct:
            if not -1 < obj_pct < 1:
                raise PctRangeError("pct should be -1 < pct < 1")

        if name != 'price':
            if obj:
                if obj <= 0:
                    raise ValueError(f"{name.upper()} should be Positive")

            if obj_pct:
                if obj_pct <= 0:
                    raise ValueError(f"{name.upper()} should be Positive")

    def get(self, name: str):
        return getattr(self, name)

    def set(self, name: str, value: float):
        setattr(self, name, value)


@dataclass
class SignalForPending(Signal):
    price: float = None
    price_pct: float = None

    def _save_signals(self):
        self.env.signals_pending_cur.append(self)

        if self.env.is_save_original:
            self.env.signals_pending.append(self)


@dataclass
class SignalByTrigger(SignalForPending):
    counter = count(1)

    order_type: OrderType = None

    mkt_id: int = None
    trigger_key: str = None

    execute_price: float = None  # 用来确定是否是必成单,用于挂单
    first_cur_price: float = None  # 记录挂单信号产生时候的价格
    parent_order: str = None  # 其实不是str，是一个order对象

    def _save_signals(self):
        self.env.signals_trigger_cur.append(self)

        if self.env.is_save_original:
            self.env.signals_trigger.append(self)


@dataclass
class SignalCancelBase(OnePyEnvBase):

    counter = None
    action_type: ActionType

    strategy_name: str
    ticker: str
    long_or_short: str

    def __post_init__(self):
        self.datetime = self.env.sys_date
        self.signal_id = next(self.counter)
        self._check_all_conflict()
        self._save_signals()

    def _save_signals(self):
        self.env.signals_cancel_cur.append(self)

        if self.env.is_save_original:
            self.env.signals_cancel.append(self)

    def _check_all_conflict(self):
        raise NotImplementedError


@dataclass
class SignalCancelTST(SignalCancelBase):
    counter = count(1)

    takeprofit: bool
    stoploss: bool
    trailingstop: bool

    def _check_all_conflict(self):
        pass


@dataclass
class SignalCancelPending(SignalCancelBase):
    counter = count(1)

    below_price: float = None
    above_price: float = None

    def _check_all_conflict(self):
        if self.below_price is not None and self.above_price is not None:
            raise ValueError(f"below and above price can't be set together!")
