from collections import UserDict, UserList

from OnePy.environment import Environment


class RecordBase(UserList):
    env = Environment

    def __init__(self, name):
        super().__init__(self)
        self.name = name
        self.data.append({'start_date': 0})

    @property
    def latest(self):
        return list(self.data[-1].values())[-1]


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
        series[0]['start_date'] = initial_cash
        return series


class SeriesDict(UserDict):

    def latest_long(self, order):
        return list(self.data[f'{order.ticker}_long'][-1].values())[0]

    def latest_short(self, order):
        return list(self.data[f'{order.ticker}_short'][-1].values())[0]

    def append_long(self, order, value):
        self.data[f'{order.ticker}_long'].append(
            {order.trading_date: value})

    def append_short(self, order, value):
        self.data[f'{order.ticker}_short'].append(
            {order.trading_date: value})

    def total_value(self):
        total = 0

        for data_list in self.data.values():
            per_dict = data_list[-1]
            total += list(per_dict.values())[0]

        return total
