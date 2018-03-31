from collections import UserDict, UserList

from OnePy.environment import Environment


class RecordBase(UserList):
    env = Environment

    def __init__(self, name):
        super().__init__(self)
        self.name = name
        self.data.append({'date': 'start', 'value': 0})

    @property
    def latest(self):
        return self.data[-1]['value']


class RecordLong(RecordBase):
    pass


class RecordShort(RecordBase):
    pass


class RecordFactory(object):
    env = Environment

    @classmethod
    def long_and_short(self, name):
        series_dict = SeriesDict()

        for ticker in self.env.feeds:
            series_dict[f'{ticker}_long'] = RecordLong(name)
            series_dict[f'{ticker}_short'] = RecordShort(name)

        return series_dict

    @classmethod
    def long_only(self, name, initial_cash):
        series = RecordLong(name)
        series[0]['value'] = initial_cash

        return series


class SeriesDict(UserDict):

    def latest_long(self, ticker):
        return self.data[f'{ticker}_long'][-1]['value']

    def latest_short(self, ticker):
        return self.data[f'{ticker}_short'][-1]['value']

    def append_long(self, ticker, trading_date,  value):
        self.data[f'{ticker}_long'].append(
            {'date': trading_date, 'value': value})

    def append_short(self, ticker, trading_date,  value):
        self.data[f'{ticker}_short'].append(
            {'date': trading_date, 'value': value})

    def total_value(self):
        total = 0

        for data_list in self.data.values():
            per_dict = data_list[-1]
            total += per_dict['value']

        return total
