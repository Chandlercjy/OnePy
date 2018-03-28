
from OnePy.environment import Environment


class GlobalVariables(object):

    env = Environment()
    """全局变量"""

    def __init__(self):
        self.context = None
        self.tickers = None  # type:list

        self.trading_date = None
        self.calander_date = None

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
        # self.trailingstop_executemode = None


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
