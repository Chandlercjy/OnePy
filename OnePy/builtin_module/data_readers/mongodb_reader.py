
import time

import pymongo

from OnePy.sys_module.base_reader import ReaderBase


class MongodbReader(ReaderBase):
    host = 'localhost'
    port = 27017
    client = pymongo.MongoClient(host=host, port=port, connect=False)

    def __init__(self,  database, ticker,  key=None):
        super().__init__(ticker, key)
        self.database = database

    def set_collection(self, database: str, collection: str):
        db = self.client[database]
        Collection = db[collection]

        return Collection

    def load(self, fromdate: str, todate: str, frequency: str):
        if self.key:
            coll = self.set_collection(database=self.database,
                                       collection=self.key)
        else:
            coll = self.set_collection(database=self.database,
                                       collection=frequency)
        result = coll.find(
            {'date': {'$gte': fromdate, '$lte': todate}}).sort('date', 1)

        return result
