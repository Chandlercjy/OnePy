from collections import defaultdict

from OnePy.environment import Environment
from OnePy.sys_module.models.base_series import BarSeries


class GlobalVariables(object):

    env = Environment
    """全局变量"""

    def __init__(self):
        self.ohlc = BarSeries()

    @property
    def trading_datetime(self):
        return self.env.feeds[self.env.tickers[0]].date

    @property
    def position(self):
        return self.env.recorder.position

    @property
    def avg_price(self):
        return self.env.recorder.avg_price

    @property
    def holding_pnl(self):
        return self.env.recorder.holding_pnl

    @property
    def commission(self):
        return self.env.recorder.commission

    @property
    def market_value(self):
        return self.env.recorder.market_value

    @property
    def margin(self):
        return self.env.recorder.margin

    @property
    def frozen_cash(self):
        return self.env.recorder.frozen_cash

    @property
    def cash(self):
        return self.env.recorder.cash

    @property
    def balance(self):
        return self.env.recorder.balance
