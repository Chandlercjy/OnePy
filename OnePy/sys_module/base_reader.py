import abc

from OnePy.environment import Environment


class DataReaderBase(metaclass=abc.ABCMeta):

    """负责读取数据"""

    env = Environment

    def __init__(self, ticker, fromdate=None, todate=None):
        self.ticker = ticker
        self.fromdate = fromdate
        self.todate = todate

        self.env.readers[self.ticker] = self
        self.env.tickers.append(ticker)
        self.env.fromdate = fromdate
        self.env.todate = todate

    @abc.abstractmethod
    def load(self, fromdate=None, todate=None):
        """需要返回已过滤好的从fromdate开始的数据"""
        pass

    @abc.abstractmethod
    def get_bar(self):
        pass
