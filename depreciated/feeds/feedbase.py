from abc import abstractmethod, ABCMeta

import csv
from datetime import datetime

import funcy as fy

from OnePy.barbase import Current_bar, Bar
from OnePy.event import events, MarketEvent


class FeedMetabase(metaclass=ABCMeta):
    dtformat = "%Y-%m-%d %H:%M:%S"
    tmformat = "%H:%M:%S"
    timeindex = None

    def __init__(self, instrument, fromdate, todate):
        self.instrument = instrument
        self.fromdate = fromdate
        self.todate = todate

        self.cur_bar = Current_bar()
        # self.bar_dict = {self.instrument: []}
        self.bar = Bar(instrument)
        self.preload_bar_list = []
        self.continue_backtest = True

        # 以下变量会被初始化
        self._per_comm = None
        self._commtype = None
        self._mult = None
        self._per_margin = None
        self._executemode = None
        self._trailingstop_executemode = None

        self._iteral_buffer = None
        self._buffer_days = None
        self._iteral_data = None

    def set_per_comm(self, value):
        self._per_comm = value

    def set_commtype(self, value):
        self._commtype = value

    def set_mult(self, value):
        self._mult = value

    def set_per_margin(self, value):
        self._per_margin = value

    def set_executemode(self, value):
        self._executemode = value

    def set_trailingstop_executemode(self, value):
        self._trailingstop_executemode = value

    def set_iteral_buffer(self, value):
        self._iteral_buffer = value

    def set_buffer_days(self, value):
        self._buffer_days = value

    @property
    def per_comm(self):
        return self._per_comm

    @property
    def commtype(self):
        return self._commtype

    @property
    def mult(self):
        return self._mult

    @property
    def per_margin(self):
        return self._per_margin

    @property
    def executemode(self):
        return self._executemode

    @property
    def trailingstop_executemode(self):
        return self._trailingstop_executemode

    @property
    def iteral_buffer(self):
        return self._iteral_buffer

    @property
    def buffer_days(self):
        return self._buffer_days

    @abstractmethod
    def load_data(self):
        """读取数据"""
        raise NotImplementedError("load_data shold be overrided")

    @abstractmethod
    def get_new_bar(self):
        """获得新行情"""
        raise NotImplementedError("get_new_bar shold be overrided")

    @abstractmethod
    def preload(self):
        """为indicator缓存数据"""
        raise NotImplementedError("preload shold be overrided")

    def run_once(self):
        """先load一次，以便cur_bar能够缓存两条数据"""
        self._iteral_data = self.load_data()
        self.get_new_bar()
        self.preload()  # preload for indicator

    def __update_bar(self):
        """更新行情"""
        self.bar.set_instrument(self.instrument)
        self.bar.add_new_bar(self.cur_bar.cur_data)

    def start(self):
        pass

    def prenext(self):
        self.get_new_bar()

    def next(self):
        self.__update_bar()
        events.put(MarketEvent(self))


class CSVFeedBase(FeedMetabase):
    """自动识别CSV数据中有open，high，low，close，volume数据，但要说明日期格式"""
    dtformat = "%Y-%m-%d %H:%M:%S"
    tmformat = "%H:%M:%S"
    timeindex = None

    def __init__(self, datapath, instrument, fromdate=None, todate=None):
        super(CSVFeedBase, self).__init__(instrument, fromdate, todate)

        self.datapath = datapath
        self.__set_date()

    def __set_date(self):
        """将日期转化为datetime对象"""
        if self.fromdate:
            self.fromdate = datetime.strptime(self.fromdate, "%Y-%m-%d")
        if self.todate:
            self.todate = datetime.strptime(self.todate, "%Y-%m-%d")

    def __set_dtformat(self, bar):
        """识别日期"""
        date = bar["date"]
        dt = "%Y-%m-%d %H:%M:%S"
        if self.timeindex:
            date = datetime.strptime(str(date), self.dtformat).strftime("%Y-%m-%d")
            return date + " " + bar[self.timeindex.lower()]
        else:
            return datetime.strptime(str(date), self.dtformat).strftime(dt)

    def get_new_bar(self):
        def __update():
            new_bar = next(self._iteral_data)
            new_bar = fy.walk_keys(lambda x: x.lower(), new_bar)
            new_bar["date"] = self.__set_dtformat(new_bar)

            for i in new_bar:
                try:
                    new_bar[i] = float(new_bar[i])  # 将数值转化为float
                except ValueError:
                    pass
            return new_bar

        try:
            new_bar = __update()
            # 日期范围判断
            dt = "%Y-%m-%d %H:%M:%S"
            if self.fromdate:
                while datetime.strptime(new_bar["date"], dt) < self.fromdate:
                    new_bar = __update()
            if self.todate:
                while datetime.strptime(new_bar["date"], dt) > self.todate:
                    raise StopIteration

            self.cur_bar.add_new_bar(new_bar)

        except StopIteration:
            self.continue_backtest = False  # stop backtest

    def load_data(self):
        return csv.DictReader(open(self.datapath))

    def preload(self):
        """
        只需运行一次，先将fromdate前的数据都load到preload_bar_list
        若没有fromdate，则不用load
        """
        self.set_iteral_buffer(self.load_data())  # for indicator

        def _update():
            bar = next(self.iteral_buffer)
            bar = fy.walk_keys(lambda x: x.lower(), bar)
            bar["date"] = self.__set_dtformat(bar)

            for i in bar:
                try:
                    bar[i] = float(bar[i])  # 将数值转化为float
                except ValueError:
                    pass
            return bar

        try:
            bar = _update()
            # 日期范围判断
            dt = "%Y-%m-%d %H:%M:%S"
            if self.fromdate:
                while datetime.strptime(bar["date"], dt) < self.fromdate:
                    bar = _update()
                    self.preload_bar_list.append(bar)
                else:
                    self.preload_bar_list.pop(-1)  # 经过验证bug检查的，最后删除掉一个重复

            elif self.fromdate is None:
                pass
            else:
                raise SyntaxError("Catch a Bug!")

        except IndexError:
            pass

        except StopIteration:
            print("???")

        self.preload_bar_list.reverse()
