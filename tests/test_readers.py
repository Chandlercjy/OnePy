import arrow

import OnePy as op
from OnePy.builtin_module.backtest_stock.stock_recorder import StockRecorder
from OnePy.builtin_module.data_readers.csvreader import CSVReader
from OnePy.builtin_module.data_readers.mongodb_reader import MongodbReader
from OnePy.sys_module.components.market_maker import MarketMaker
from OnePy.sys_module.models.base_bar import BarBase
from setting_for_test import (DATABASE, END, FREQUENCY, INSTRUMENT, START,
                              TICKER, set_easy_context, shift_date)


def func_test_reader(reader: op.ReaderBase):
    def test_load(start, end, iter_data):
        first_date = next(iter_data)['date']
        assert isinstance(first_date, str), "it should be iterable"

        if FREQUENCY == 'H1':
            shift_num = 1/24
        elif FREQUENCY == 'D':
            shift_num = 1
        next_date = shift_date(first_date, shift_num)
        assert next(iter_data)['date'] == next_date
        last_date = [i for i in iter_data][-1]['date']
        assert arrow.get(last_date) <= arrow.get(
            end), f"{last_date} can't more than {END}"

    StockRecorder()
    go = op.OnePiece()
    go.set_date(START, END, FREQUENCY, INSTRUMENT)

    test_iter_data = reader.load(START, END, FREQUENCY)
    test_load(START, END, test_iter_data)

    NEW_START = shift_date(START, -9)
    NEW_END = shift_date(NEW_START, 10)
    test_iter_data = reader.load_by_cleaner(NEW_START, NEW_END, FREQUENCY)
    test_load(NEW_START, NEW_END, test_iter_data)

    # 获取bar
    bars = MarketMaker.get_bar(TICKER, FREQUENCY)
    assert isinstance(bars, BarBase)
    assert reader in reader.env.readers.values()


def test_mongodb_reader():
    set_easy_context()
    reader = MongodbReader(database=DATABASE, ticker=TICKER)
    func_test_reader(reader)


def test_csv_reader():
    set_easy_context()
    reader = CSVReader(data_path='./', file_name=TICKER, ticker=TICKER)
    func_test_reader(reader)


if __name__ == "__main__":
    test_csv_reader()
