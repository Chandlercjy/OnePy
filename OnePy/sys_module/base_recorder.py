from OnePy.builtin_module.trade_log.match_engine import MatchEngine
from OnePy.sys_module.metabase_env import OnePyEnvBase


class RecorderBase(OnePyEnvBase):

    def __init__(self, trade_log):
        self.env.recorders.update({self.__class__.__name__: self})
        self.env.recorder = self
        self.match_engine = MatchEngine(trade_log)

        self.initial_cash = 100000
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

    def _record_order(self):
        """记录成交的账单信息，更新账户信息"""
        raise NotImplementedError

    def run(self):
        raise NotImplementedError

    def update(self):
        """根据最新价格更新账户信息"""
        raise NotImplementedError
