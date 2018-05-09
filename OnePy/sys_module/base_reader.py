
from OnePy.sys_module.metabase_env import OnePyEnvBase


class DataReaderBase(OnePyEnvBase):

    """负责读取数据"""

    def __init__(self, ticker, fromdate=None, todate=None):
        self.ticker = ticker
        self.fromdate = fromdate
        self.todate = todate

        self.env.readers[self.ticker] = self
        self.env.fromdate = fromdate
        self.env.todate = todate

        self.margin_per_lot = None
        self.dollar_per_pips = None

    def load(self, fromdate=None, todate=None):
        """需要返回已过滤好的从fromdate开始的数据,cleander需要用"""
        raise NotImplementedError

    def get_bar(self):
        raise NotImplementedError
