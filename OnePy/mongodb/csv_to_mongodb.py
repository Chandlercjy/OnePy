from OnePy.mongodb.mongodbbase import MongoDB_config


class Forex_csv_to_MongoDB(MongoDB_config):
    host = 'localhost'
    port = 27017
    dtformat = '%Y%m%d'
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
        super(Forex_csv_to_MongoDB, self).__init__(database, collection, host, port)


class Tushare_csv_to_MongoDB(MongoDB_config):
    host = 'localhost'
    port = 27017
    dtformat = '%Y-%m-%d'
    tmformat = '%H:%M:%S'
    date = 'date'
    time = None
    open = 'open'
    high = 'high'
    low = 'low'
    close = 'close'
    volume = 'volume'
    openinterest = None

    def __init__(self, database, collection, host=None, port=None):
        super(Tushare_csv_to_MongoDB, self).__init__(database, collection, host, port)