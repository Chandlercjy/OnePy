
from OnePy.environment import Environment
from OnePy.utils.clean import make_it_datetime, make_it_float


class Bar(object):
    env = None  # type:Environment

    def __init__(self, reader):
        self._iter_data = reader.load()
        self.current_ohlc = None
        self.next_ohlc = next(self._iter_data)

    def next(self):
        self.current_ohlc, self.next_ohlc = self.next_ohlc, next(
            self._iter_data)

    @property
    def execute_price(self):
        if self.env.execute_on_close_or_next_open is 'open':
            return self.next_ohlc['open']

        return self.close

    @property
    def cur_price(self):
        return self.close

    @property  # type: ignore
    @make_it_datetime
    def date(self):
        return self.current_ohlc['date']

    @property  # type: ignore
    @make_it_float
    def open(self):
        return self.current_ohlc['open']

    @property  # type: ignore
    @make_it_float
    def high(self):
        return self.current_ohlc['high']

    @property  # type: ignore
    @make_it_float
    def low(self):
        return self.current_ohlc['low']

    @property  # type: ignore
    @make_it_float
    def close(self):
        return self.current_ohlc['close']

    @property  # type: ignore
    @make_it_float
    def volume(self):
        return self.current_ohlc['volume']


# class Bsar(Bar):
    # """
    # Bar主要存储所有Feed的OHLC数据，会在onepy.py中整合
    # 在feed中每次添加new_bar前需先set_insrument，以便识别添加了哪个feed
    # """

    # def __init__(self, instrument):
        # self._bar_dict = {instrument: []}
        # self._instrument = instrument
        # self._data_name = None  # 用来定义getitem的返回值

    # def __getitem__(self, item):
        # return self._bar_dict

    # def _initialize(self):
        # """将数据清空"""
        # self._bar_dict = {}

    # def _combine_all_feed(self, new_bar_dict):
        # """只运行一次，将所有feed整合到一起"""
        # self._bar_dict.update(new_bar_dict)

    # def __getitem_func(self, given):
        # if isinstance(given, slice):
        # # do your handling for a slice object:
        # stop = given.stop if given.stop is not None else len(self.data)

        # # 处理切片为负的情况
        # length = len(self.data)
        # start = length + start if start < 0 else start
        # stop = length + stop if stop < 0 else stop
        # original_data = self.data[start:stop]  # 格式为[{},{},{}...]
        # data = [i[self._data_name] for i in original_data]

        # return data
    # else:
        # # Do your handling for a plain index

        # return self._bar_dict[self.instrument][given]["close"]

    # def __create_data_cls(self):
        # cls = type("OHLC", (), {})
        # cls.data = self._bar_dict[self.instrument]
        # cls.__getitem__ = self.__getitem_func

        # return cls

    # def set_instrument(self, instrument):
        # self._instrument = instrument

    # def add_new_bar(self, new_bar):
        # "添加新行情"
        # self._bar_dict[self.instrument].append(new_bar)

    # def instrument(self):
        # return self._instrument

    # def data(self):
        # return self._bar_dict[self.instrument]

    # def total_dict(self):
        # return self._bar_dict

    # def df(self):
        # return pd.DataFrame(self._bar_dict[self.instrument])

    # def open(self):
        # self._data_name = "open"
        # cls = self.__create_data_cls()

        # return cls()

    # def high(self):
        # self._data_name = "high"
        # cls = self.__create_data_cls()

        # return cls()

    # def low(self):
        # self._data_name = "low"
        # cls = self.__create_data_cls()

        # return cls()

    # def close(self):
        # self._data_name = "close"
        # cls = self.__create_data_cls()

        # return cls()

    # def volume(self):
        # self._data_name = "volume"
        # cls = self.__create_data_cls()

        # return cls()
