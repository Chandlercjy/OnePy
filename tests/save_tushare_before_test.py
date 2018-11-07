from OnePy.builtin_module.mongodb_saver.tushare_saver import \
    multi_tushare_to_mongodb
from OnePy.builtin_module.mongodb_saver.utils import MongoDBFunc

TICKER_LIST = ['000001']

FREQUENCY = ['D', 'H1']
START = '2018-01-01'

multi_tushare_to_mongodb(ticker_list=TICKER_LIST,
                         period_list=FREQUENCY, fromdate=START)
MongoDBFunc().drop_duplicates(TICKER_LIST, FREQUENCY, 'tushare')
