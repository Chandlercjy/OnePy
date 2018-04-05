from itertools import count

from dataclasses import dataclass, field

from OnePy.constants import OrderType
from OnePy.environment import Environment


@dataclass
class Signal(object):
    env = Environment

    counter = count(1)

    order_type: OrderType
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
    execute_price: float = None  # 用来确定是否是必成单
    first_cur_price: float = None

    # Trigger only
    mkt_id: float = None
    exec_type: str = None

    id: int = field(init=False)

    def __post_init__(self):
        self.datetime = self.env.feeds[self.ticker].date
        self.id = next(self.counter)
        self.check_all_conflict()
        self.save_signals()

    def save_signals(self):
        self.env.signals_normal_cur.append(self)
        self.env.signals_normal.append(self)

    def check_all_conflict(self):
        self._check_conflict(self.price, self.price_pct)
        self._check_conflict(self.takeprofit, self.takeprofit_pct)
        self._check_conflict(self.stoploss, self.stoploss_pct)
        self._check_conflict(self.trailingstop, self.trailingstop_pct)

    def get(self, name):
        return getattr(self, name)

    def set(self, name, value):
        setattr(self, name, value)

    @staticmethod
    def _check_conflict(obj, obj_pct):
        if obj and obj_pct:
            raise Exception("$ and pct can't be set together")


class SignalByTrigger(Signal):
    counter = count(1)

    def save_signals(self):
        self.env.signals_trigger_cur.append(self)
        self.env.signals_trigger.append(self)

    def make_size_correct(self):
        """调整一下size，因为是反过来"""
        pass


if __name__ == "__main__":
    Signal.env = Environment()
    gg = Signal(1, '000001', 's', 's')
    ff = Signal(2, '555', 's', 's')
    ss = SignalByTrigger(2, '44', 2, 2)
    print(ss.id)
    print(gg.id)
    print(ff.id)
    kk = Signal(2, '555', 's', 's')
    ll = SignalByTrigger(2, '44', 2, 2)
    print(kk.id)
    print(ll.id)
