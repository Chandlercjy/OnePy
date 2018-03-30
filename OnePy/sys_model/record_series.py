from collections import UserDict, UserList

from OnePy.environment import Environment


class RecordBase(UserList):
    env = Environment()

    def __init__(self, name):
        super().__init__(self)
        self.name = name

    @property
    def latest(self):
        return self.data[-1].values()


class RecordLong(RecordBase):
    pass


class RecordShort(RecordBase):
    pass


class RecordFactory(object):
    env = Environment()

    @classmethod
    def long_and_short(self, name):
        series_dict = SeriesDict()

        print(self.env.feeds)

        for ticker in self.env.feeds:
            series_dict[f'{ticker}_long'] = RecordLong(name)
            series_dict[f'{ticker}_short'] = RecordShort(name)
            print(series_dict)

        return series_dict

    @classmethod
    def long_only(self, name):
        return {name: RecordLong}


class SeriesDict(UserDict):

    def long_latest(self, ticker):
        return self.data[f'{ticker}_long'][-1].values()

    def short_latest(self, ticker):
        return self.data[f'{ticker}_short'][-1].values()
