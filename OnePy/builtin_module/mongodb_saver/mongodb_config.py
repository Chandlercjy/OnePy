import json
from datetime import datetime

import arrow
import funcy as fy
import pandas as pd
import pymongo


class MongodbConfig(object):
    host = 'localhost'
    port = 27017
    dtformat = '%Y-%m-%d %H:%M:%S'
    tmformat = '%H:%M:%S'
    date = 'Date'
    time = 'Timestamp'
    open = 'Open'
    high = 'High'
    low = 'Low'
    close = 'Close'
    volume = 'Volume'
    openinterest = None
    client = pymongo.MongoClient(host=host, port=port, connect=False)

    def __init__(self, database, collection, host=None, port=None):
        self.host = host if host else self.host
        self.port = port if port else self.port
        self.database = database
        self.collection = collection

    def __set_dtformat(self, bar):
        """识别日期"""

        return arrow.get(bar['date']).format('YYYY-MM-DD HH:mm:ss')

    def _set_collection(self):
        """设置数据库"""
        db = self.client[self.database]
        Collection = db[self.collection]

        return Collection

    def __load_csv(self, path):
        """读取CSV"""
        df = pd.read_csv(path)
        j = df.to_json()
        data = json.loads(j)

        return data

    def _combine_and_insert(self, data):
        """整合并插入数据"""
        # 构造 index 列表
        name_list = [self.date, self.time, self.open, self.high,
                     self.low, self.close, self.volume, self.openinterest]
        # 删除 None

        for i in range(len(name_list)):
            if None in name_list:
                name_list.remove(None)

        def process_data(n):
            # 返回单个数据的字典，key为index，若无index则返回 None
            single_data = {index.lower(): data[index].get(str(n))
                           for index in name_list}

            return single_data

        lenth = len(data[self.date])  # 总长度
        coll = self._set_collection()

        # 插入数据

        for i in range(lenth):
            bar = process_data(i)
            bar[self.date.lower()] = self.__set_dtformat(bar)

            coll.insert_one(bar)

    def data_to_db(self, path):
        """数据导入数据库"""
        data = self.__load_csv(path)
        self._combine_and_insert(data)
        print(f'{self.database}, {self.collection}, Total inserted: {len(data)}')
