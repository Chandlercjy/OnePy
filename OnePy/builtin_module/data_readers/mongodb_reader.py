
import pymongo

from OnePy.sys_module.base_reader import DataReaderBase
from OnePy.sys_module.models.bar_backtest import BarBacktest


class MongodbReader(DataReaderBase):
    host = 'localhost'
    port = 27017
    client = pymongo.MongoClient(host=host, port=port, connect=False)

    def __init__(self, database, collection, ticker, fromdate=None, todate=None):
        super().__init__(ticker, fromdate, todate)
        self.database = database
        self.collection = collection

    def set_collection(self):
        db = self.client[self.database]
        Collection = db[self.collection]

        return Collection

    def load(self, fromdate=None, todate=None):
        coll = self.set_collection()

        if fromdate is None:
            fromdate = self.fromdate

        if todate is None:
            todate = self.todate

        if fromdate and todate:
            return coll.find({'date': {'$gte': fromdate, '$lt': todate}})
        elif fromdate:
            return coll.find({'date': {'$gte': fromdate}})
        elif todate:
            return coll.find({'date': {'$lt': todate}})
        else:
            return coll.find()

    def get_bar(self):
        return BarBacktest(self)
