
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


class Context(object):

    def __init__(self):
        self.fromdate = None
        self.todate = None


class TickerSettingBase(object):

    """表示跟随每一个Ticker的配置信息,只有在recorder中才用用到"""

    def __init__(self, ticker):

        self.ticker = ticker
        self.per_comm = None
        self.commtype = Commission()
        self.leverage = None
        self.per_margin = None


class Commission(object):

    """主要分为固定$和百分比%"""

    def __init__(self, fixed_or_percentage):
        self._fixed_or_percentage = fixed_or_percentage


class StockSetting(TickerSettingBase):

    """Docstring for StockSetting. """

    def __init__(self, ticker):
        super().__init__(self, ticker)


class DataBuffer(object):

    """用于与读取数据，便与恢复状态或计算指标"""

    def __init__(self):
        pass
