import json

import arrow
import tushare as ts

from OnePy.builtin_module.mongodb_saver.mongodb_config import MongodbConfig
from OnePy.utils.awesome_func import run_multiprocessing, run_multithreading


class Tushare_to_MongoDB(MongodbConfig):
    host = "localhost"
    port = 27017

    def __init__(self, database, collection, host=None, port=None):
        super(Tushare_to_MongoDB, self).__init__(
            database, collection, host, port)
        self.ktype: str = None

    def _load_from_api(self, code, start, end, ktype, autype, index):
        d = dict(code=code, ktype=ktype)

        if start:
            d["start"] = start

        if end:
            d["end"] = end

        df = ts.get_k_data(**d)
        df.reset_index(drop=True, inplace=True)
        j = df.to_json()
        data = json.loads(j)

        df_len = len(df)

        return data, df_len

    def data_to_db(self, code, start=None, end=None,
                   ktype="D", autype="qfq", index=False):
        self.ktype = ktype
        data, df_len = self._load_from_api(
            code, start, end, ktype, autype, index)
        self._combine_and_insert(data)

        return df_len

    def _combine_and_insert(self, data):
        """整合并插入数据"""
        # 构造 index 列表
        name_list = ['date', 'open', 'high', 'low', 'close', 'volume']

        def process_data(n):
            # 返回单个数据的字典，key为index，若无index则返回 None
            single_data = {index: data[index].get(str(n))
                           for index in name_list}

            return single_data

        lenth = len(data['date'])  # 总长度
        coll = self._set_collection()

        # 插入数据

        for i in range(lenth):
            bar = process_data(i)
            bar['date'] = arrow.get(bar['date']).format("YYYY-MM-DD HH:mm:ss")

            if self.ktype == 'D':
                bar['date'] = bar['date'].replace('00:00:00', '15:00:00')

            coll.insert_one(bar)


def multi_tushare_to_mongodb(ticker_list: list, period_list: list,
                             fromdate: str=None):
    """
    多线程下载数据.
    periods: M5, M15, M30, H1, D, W
    """
    params_series = []

    for ticker in ticker_list:
        for frequency in period_list:
            params_series.append((ticker, frequency, fromdate))

    print('Start!')
    run_multithreading(get_data, params_series, max_worker=None)
    print(f'{ticker_list},{frequency} all set!!!!!')


def get_data(database, collection, fromdate):
    if collection not in ['M5', 'M15', 'M30', 'H1', 'D', 'W']:
        raise Exception("collection should be in M5,M15,M30,H1,D,W ")

    if collection in ['M5', 'M15', 'M30']:
        ktype = collection.replace("M", '')
    elif collection == 'H1':
        ktype = '60'
    else:
        ktype = collection

    single = Tushare_to_MongoDB(
        database=f'{database}_tushare', collection=collection)
    try:
        length = single.data_to_db(code=database, start=fromdate,
                                   ktype=ktype, autype="qfq", index=False)
        print(
            f'<<{database}, {collection}>> has completed, Total: {length}')
    except Exception as e:
        print(f'Retry: <<{database}>>, Becasue {e}')
        get_data(database, collection, fromdate)
        print('retry successed!')
