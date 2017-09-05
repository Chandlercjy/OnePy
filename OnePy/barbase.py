import pandas as pd


class BarBase(object):
    pass


class Current_bar(BarBase):
    def __init__(self):
        self._cur_bar_list = []

    def add_new_bar(self, new_bar):
        "添加新行情，会缓存第n条当前行情，和第n+1条行情，共两条"
        self._cur_bar_list.pop(0) if len(self._cur_bar_list) == 2 else None
        self._cur_bar_list.append(new_bar)

    @property
    def cur_data(self):
        return self._cur_bar_list[0]

    @property
    def next_data(self):
        return self._cur_bar_list[1]

    @property
    def cur_date(self):
        return self._cur_bar_list[0]["date"]

    @property
    def cur_open(self):
        return self._cur_bar_list[0]["open"]

    @property
    def cur_high(self):
        return self._cur_bar_list[0]["high"]

    @property
    def cur_low(self):
        return self._cur_bar_list[0]["low"]

    @property
    def cur_close(self):
        return self._cur_bar_list[0]["close"]

    @property
    def next_date(self):
        return self._cur_bar_list[1]["date"]

    @property
    def next_open(self):
        return self._cur_bar_list[1]["open"]

    @property
    def next_high(self):
        return self._cur_bar_list[1]["high"]

    @property
    def next_low(self):
        return self._cur_bar_list[1]["low"]

    @property
    def next_close(self):
        return self._cur_bar_list[1]["close"]


class Bar(BarBase):
    """
    Bar主要存储所有Feed的OHLC数据，会在onepy.py中整合
    在feed中每次添加new_bar前需先set_insrument，以便识别添加了哪个feed
    """

    def __init__(self, instrument):
        self._bar_dict = {instrument: []}
        self._instrument = instrument
        self._data_name = None  # 用来定义getitem的返回值

    def __getitem__(self, item):
        return self._bar_dict

    def _initialize(self):
        """将数据清空"""
        self._bar_dict = {}

    def _combine_all_feed(self, new_bar_dict):
        """只运行一次，将所有feed整合到一起"""
        self._bar_dict.update(new_bar_dict)

    def __getitem_func(self, given):
        if isinstance(given, slice):
            # do your handling for a slice object:
            start = given.start if given.start is not None else 0
            stop = given.stop if given.stop is not None else len(self.data)

            # 处理切片为负的情况
            length = len(self.data)
            start = length + start if start < 0 else start
            stop = length + stop if stop < 0 else stop
            original_data = self.data[start:stop]  # 格式为[{},{},{}...]
            data = [i[self._data_name] for i in original_data]
            return data
        else:
            # Do your handling for a plain index
            return self._bar_dict[self.instrument][given]["close"]

    def __create_data_cls(self):
        cls = type("OHLC", (), {})
        cls.data = self._bar_dict[self.instrument]
        cls.__getitem__ = self.__getitem_func
        return cls

    def set_instrument(self, instrument):
        self._instrument = instrument

    def add_new_bar(self, new_bar):
        "添加新行情"
        self._bar_dict[self.instrument].append(new_bar)

    @property
    def instrument(self):
        return self._instrument

    @property
    def data(self):
        return self._bar_dict[self.instrument]

    @property
    def total_dict(self):
        return self._bar_dict

    @property
    def df(self):
        return pd.DataFrame(self._bar_dict[self.instrument])

    @property
    def open(self):
        self._data_name = "open"
        cls = self.__create_data_cls()
        return cls()

    @property
    def high(self):
        self._data_name = "high"
        cls = self.__create_data_cls()
        return cls()

    @property
    def low(self):
        self._data_name = "low"
        cls = self.__create_data_cls()
        return cls()

    @property
    def close(self):
        self._data_name = "close"
        cls = self.__create_data_cls()
        return cls()

    @property
    def volume(self):
        self._data_name = "volume"
        cls = self.__create_data_cls()
        return cls()
