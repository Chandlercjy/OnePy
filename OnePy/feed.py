#coding=utf8
import csv
import funcy as fy

from datetime import datetime

from .event import events, MarketEvent


class FeedBase(object):

    dtformat = '%Y-%m-%d %H:%M:%S'
    tmformat = '%H:%M:%S'
    timeindex = None

    def __init__(self,datapath,instrument,
                        fromdate=None,todate=None,timeframe=None):
        self.live_mode = False
        self.continue_backtest = True

        self.datapath = datapath
        self.instrument = instrument
        self.fromdate = datetime.strptime(fromdate, '%Y-%m-%d') if fromdate else None         # 先将日期转化为datetime对象
        self.todate = datetime.strptime(todate, '%Y-%m-%d') if todate else None               # 先将日期转化为datetime对象
        self.timeframe = timeframe

        self.cur_bar_list = []
        self.bar_dict = {self.instrument:[]}

        self.preload_bar_list = []

        self.iteral_data = self.load_csv()
        self.iteral_data2 = self.load_csv()    # for indicator

    def set_dtformat(self,bar):
        # 目前只设置支持int和str
        date = bar['date']
        dt = "%Y-%m-%d %H:%M:%S"
        if self.timeindex:
            date = datetime.strptime(str(date), self.dtformat).strftime('%Y-%m-%d')
            return date + ' ' + bar[self.timeindex.lower()]
        else:
            return datetime.strptime(str(date), self.dtformat).strftime(dt)

    def _get_new_bar(self):
        def _update():
            bar = next(self.iteral_data)
            bar = fy.walk_keys(lambda x:x.lower(), bar)
            bar['date'] = self.set_dtformat(bar)

            for i in list(bar.keys()):
                try:bar[i] = float(bar[i])      # 将数值转化为float
                except ValueError:pass
            return bar

        try:
            bar = _update()
            # 日期范围判断
            dt = '%Y-%m-%d %H:%M:%S'
            if self.fromdate:
                while datetime.strptime(bar['date'], dt) < self.fromdate:
                    bar = _update()
            if self.todate:
                while datetime.strptime(bar['date'], dt) > self.todate:
                    raise StopIteration

            self.cur_bar_list.pop(0) if len(self.cur_bar_list) is 2 else None
            self.cur_bar_list.append(bar)

        except StopIteration:
            self.continue_backtest = False  # stop backtest

    def load_csv(self):
        return csv.DictReader(open(self.datapath))

    def run_once(self):
        self._get_new_bar()
        self._preload()         # preload for indicator

    def update_bar(self, instrument):
        self.bar_dict[instrument].append(self.cur_bar_list[0])

    def _preload(self):
        """只需运行一次，先将fromdate前的数据都load到preload_bar_list"""
        """若没有fromdate，则不用load"""
        def _update():
            bar = next(self.iteral_data2)
            bar = fy.walk_keys(lambda x:x.lower(), bar)
            bar['date'] = self.set_dtformat(bar)

            for i in list(bar.keys()):
                try:bar[i] = float(bar[i])      # 将数值转化为float
                except ValueError:pass
            return bar

        try:
            bar = _update()
            # 日期范围判断
            dt = '%Y-%m-%d %H:%M:%S'
            if self.fromdate:
                while datetime.strptime(bar['date'], dt) < self.fromdate:
                    bar = _update()
                    self.preload_bar_list.append(bar)

                else:
                    self.preload_bar_list.pop(-1)   # 经过验证bug检查的，最后删除掉一个重复
            elif self.fromdate is None:
                pass
            else:
                raise SyntaxError('Catch a Bug!')

        except IndexError:
            pass

        except StopIteration:
            print('???')

        self.preload_bar_list.reverse()


    def start(self):
        # preload for indicator
        pass

    def prenext(self):
        self._get_new_bar()

    def next(self):
        self.update_bar(self.instrument)

        info = dict(instrument = self.instrument,
                    cur_bar_list = self.cur_bar_list,
                    bar_dict = self.bar_dict,
                    iteral_data2 = self.iteral_data2,
                    fromdate = self.fromdate,
                    dtformat = self.dtformat,
                    tmformat = self.tmformat,
                    timeindex = self.timeindex,
                    # index_list = self.index_list,
                    preload_bar_list = self.preload_bar_list)
        events.put(MarketEvent(info))


class Forex_CSVFeed(FeedBase):
    '''
    如果CSV中日期和时间分为两列，即一列为2017.01.01，一列为12:00:00，
    则需要在params中注明 timeindex，以及日期和时间的格式
    '''

    dtformat = '%Y%m%d'
    tmformat = '%H:%M:%S'
    timeindex = 'Timestamp'

    def __init__(self,datapath,instrument,fromdate=None,
                                todate=None,timeframe=None):
        super(Forex_CSVFeed,self).__init__(datapath,instrument,
                                            fromdate,todate,timeframe)

class Tushare_CSVFeed(FeedBase):
    '''
    如果CSV中日期和时间分为两列，即一列为2017.01.01，一列为12:00:00，
    则需要在params中注明 timeindex，以及日期和时间的格式
    '''

    dtformat = '%Y-%m-%d'
    tmformat = None
    timeindex = None

    def __init__(self,datapath,instrument,fromdate=None,
                                todate=None,timeframe=None):
        super(Tushare_CSVFeed,self).__init__(datapath,instrument,
                                            fromdate,todate,timeframe)

class Futures_CSVFeed(FeedBase):
    '''
    如果CSV中日期和时间分为两列，即一列为2017.01.01，一列为12:00:00，
    则需要在params中注明 timeindex，以及日期和时间的格式
    '''

    dtformat = '%Y/%m/%d'
    tmformat = '%H:%M:%S'
    timeindex = 'Time'

    def __init__(self,datapath,instrument,fromdate=None,
                                todate=None,timeframe=None):
        super(Futures_CSVFeed,self).__init__(datapath,instrument,
                                            fromdate,todate,timeframe)


class GenericCSVFeed(FeedBase):
    '''
    如果CSV中日期和时间分为两列，即一列为2017.01.01，一列为12:00:00，
    则需要在params中注明 timeindex，以及日期和时间的格式
    '''
    dtformat = '%Y-%m-%d'
    tmformat = '%H:%M:%S'
    timeindex = None

    def __init__(self,datapath,instrument,fromdate=None,todate=None,timeframe=None):
        super(GenericCSVFeed,self).__init__(datapath,instrument,fromdate,todate,timeframe)




################ Main func ##################
def run_first(feed_list):
    for feed in feed_list:
        feed.run_once()

def load_all_feed(feed_list):
    for feed in feed_list:
        feed.start()
        feed.prenext()
        feed.next()


def combine_feed():
    # 将所有feed的信息都整合在一起
    pass
