import csv

from OnePy.event import EVENT, Event
from OnePy.model.bar import Bar


class MarketMaker(object):

    env = None
    gvar = None

    def __init__(self):

        self.data_Buffer = None
        self.ohlc = None
        self.tick_data = None
        self.execute_price = None

    def update_market(self):
        try:
            for bar in self.env.feeds.values():
                bar.next()

            return True
        except StopIteration:
            return False


class DataReaderBase(object):

    """负责读取数据"""

    env = None

    def __init__(self, ticker, fromdate=None, todate=None):
        self.ticker = ticker
        self.fromdate = fromdate
        self.todate = todate
        self.env.readers[self.ticker] = self
