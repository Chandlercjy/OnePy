import csv
from datetime import datetime

import funcy as fy

from OnePy.barbase import Current_bar
from OnePy.event import events, MarketEvent


class FeedMetabase(object):
    dtformat = "%Y-%m-%d %H:%M:%S"
    tmformat = "%H:%M:%S"
    timeindex = None

    def __init__(self, instrument):
        self.instrument = instrument
        self.cur_bar = Current_bar()
        self.bar_dict = {self.instrument: []}

    def get_new_bar(self):
        pass

    def preload(self):
        pass

    def run_once(self):
        self.get_new_bar()
        self.preload()  # preload for indicator

    def update_bar(self, instrument):
        self.bar_dict[instrument].append(self.cur_bar.cur_data)

    def start(self):
        pass

    def prenext(self):
        self.get_new_bar()

    def next(self):
        self.update_bar(self.instrument)
        events.put(MarketEvent(self))


class FeedBase(FeedMetabase):
    dtformat = "%Y-%m-%d %H:%M:%S"
    tmformat = "%H:%M:%S"
    timeindex = None

    def __init__(self, datapath, instrument,
                 fromdate=None, todate=None):
        super(FeedBase, self).__init__(instrument)
        self.continue_backtest = True

        self.datapath = datapath
        self.fromdate = datetime.strptime(fromdate, "%Y-%m-%d") if fromdate else None  # 先将日期转化为datetime对象
        self.todate = datetime.strptime(todate, "%Y-%m-%d") if todate else None  # 先将日期转化为datetime对象

        self.preload_bar_list = []
        self.iteral_data = self.__load_data()

    def __set_dtformat(self, bar):
        # 目前只设置支持int和str
        date = bar["date"]
        dt = "%Y-%m-%d %H:%M:%S"
        if self.timeindex:
            date = datetime.strptime(str(date), self.dtformat).strftime("%Y-%m-%d")
            return date + " " + bar[self.timeindex.lower()]
        else:
            return datetime.strptime(str(date), self.dtformat).strftime(dt)

    def get_new_bar(self):
        def __update():
            bar = next(self.iteral_data)
            bar = fy.walk_keys(lambda x: x.lower(), bar)
            bar["date"] = self.__set_dtformat(bar)

            for i in bar:
                try:
                    bar[i] = float(bar[i])  # 将数值转化为float
                except ValueError:
                    pass
            return bar

        try:
            bar = __update()
            # 日期范围判断
            dt = "%Y-%m-%d %H:%M:%S"
            if self.fromdate:
                while datetime.strptime(bar["date"], dt) < self.fromdate:
                    bar = __update()
            if self.todate:
                while datetime.strptime(bar["date"], dt) > self.todate:
                    raise StopIteration

            self.cur_bar.add_new_bar(bar)

        except StopIteration:
            self.continue_backtest = False  # stop backtest

    def __load_data(self):
        return csv.DictReader(open(self.datapath))

    def preload(self):
        """
        只需运行一次，先将fromdate前的数据都load到preload_bar_list
        若没有fromdate，则不用load
        """
        self.iteral_buffer = self.__load_data()  # for indicator

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
