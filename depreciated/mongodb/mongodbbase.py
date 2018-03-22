import json
from datetime import datetime

import funcy as fy
import pandas as pd
import pymongo


class MongoDB_config(object):
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

    def __init__(self, database, collection, host=None, port=None):
        self.host = host if host else self.host
        self.port = port if port else self.port
        self.database = database
        self.collection = collection

    def __set_dtformat(self, bar):
        """识别日期"""
        date = bar[self.date.lower()]
        dt = "%Y-%m-%d %H:%M:%S"
        if '%H' in self.dtformat:
            return datetime.strptime(str(date), self.dtformat).strftime(dt)
        elif self.time:
            date = datetime.strptime(str(date), self.dtformat).strftime('%Y-%m-%d')
            return date + ' ' + bar[self.time.lower()]
        else:
            return datetime.strptime(str(date), self.dtformat).strftime('%Y-%m-%d')

    def _set_collection(self):
        """设置数据库"""
        client = pymongo.MongoClient(host=self.host, port=self.port)
        db = client[self.database]
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
            print('Inserting ' + str(i) + ', Total: ' + str(lenth))

    def __get_dups_id(self, data):
        """获得重复数据的id"""
        data['dups'].pop(0)
        return data['dups']

    def _drop_duplicates(self):
        """删除重复数据"""
        coll = self._set_collection()
        c = coll.aggregate([{"$group":
                                 {"_id": {'date': '$date'},
                                  "count": {'$sum': 1},
                                  "dups": {'$addToSet': '$_id'}}},
                            {'$match': {'count': {"$gt": 1}}}
                            ]
                           )
        data = [i for i in c]
        duplicates = fy.walk(self.__get_dups_id, data)
        dups_id_list = fy.cat(duplicates)
        for i in dups_id_list:
            coll.delete_one({'_id': i})
        # print("OK, duplicates droped! Done!")

    def data_to_db(self, path):
        """数据导入数据库"""
        data = self.__load_csv(path)
        self._combine_and_insert(data)
        self._drop_duplicates()
