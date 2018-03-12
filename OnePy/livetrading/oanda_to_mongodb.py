import funcy as fy
import itertools
import arrow

from OnePy.livetrading import oanda
from OnePy.mongodb.mongodbbase import MongoDB_config


class Oanda_to_mongodb(MongoDB_config):
    def __init__(self, accountID, access_token, database,
                 collection, host=None, port=None, print_log=True):
        super(Oanda_to_mongodb, self).__init__(database, collection, host, port)

        self.api = oanda.oanda_api(accountID, access_token)
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
                print(f'Inserting {i}, Total: {lenth}, date: {date}')

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
        self._drop_duplicates()


def Multi_Oanda_Candles_to_MongoDB(accountID, access_token,
                                   instrument_list,
                                   period_list,
                                   count=50,
                                   interval=1,
                                   fromdate=None,
                                   todate=None):
    """
    period: S5, S10, S30, M1, M2, M4, M5, M10, M15, M30
                 H1, H2, H3, H4, H6, H8, H12,
                 D, W, M

    """
    from oandapyV20.exceptions import V20Error
    def get_data():
        single = Oanda_to_mongodb(accountID, access_token, i, j)
        if todate:
            single.candle_to_db(i, j, count=count,
                                fromdate=fromdate,
                                todate=todate)
        else:
            single.candle_to_db(i, j, count=count,
                                fromdate=fromdate)

    date = fromdate

    for i in instrument_list:
        for j in period_list:
            try:
                for k in itertools.count(1):
                    fromdate = arrow.get(fromdate).replace(days=interval).format('YYYY-MM-DD')
                    get_data()
            except V20Error:
                fromdate = date
                print(f'<<{i}, {j}>> has been completed!!!!!!!!!!!!!!!!!!')

    print('Everything is all right!')