from itertools import count

from dataclasses import dataclass, field

from OnePy.constants import ExecType
from OnePy.sys_module.components.exceptions import (OrderConflictError,
                                                    PctRangeError)
from OnePy.sys_module.metabase_env import OnePyEnvBase


@dataclass
class Signal(OnePyEnvBase):

    counter = count(1)

    size: int
    ticker: str
    datetime: str = None
    takeprofit: float = None
    takeprofit_pct: float = None
    stoploss: float = None
    stoploss_pct: float = None
    trailingstop: float = None
    trailingstop_pct: float = None
    price: float = None
    price_pct: float = None
    execute_price: float = None  # 用来确定是否是必成单,用于挂单
    first_cur_price: float = None

    action_type: str = None
    order_type: str = None
    mkt_id: float = None
    signal_id: int = field(init=False)

    def __post_init__(self):
        self.datetime = self.env.trading_datetime
        self.signal_id = next(self.counter)
        self._check_all_conflict()
        self._save_signals()

    def _save_signals(self):
        self.env.signals_normal_cur.append(self)
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
    def _check_conflict(obj, obj_pct, name):
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

    def is_absolute_signal(self):
        return True if self.execute_price else False

    def get(self, name):
        return getattr(self, name)

    def set(self, name, value):
        setattr(self, name, value)


@dataclass
class SignalByTrigger(Signal):
    counter = count(1)

    exec_type: str = None
    trigger_key: str = None

    def _save_signals(self):
        self.env.signals_trigger_cur.append(self)
        self.env.signals_trigger.append(self)
