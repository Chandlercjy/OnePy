import datetime
import os, os.path
import pandas as pd

from abc import ABCMeta, abstractmethod
from event import MarketEvent,events

class DataHandler(object):

    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def get_latest_bars(self, symbol, N=1):
        raise NotImplementedError("Should implement get_latest_bars()")

    @abstractmethod
    def update_bars(self):
        raise NotImplementedError("Should implement update_bars()")

class csv_reader(DataHandler):
    def __init__(self, csv_path, symbol_list, start=None, end=None, caps=False):
        """
        csv_path: if /Users/csv/xxx.csv, just set csv_path = /User/csv
        symbol_list: put csv file name in a list, like ['xxx']
        start: 'Y-m-d', such as '2017-01-01', default to read all
        end: 'Y-m-d', such as '2017-01-01', default to read all
        caps: if True, csv.columns = ['Open,High,Low,Close,Volume,Adj Close']
              if False, csv.columns = ['open,high,low,close,volume']
            Attention! True will automatically set 'adj_close' to  override 'close'
        """

        self.csv_path = csv_path
        self.start = start
        self.end = end
        self.caps = caps

        # OHLC
        if self.caps:
            self.open = 'Open'
            self.high = 'High'
            self.low = 'Low'
            self.close = 'Adj Close'
            self.volume = 'Volume'
        else:
            self.open = 'open'
            self.high = 'high'
            self.low = 'low'
            self.close = 'close'
            self.volume = 'volume'

        self.symbol_list = symbol_list  # stock code list

        self.symbol_dict = {}   # a dict contain DataFrames
        self.latest_bar_dict = {}


        self.continue_backtest = True

        self._open_convert_csv_files()

        self.roll_data = {}  # for generator

    def _open_convert_csv_files(self):
        comb_index = None
        for s in self.symbol_list:
            # Load the CSV and set index to Datatime
            symbol_data = pd.read_csv(os.path.join(self.csv_path,'%s.csv' % s),
                                      parse_dates=True, index_col=0)

            self.symbol_dict[s] = symbol_data.loc[self.start:self.end]

        # Combine the index to pad forward values, depreciated for now!!!
            if comb_index is None:
                comb_index = self.symbol_dict[s].index
            else:
                comb_index = comb_index.union(self.symbol_dict[s].index)

        # Create and Set the lates symbol_dict to None
            self.latest_bar_dict[s] = []

        # Reindex the DataFrames, depreciated for now!!!
            self.symbol_dict[s] = self.symbol_dict[s].reindex(
                                        index=comb_index,method='pad')

    def _get_new_bar(self, symbol):
        """
        Returns the latest bar from the data feed as a tuple of
        (sybmbol, datetime, open, low, high, close, volume, code).

        yield also create a generator
        """
        df = self.symbol_dict[symbol]
        lenth = len(df)
        for i in range(lenth):
            yield ({'symbol':symbol, 'date':str(df.index[i]),
                    'open':df[[self.open]].iat[i,0],
                    'low':df[[self.low]].iat[i,0],
                    'high':df[[self.high]].iat[i,0],
                    'close':df[[self.close]].iat[i,0],
                    'volume':df[[self.volume]].iat[i,0]})

    def get_latest_bars(self, symbol, N=1):
        try:
            bars_list = self.latest_bar_dict[symbol]
        except KeyError:
            print "That symbol is not available in the historical data set."
        else:
            return bars_list[-N:]

    def convert_to_df(self,latest_bar):
        d = latest_bar[0]
        df = pd.DataFrame(d, index=[0])
        df.reset_index(drop=True, inplace=True)
        df['date']=pd.DatetimeIndex(df['date'])
        df.set_index('date',inplace=True)
        return df

    def update_bars(self):
        """
        Everytime update, update bar from the 0 row for every symbol
        run strategy one by one for all symbol,
        need a event loop
        and finally fullfill the latest_bar_dict
        """
        for s in self.symbol_list:
            if self.latest_bar_dict[s] == [] :
                self.roll_data[s] = self._get_new_bar(s)
            try:
                bar = self.roll_data[s].next()

            except StopIteration:
                self.continue_backtest = False
            else:
                if bar is not None:
                    self.latest_bar_dict[s].append(bar)

        events.put(MarketEvent())

class DataFrame_reader(DataHandler):
    def __init__(self, df, symbol_list, start=None, end=None, caps=False):

        self.df = df
        self.start = start
        self.end = end
        self.symbol_list = symbol_list  # stock code list
        self.caps = caps

        # OHLC
        if self.caps:
            self.open = 'Open'
            self.high = 'High'
            self.low = 'Low'
            self.close = 'Close'
            self.volume = 'Volume'
        else:
            self.open = 'open'
            self.high = 'high'
            self.low = 'low'
            self.close = 'close'
            self.volume = 'volume'

        self.symbol_dict = {}   # a dict contain DataFrames
        self.latest_bar_dict = {}


        self.continue_backtest = True

        self._open_convert_csv_files()

        self.roll_data = {}  # for generator

    def _open_convert_csv_files(self):
        comb_index = None
        for s in self.symbol_list:
            # Load the CSV and set index to Datatime
            symbol_data = self.df
            self.symbol_dict[s] = symbol_data.loc[self.start:self.end]

        # Combine the index to pad forward values, depreciated for now!!!
            if comb_index is None:
                comb_index = self.symbol_dict[s].index
            else:
                comb_index = comb_index.union(self.symbol_dict[s].index)

        # Create and Set the lates symbol_dict to None
            self.latest_bar_dict[s] = []


        # Reindex the DataFrames, depreciated for now!!!
            self.symbol_dict[s] = self.symbol_dict[s].reindex(
                                        index=comb_index,method='pad')

    def _get_new_bar(self, symbol):
        """
        Returns the latest bar from the data feed as a tuple of
        (sybmbol, datetime, open, low, high, close, volume, code).

        yield also create a generator
        """
        df = self.symbol_dict[symbol]
        lenth = len(df)
        for i in range(lenth):
            yield ({'symbol':symbol, 'date':str(df.index[i]),
                    'open':df[[self.open]].iat[i,0],
                    'low':df[[self.low]].iat[i,0],
                    'high':df[[self.high]].iat[i,0],
                    'close':df[[self.close]].iat[i,0],
                    'volume':df[[self.volume]].iat[i,0]})

    def get_latest_bars(self, symbol, N=1):
        try:
            bars_list = self.latest_bar_dict[symbol]
        except KeyError:
            print "That symbol is not available in the historical data set."
        else:
            return bars_list[-N:]

    def convert_to_df(self,latest_bar):
        d = latest_bar[0]
        df = pd.DataFrame(d, index=[0])
        df.reset_index(drop=True, inplace=True)
        df['date']=pd.DatetimeIndex(df['date'])
        df.set_index('date',inplace=True)
        return df

    def update_bars(self):
        """
        Everytime update, update bar from the 0 row for every symbol
        run strategy one by one for all symbol,
        need a event loop
        and finally fullfill the latest_bar_dict
        """
        for s in self.symbol_list:
            if self.latest_bar_dict[s] == [] :
                self.roll_data[s] = self._get_new_bar(s)
            try:
                bar = self.roll_data[s].next()

            except StopIteration:
                self.continue_backtest = False
            else:
                if bar is not None:
                    self.latest_bar_dict[s].append(bar)

        events.put(MarketEvent())
