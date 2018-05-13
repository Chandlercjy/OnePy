import arrow

from OnePy.builtin_module.data_readers.csvreader import CSVReader
from OnePy.builtin_module.data_readers.mongodb_reader import MongodbReader
from OnePy.sys_module.base_cleaner import CleanerBase

DATABASE = 'tushare'
COLLECTION = '000001'
START = '2018-01-03'
END = '2018-02-01'


def func_test_reader(reader):
    def roll_bar_to_end(bar_object):

        while True:
            try:
                bar_object.next()
            except StopIteration:
                break

    # 应该返回迭代器
    test_iter_data = reader.load(START, END)
    assert next(test_iter_data), "it should be iterable"

    bars = reader.get_bar()
    # key 应该小写

    for key in ['date', 'open', 'high', 'low', 'close', 'volume']:
        assert key in bars.next_ohlc, f"'{key}' should be lower case in data"

    # 测试日期
    assert bars.next_ohlc['date'] == START, (
        f"fromdate is wrong, should be {START} not {bars.next_ohlc['date']}")
    bars.next()
    assert bars.date == START, "fromdate is wrong"
    roll_bar_to_end(bars)
    assert arrow.get(bars.next_ohlc['date']) < arrow.get(
        END), "bar should ahead one interval for Cleaner"

    # 测试变量类型
    assert isinstance(bars.open, float), "should be float"
    assert isinstance(bars.high, float), "should be float"
    assert isinstance(bars.low, float), "should be float"
    assert isinstance(bars.close, float), "should be float"
    assert isinstance(bars.volume, float), "should be float"
    assert isinstance(bars.next_ohlc['open'], float), "should be float"

    bars._execute_mode = 'open'
    assert bars.execute_price == bars.next_ohlc['open']
    bars._execute_mode = 'close'
    assert bars.execute_price == bars.close


def func_test_base_cleaner(reader):

    cleaner = CleanerBase(10, 20)
    cleaner.initialize_buffer_data()
    raw_ohlc = reader.load(cleaner.startdate, START)
    latest_ohlc = [i for i in raw_ohlc][-1]

    # 测试load好的cleaner buffer为fromdate日期前的数据
    assert latest_ohlc['date'] == '2018-01-02', 'date is not right'
    assert cleaner.data['000001'][-1] == latest_ohlc['close']


def test_mongodb_reader():
    reader = MongodbReader(database=DATABASE, collection=COLLECTION,
                           ticker='000001', fromdate=START, todate=END)
    func_test_reader(reader)
    func_test_base_cleaner(reader)


def test_csv_reader():
    reader = CSVReader('./000001.csv', '000001', fromdate=START, todate=END)
    func_test_reader(reader)
    func_test_base_cleaner(reader)


if __name__ == "__main__":
    test_csv_reader()
