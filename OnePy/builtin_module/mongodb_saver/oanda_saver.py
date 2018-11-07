import math

import arrow
import funcy as fy
from oandapyV20.exceptions import V20Error
from oandakey import access_token, accountID

from OnePy.builtin_module.mongodb_saver.mongodb_config import MongodbConfig
from OnePy.builtin_module.mongodb_saver.utils import get_interval
from OnePy.custom_module.api.oanda_api import OandaAPI
from OnePy.utils.awesome_func import run_multiprocessing, run_multithreading


class Oanda_to_mongodb(MongodbConfig):
    def __init__(self, accountID, access_token, database,
                 collection, host=None, port=None, print_log=True):
        super().__init__(database, collection, host, port)

        self.api = OandaAPI(accountID, access_token)
        self.print_log = print_log

    def _normalize(self, candle):
        date = candle['time'].replace('T', ' ')[:19]
        ohlc = dict(date=date,
                    timestamp=date[-8:],
                    open=float(candle['mid']['o']),
                    high=float(candle['mid']['h']),
                    low=float(candle['mid']['l']),
                    close=float(candle['mid']['c']),
                    volume=float(candle['volume']),
                    complete=float(candle['complete']))

        return ohlc

    def _combine_and_insert(self, data):
        data = data['candles']
        candle_list = fy.walk(self._normalize, data)

        lenth = len(candle_list)  # 总长度
        coll = self._set_collection()

        # 插入数据
        i = 0

        for bar in candle_list:
            i += 1
            coll.insert_one(bar)

            if self.print_log:
                date = bar['date']
                # print(f'Inserting {i}, Total: {lenth}, date: {date}')

    def candle_to_db(self, instrument, granularity, count=50,
                     fromdate=None, todate=None, price='M',
                     smooth=False, includeFirst=None):
        """
        granularity: S5, S10, S30, M1, M2, M4, M5, M10, M15, M30
                     H1, H2, H3, H4, H6, H8, H12,
                     D, W, M
        """
        data = self.api.get_candlestick_list(instrument, granularity, count,
                                             fromdate, todate, price, smooth, includeFirst)
        self._combine_and_insert(data)


def multi_oanda_candles_to_mongodb(accountID, access_token,
                                   ticker_list,
                                   period_list,
                                   fromdate=None,
                                   todate=None):
    """
    period: S5, S10, S30, M1, M2, M4, M5, M10, M15, M30
                 H1, H2, H3, H4, H6, H8, H12,
                 D, W, M

    """

    date = fromdate
    params_series = []

    for ticker in ticker_list:
        for frequency in period_list:
            interval = get_interval(frequency)
            diff = arrow.get(todate) - arrow.get(fromdate)
            loop_time = math.ceil(abs(diff.days)/interval)

            for i in range(loop_time):
                new_fromdate = arrow.get(fromdate).replace(
                    days=interval*i).format('YYYY-MM-DDTHH:mm:ss')+"Z"

                params_tuple = (ticker, frequency, new_fromdate)
                params_series.append(params_tuple)

    params_series = (i for i in params_series)
    print('Start!')
    run_multithreading(get_data, [params for params in params_series], 20)
    print(f'{ticker_list},{frequency} all set!!!!!')


def get_data(database, collection, fromdate):
    single = Oanda_to_mongodb(
        accountID, access_token, database+'_oanda', collection)
    try:
        single.candle_to_db(database, collection,
                            count=5000, fromdate=fromdate)
    except V20Error:
        print(f'<<{database}, {collection}>> has been completed')
