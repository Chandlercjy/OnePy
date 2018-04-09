import abc

from OnePy.environment import Environment
from OnePy.sys_module.components.match_engine import MatchEngine
from OnePy.sys_module.models.base_series import BarSeries


class RecorderBase(metaclass=abc.ABCMeta):
    env = Environment

    def __init__(self):
        self.env.recorders.update({self.__class__.__name__: self})
        self.env.recorder = self
        self.match_engine = MatchEngine()
        self.ohlc = BarSeries()

        self.initial_cash = 100
        self.per_comm = 1
        self.per_comm_pct = None
        self.margin_rate = 0.1

        self.position = None
        self.avg_price = None
        self.holding_pnl = None
        self.realized_pnl = None
        self.commission = None
        self.market_value = None
        self.margin = None

        self.cash = None
        self.frozen_cash = None
        self.balance = None

    @abc.abstractmethod
    def _record_order(self):
        pass

    @abc.abstractmethod
    def run(self):
        pass

    @abc.abstractmethod
    def update(self):
        """根据最新价格更新账户信息"""
        pass
