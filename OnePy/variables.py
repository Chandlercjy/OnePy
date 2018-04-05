from collections import defaultdict

from OnePy.environment import Environment


class GlobalVariables(object):

    env = Environment
    """全局变量"""

    def __init__(self):
        self.context = None

        # Portfolio
        self.frozen_cash = None
        self.total_returns = None
        self.daily_returns = None
        self.margin = None
        self.avg_price = None
        self.daily_pnl = None
        self.holding_pnl = None
        self.realized_pnl = None
        self.total_value = None
        self.transaction_cost = None
        self.buy_margin = None
        self.sell_margin = None

        self.trading_date = None
        self.last_trading_date = None

    @property
    def start_date(self):
        return None

    @property
    def calendar_date(self):
        return self.trading_date.format("YYYY-MM-DD")

    @property
    def cash(self):
        return self.env.recorder.cash

    @property
    def position(self):
        return self.env.recorder.position

    @property
    def feed(self):
        return self.env.feeds
