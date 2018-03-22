import json
import tushare as ts

from OnePy.mongodb.mongodbbase import MongoDB_config


class Tushare_to_MongoDB(MongoDB_config):
    host = "localhost"
    port = 27017
    dtformat = "%Y-%m-%d %H:%M"
    tmformat = "%H:%M:%S"
    date = "date"
    time = None
    open = "open"
    high = "high"
    low = "low"
    close = "close"
    volume = "volume"
    openinterest = None

    def __init__(self, database, collection, host=None, port=None):
        super(Tushare_to_MongoDB, self).__init__(database, collection, host, port)

    def __load_csv(self, code, start, end, ktype, autype, index):
        d = dict(code=code, ktype=ktype)
        if start:
            d["start"] = start
        if end:
            d["end"] = end
        if ktype is "D":
            self.dtformat = "%Y-%m-%d"
        df = ts.get_k_data(**d)
        df.reset_index(drop=True,inplace=True)
        j = df.to_json()
        data = json.loads(j)
        return data

    def data_to_db(self, code, start=None, end=None,
                   ktype="D", autype="qfq", index=False):
        data = self.__load_csv(code, start, end, ktype, autype, index)
        self._combine_and_insert(data)
        self._drop_duplicates()
