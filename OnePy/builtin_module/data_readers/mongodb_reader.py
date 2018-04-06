
import arrow
import funcy as fy
import pymongo

from OnePy.sys_module.base_reader import DataReaderBase
from OnePy.sys_module.models.bars import Bar


class MongodbReader(DataReaderBase):
    host = 'localhost'
    port = 27017

    def __init__(self, database, collection, ticker, fromdate=None, todate=None, host=None, port=None):
        super().__init__(ticker, fromdate, todate)
        self.host = host if host else self.host
        self.port = port if port else self.port

        self.database = database
        self.collection = collection

    def set_collection(self):
        client = pymongo.MongoClient(host=self.host, port=self.port)
        db = client[self.database]
        Collection = db[self.collection]

        return Collection

    def load(self):
        coll = self.set_collection()

        if self.fromdate and self.todate:
            return coll.find({'date': {'$gt': self.fromdate, '$lt': self.todate}})
        elif self.fromdate:
            return coll.find({'date': {'$gt': self.fromdate}})
        elif self.todate:
            return coll.find({'date': {'$lt': self.todate}})
        else:
            return coll.find()

    def get_bar(self):
        return Bar(self)


if __name__ == "__main__":
    db = MongodbReader('tushare', '000001', '000001')
    b = db.load()
    print(next(b))
