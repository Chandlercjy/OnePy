import arrow
import funcy as fy
import pymongo

from .feedbase import FeedMetabase


class MongoDB_Backtest_Feed(FeedMetabase):
    host = 'localhost'
    port = 27017

    def __init__(self, database, collection, fromdate=None, todate=None, host=None, port=None):
        super(MongoDB_Backtest_Feed, self).__init__(database)
        self.live_mode = False
        self.continue_backtest = True

        self.fromdate = fromdate
        self.todate = todate

        self.preload_bar_list = []

        self.host = host if host else self.host
        self.port = port if port else self.port

        self.database = database
        self.collection = collection

        self.iteral_data = self._load_data()

        self.buffer = 10

    def set_collection(self):
        client = pymongo.MongoClient(host=self.host, port=self.port)
        db = client[self.database]
        Collection = db[self.collection]
        return Collection

    def _load_data(self):
        coll = self.set_collection()
        if self.fromdate and self.todate:
            return coll.find({'date': {'$gt': self.fromdate, '$lt': self.todate}})
        elif self.fromdate:
            return coll.find({'date': {'$gt': self.fromdate}})
        elif self.todate:
            return coll.find({'date': {'$lt': self.todate}})
        else:
            return coll.find()

    def get_new_bar(self):
        def _update():
            bar = self.iteral_data.next()
            bar.pop('_id')
            for i in bar:
                try:
                    bar[i] = float(bar[i])  # 将数值转化为float
                except ValueError:
                    pass
                except TypeError:
                    pass
            return bar

        try:
            bar = _update()
            self.cur_bar.add_new_bar(bar)

        except StopIteration:
            self.continue_backtest = False  # stop backtest

    def preload(self):
        """只需运行一次，先将fromdate前的数据都load到preload_bar_list"""
        """若没有fromdate，则不用load"""
        coll = self.set_collection()

        if self.fromdate:
            buff_date = arrow.get(self.fromdate).replace(days=-self.buffer)
            buff_date = buff_date.format('YYYY-MM-DD HH:mm:ss')
            self.iteral_buffer = coll.find({'date': {'$gt': buff_date, '$lt': self.fromdate}})

        else:
            self.iteral_buffer = []

        self.preload_bar_list = [i for i in self.iteral_buffer]

        fy.walk(lambda x: x.pop('_id'), self.preload_bar_list)

        self.preload_bar_list.reverse()
