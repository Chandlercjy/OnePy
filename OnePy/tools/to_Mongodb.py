#coding=utf8

import pymongo
from collections import OrderedDict
import json
import pandas as pd
from ..utils.py3 import with_metaclass
from ..utils.metabase import MetaParams
from datetime import datetime

class MongoDB_config(with_metaclass(MetaParams,object)):
    params = dict(host='localhost',
                  port = 27017,
                  dtformat = '%Y-%m-%d %H:%M:%S',
                  tmformat = '%H:%M:%S',
                  date = 'Date',
                  time = 'Timestamp',
                  open = 'Open',
                  high = 'High',
                  low = 'Low',
                  close = 'Close',
                  volume = 'Volume',
                  openinterest = None)

    def __init__(self,database,collection,host=None,port=None):
        self.host = host if host else self.p.host
        self.port = port if port else self.p.port
        self.database = database
        self.collection = collection

    def set_dtformat(self,bar):
        # 目前只设置支持int和str
        date = bar[self.p.date.lower()]
        dt = "%Y-%m-%d %H:%M:%S"
        if '%H' in self.p.dtformat:
            return datetime.strptime(str(date), self.p.dtformat).strftime(dt)
        elif self.p.time:
            date = datetime.strptime(str(date), self.p.dtformat).strftime('%Y-%m-%d')
            return date + ' ' + bar[self.p.time.lower()]
        else:
            return datetime.strptime(str(date), self.p.dtformat).strftime('%Y-%m-%d')


    def set_collection(self):
        client = pymongo.MongoClient(host=self.host, port=self.port)
        db = client[self.database]
        Collection = db[self.collection]
        return Collection

    def load_csv(self, path):
        df = pd.read_csv(path)
        j = df.to_json()
        data = json.loads(j)
        return data

    def combine_and_insert(self, data):
        # 构造 index 列表
        name_list = [self.p.date, self.p.time, self.p.open, self.p.high,
                    self.p.low, self.p.close, self.p.volume,self.p.openinterest]
        # 删除 None
        for i in range(len(name_list)):
            if None in name_list:
                name_list.remove(None)

        def process_data(n):
            # 返回单个数据的字典，key为index，若无index则返回 None
            single_data = {index.lower():data[index].get(str(n))
                                for index in name_list}
            return single_data

        lenth = len(data[self.p.date])  # 总长度
        coll = self.set_collection()

        # 插入数据
        for i in range(lenth):
            bar = process_data(i)
            bar[self.p.date.lower()] = self.set_dtformat(bar)
            coll.insert_one(bar)
            print 'Inserting ' + str(i) + ', Total: '+ str(lenth)


    def csv_to_db(self, path):
        data = self.load_csv(path)
        self.combine_and_insert(data)


class Forex_CSV_to_MongoDB(with_metaclass(MetaParams, MongoDB_config)):
    params = dict(host='localhost',
                  port = 27017,
                  dtformat = '%Y%m%d',
                  tmformat = '%H:%M:%S',
                  date = 'Date',
                  time = 'Timestamp',
                  open = 'Open',
                  high = 'High',
                  low = 'Low',
                  close = 'Close',
                  volume = 'Volume',
                  openinterest = None)

    def __init__(self,database,collection,host=None,port=None):
        super(Forex_CSV_to_MongoDB, self).__init__(database,collection,host,port)

# for tushare
class TS_CSV_to_MongoDB(with_metaclass(MetaParams, MongoDB_config)):
    params = dict(host='localhost',
                  port = 27017,
                  dtformat = '%Y-%m-%d',
                  tmformat = '%H:%M:%S',
                  date = 'date',
                  time = None,
                  open = 'open',
                  high = 'high',
                  low = 'low',
                  close = 'close',
                  volume = 'volume',
                  openinterest = None)

    def __init__(self,database,collection,host=None,port=None):
        super(TS_CSV_to_MongoDB, self).__init__(database,collection,host,port)
