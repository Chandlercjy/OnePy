import pandas as pd
import numpy as np


class DataSeriesBase(object):
    _name = None  # 后面必须先设置
    _instrument = None

    def __init__(self):
        self._dict = {}

    def __getitem__(self, key):
        return self._dict[self._instrument][key][self._name]

    def initialize(self, instrument, initial):
        self._dict[instrument] = [{'date': 'start', self._name: initial}]  # 初始化数据没用，后面调用的时候都会忽略

    def set_instrument(self, instrument):
        self._instrument = instrument

    def add(self, date, val):
        self._dict[self._instrument].append({'date': date, self._name: val})

    @property
    def dict(self):
        return self._dict[self._instrument]

    @property
    def keys(self):
        return self._dict.keys()

    @property
    def date(self):
        return [i['date'] for i in self._dict[self._instrument]]

    @property
    def list(self):
        return [i[self._name] for i in self._dict[self._instrument]]

    @property
    def df(self):
        df = pd.DataFrame(self._dict[self._instrument][1:])
        df.set_index('date', inplace=True)
        df.index = pd.DatetimeIndex(df.index)
        return df

    @property
    def series(self):
        return self.df[self._name]

    @property
    def array(self):
        return np.array(self.list)

    @property
    def total_dict(self):
        return self._dict

    def plot(self):
        self.df.plot()

    def del_last(self):
        self._dict[self._instrument].pop(-2)

    def copy_last(self, new_date):
        self._dict[self._instrument].append(self._dict[self._instrument][-1])
        self._dict[self._instrument][-1]['date'] = new_date

    def total(self, key=-1, name=None):
        """全部instrument合起来的value"""
        if name is None:
            name = self._name
        value = 0
        for i in self._dict.values():
            value += i[key][name]
        return value


class PositionSeries(DataSeriesBase):
    _name = 'position'


class MarginSeries(DataSeriesBase):
    _name = 'margin'


class Avg_priceSeries(DataSeriesBase):
    _name = 'avg_price'


class RealizedPLSeries(DataSeriesBase):
    _name = 'realizedPL'

    def update_cur(self, realizedPL):
        self._dict[self._instrument][-1]['realizedPL'] = realizedPL


class CommissionSeries(DataSeriesBase):
    _name = 'commission'


class CashSeries(DataSeriesBase):
    _name = 'cash'
    _instrument = 'all'


class UnrealizedPLSeries(DataSeriesBase):
    _name = 'unrealizedPL'

    def initialize(self, instrument, initial):
        self._dict[instrument] = [{'date': 'start',
                                   self._name: initial,
                                   'unrealizedPL_high': initial,
                                   'unrealizedPL_low': initial}]  # 初始化数据没用，后面调用的时候都会忽略

    def add(self, date, unrealizedPL, unrealizedPL_high, unrealizedPL_low):
        self._dict[self._instrument].append({'date': date,
                                             self._name: unrealizedPL,
                                             'unrealizedPL_high': unrealizedPL_high,
                                             'unrealizedPL_low': unrealizedPL_low})

    @property
    def high(self):
        return [i['unrealizedPL_high'] for i in self._dict[self._instrument]]

    @property
    def low(self):
        return [i['unrealizedPL_low'] for i in self._dict[self._instrument]]

    def total_high(self, key=-1):
        return self.total(key, 'unrealizedPL_high')

    def total_low(self, key=-1):
        return self.total(key, 'unrealizedPL_low')


class BalanceSeries(DataSeriesBase):
    _name = 'balance'
    _instrument = 'all'

    def initialize(self, instrument, initial):
        self._dict[self._instrument] = [{'date': 'start',
                                         self._name: initial,
                                         'balance_high': initial,
                                         'balance_low': initial}]  # 初始化数据没用，后面调用的时候都会忽略

    def add(self, date, balance, balance_high, balance_low):
        self._dict[self._instrument].append({'date': date,
                                             self._name: balance,
                                             'balance_high': balance_high,
                                             'balance_low': balance_low})

    @property
    def high(self):
        return [i['balance_high'] for i in self._dict[self._instrument]]

    @property
    def low(self):
        return [i['balance_low'] for i in self._dict[self._instrument]]
