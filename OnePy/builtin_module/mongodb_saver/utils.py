import pymongo

from OnePy.utils.awesome_func import run_multiprocessing, run_multithreading


class MongoDBFunc:

    def __init__(self, host='localhost', port=27017):
        self.host = host
        self.port = port

    def _set_collection(self, database, collection):
        """设置数据库"""
        client = pymongo.MongoClient(host=self.host, port=self.port)
        db = client[database]
        Collection = db[collection]

        return Collection

    def _drop_duplicates_func(self, collection_obj):
        """删除重复数据"""
        c = collection_obj.aggregate([{"$group":
                                       {"_id": {'date': '$date'},
                                        "count": {'$sum': 1},
                                           "dups": {'$addToSet': '$_id'}}},
                                      {'$match': {'count': {"$gt": 1}}}
                                      ], allowDiskUse=True
                                     )

        def get_duplicates():
            for i in c:
                for dup in i['dups'][1:]:
                    yield dup

        length = 0

        for i in get_duplicates():
            collection_obj.delete_one({'_id': i})
            length += 1

        return length

    def drop_duplicates(self, ticker_list, period_list, broker):
        run_multiprocessing(self.drop_duplicates_one_by_one,
                            [(ticker, frequency, broker)

                             for ticker in ticker_list for frequency in period_list], 20)

    def drop_duplicates_one_by_one(self, database, collection, broker):
        coll = self._set_collection(f'{database}_{broker}', collection)
        length = self._drop_duplicates_func(coll)
        print(f'<<{database}, {collection}>> has been drop {length} duplicates!')

    def drop_collections(self, ticker_list, period_list, broker):
        run_multithreading(self.drop_collection_one_by_one,
                           [(ticker, frequency, broker)
                            for ticker in ticker_list for frequency in period_list], 20)

    def drop_collection_one_by_one(self, database, collection, broker):
        coll = self._set_collection(database+f'_{broker}', collection)
        coll.drop()
        print(f'<<{database}, {collection}>> has been deleted!')


def get_interval(frequency):

    if frequency == 'S5':
        interval_num = 0.25
    elif frequency == 'S10':
        interval_num = 0.5
    elif frequency == 'S30':
        interval_num = 1.5
    elif frequency == 'M1':
        interval_num = 3
    elif frequency == 'M2':
        interval_num = 6
    elif frequency == 'M4':
        interval_num = 12
    elif frequency == 'M5':
        interval_num = 17
    elif frequency == 'M10':
        interval_num = 34
    elif frequency == 'M15':
        interval_num = 51
    elif frequency == 'M30':
        interval_num = 90
    elif frequency == 'H1':
        interval_num = 180
    elif frequency == 'H2':
        interval_num = 360
    elif frequency == 'H3':
        interval_num = 400
    elif frequency == 'H4':
        interval_num = 700
    elif frequency == 'H6':
        interval_num = 800
    else:
        interval_num = 1000

    return interval_num
