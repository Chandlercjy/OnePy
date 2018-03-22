import csv

from OnePy.environment import Environment
from OnePy.bar import Bar

class FeedMetabase(object):

    _env = Environment()

    def __init__(self):

        self.data_Buffer = None
        self.ohlc = None
        self.tick_data = None
        self.execute_price = None
        self.feed_list = self._env.feed_list

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

    def load_data(self, *readers):
        for reader in readers:
            self.feed_list.append(reader.load())

    def run_once(self):
        """先load一次，以便cur_bar能够缓存两条数据"""
        self._iteral_data = self.load_data()
        self.get_new_bar()
        self.preload()  # preload for indicator

    def __update_bar(self):
        """更新行情"""
        self.bar.set_instrument(self.ticker)
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

    def __init__(self, datapath, ticker, fromdate=None, todate=None):
        super(CSVFeedBase, self).__init__(ticker, fromdate, todate)

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
            date = datetime.strptime(
                str(date), self.dtformat).strftime("%Y-%m-%d")

            return date + " " + bar[self.timeindex.lower()]
        else:
            return datetime.strptime(str(date), self.dtformat).strftime(dt)


class DataReaderBase(object):

    """负责读取数据"""

    _env = Environment()

    def __init__(self):
        pass


class CSVReader(DataReaderBase):

    def __init__(self,  data_path, ticker, fromdate=None, todate=None):
        super().__init__()
        self.data_path = data_path
        self.ticker = ticker
        self.fromdate = fromdate
        self.todate = todate

    def load(self):
        return csv.DictReader(open(self.data_path))


