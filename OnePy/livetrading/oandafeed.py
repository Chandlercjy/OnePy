from datetime import timedelta
from time import sleep

import arrow
import funcy as fy
import pymongo

from OnePy.feeds.feedbase import FeedMetabase
from OnePy.livetrading.oanda_to_mongodb import Oanda_to_mongodb

class Oanda_Feed(FeedMetabase):
    host = 'localhost'
    port = 27017

    def __init__(self, database, collection, instrument, host=None, port=None):
        super(Oanda_Feed, self).__init__(instrument, fromdate=None, todate=None)
        self.continue_backtest = True

        self.instrument = instrument
        self.bar_dict = {self.instrument: []}
        self.preload_bar_list = []

        self.host = host if host else self.host
        self.port = port if port else self.port

        self.database = database
        self.collection = collection

        self._buffer_days = 4
        self.ratio = self._get_day_ratio()

    def set_collection(self):
        client = pymongo.MongoClient(host=self.host, port=self.port)
        db = client[self.database]
        Collection = db[self.collection]
        return Collection

    def run_once(self):
        self._save_to_mongodb(5000)
        self.load_data()
        self.get_new_bar()
        self.preload()  # preload for indicator

    def _get_day_ratio(self):
        """
        (S5, S10, S30, M1, M2, M4, M5) <- BAD Interval
        M10, M15, M30, H1, H2, H3, H4, H6, H8, H12
        """
        if self.collection == "S5":
            return 5 / 60 / 60 / 24
        elif self.collection == "S10":
            return 10 / 60 / 60 / 24
        elif self.collection == "S30":
            return 30 / 60 / 60 / 24
        elif self.collection == "M1":
            return 1 / 60 / 24
        elif self.collection == "M2":
            return 2 / 60 / 24
        elif self.collection == "M4":
            return 4 / 60 / 24
        elif self.collection == "M5":
            return 5 / 60 / 24
        elif self.collection == "M10":
            return 10 / 60 / 24
        elif self.collection == "M15":
            return 15 / 60 / 24
        elif self.collection == "M30":
            return 30 / 60 / 24
        elif self.collection == "H1":
            return 1 / 24
        elif self.collection == "H2":
            return 2 / 24
        elif self.collection == "H3":
            return 3 / 24
        elif self.collection == "H4":
            return 4 / 24
        elif self.collection == "H8":
            return 8 / 24
        elif self.collection == "H12":
            return 12 / 24

    def load_data(self):
        """在livetrading中，此函数作用为生成最新的cur_bar的data"""
        coll = self.set_collection()
        Datetime = arrow.utcnow().replace(days=-self.ratio * 10).format('YYYY-MM-DD HH:mm:ss')
        bar = coll.find({'date': {"$gt": Datetime}}).sort('date')
        latest_bar = [i for i in bar][-2:]
        self.cur_bar.add_new_bar(latest_bar, True)

    def _value_to_float(self, bar):
        # bar.pop('_id')
        for i in bar:
            try:
                bar[i] = float(bar[i])  # 将数值转化为float
            except ValueError:
                pass
            except TypeError:
                pass
        return bar

    def get_new_bar(self):
        """直接从API读取feed"""

        bar_list = self.get_candles()
        last_bar = self.cur_bar.cur_data
        while arrow.get(bar_list[0]['date']) >= arrow.get(last_bar['date']):
            if arrow.get(bar_list[0]['date']) > arrow.get(last_bar['date']) \
                    and bar_list[0]['complete'] == 1:
                fy.walk(self._value_to_float, bar_list)

                self.cur_bar.add_new_bar(bar_list, live=True)
                break
            else:
                if (arrow.utcnow() - arrow.get(last_bar['date'])) >= timedelta(self.ratio * 2):
                    # print(arrow.utcnow() - arrow.get(last_bar['date']))
                    # print(timedelta(self.ratio * 2))
                    # print(arrow.get(last_bar['date']))
                    bar_list = self.get_candles()
                    sleep(3)
                else:
                    sleep(1)

    def preload(self):
        """只需运行一次，先将fromdate前的数据都load到preload_bar_list"""
        """若没有fromdate，则不用load"""
        coll = self.set_collection()

        buff_date = arrow.utcnow().replace(days=-self.buffer_days)
        buff_date = buff_date.format('YYYY-MM-DD HH:mm:ss')
        self.set_iteral_buffer(coll.find({'date': {'$gt': buff_date}}))

        self.preload_bar_list = [i for i in self.iteral_buffer]
        fy.walk(lambda x: x.pop('_id'), self.preload_bar_list)
        self.preload_bar_list.reverse()

    def _save_to_mongodb(self, count=500):
        data_to_db = Oanda_to_mongodb(self.accountID, self.access_token,
                                      self.database, self.collection,
                                      print_log=False)
        data_to_db.candle_to_db(self.database, self.collection, count=count)

    def get_candles(self):
        data = self.oanda.get_candlestick_list(instrument=self.database, granularity=self.collection, count=5)
        return self.format_candles(data)

    def format_candles(self, data):
        bar_list = []
        for i in [2, 1]:
            ohlc = data['candles'][-i]['mid']
            ohlc['open'] = ohlc.pop("o")
            ohlc['high'] = ohlc.pop("h")
            ohlc['low'] = ohlc.pop("l")
            ohlc['close'] = ohlc.pop("c")

            ohlc['date'] = arrow.get(data['candles'][-i]['time']).format("YYYY-MM-DD HH:mm:ss")
            ohlc['timestamp'] = arrow.get(data['candles'][-i]['time']).format("HH:mm:ss")
            ohlc['volume'] = data['candles'][-i]['volume']
            ohlc['complete'] = data['candles'][-i]['complete']
            bar_list.append(ohlc)

        return bar_list


if __name__ == '__main__':
    from OnePy.livetrading import oanda

    feed = Oanda_Feed(database='EUR_USD', collection='S10',instrument="EUR_USD")
    feed.accountID = accountID
    feed.access_token = access_token
    feed.oanda = oanda.oanda_api(accountID, access_token)

    print(1)
    feed.run_once()
    print(feed.cur_bar.cur_data)
    print(2)
    feed.get_new_bar()
    print(feed.cur_bar.cur_data)
    print(3)
    feed.get_new_bar()
    print(feed.cur_bar.cur_data)
    print(4)
    feed.get_new_bar()
    print(feed.cur_bar.cur_data)
