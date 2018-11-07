import arrow

from OnePy.builtin_module.backtest_stock.stock_recorder import StockRecorder
from OnePy.builtin_module.data_readers.csvreader import CSVReader
from OnePy.sys_module.models.base_bar import BarBase
from setting_for_test import (DATABASE, END, FREQUENCY, INSTRUMENT, START,
                              TICKER, set_easy_context, shift_date)


def test_bar():
    # 初始化数据
    set_easy_context()
    reader = CSVReader(data_path='./', file_name=TICKER, ticker=TICKER)
    StockRecorder()

    if FREQUENCY == 'H1':
        shift_num = 1/24
    elif FREQUENCY == 'D':
        shift_num = 1

    # 应该返回迭代器
    bars = BarBase(TICKER, FREQUENCY)
    bars.initialize(7)

    for key in ['date', 'open', 'high', 'low', 'close', 'volume']:  # key 小写
        assert key in bars.next_ohlc, f"'{key}' should be lower case in data"

    # 测试日期
    # start = bars.next_ohlc['date']
    start = arrow.get(START).format("YYYY-MM-DD HH:mm:ss")
    pre_start = shift_date(start, -shift_num)
    assert arrow.get(bars.current_ohlc['date']) <= arrow.get(START)
    assert arrow.get(bars.current_ohlc['date']) <= arrow.get(
        pre_start), "current_ohlc is wrong"
    assert arrow.get(bars.next_ohlc['date']) <= arrow.get(
        start), "next_ohlc is wrong"

    bars.next_directly()
    assert arrow.get(bars.previous_ohlc['date']) <= arrow.get(
        pre_start), "previous_ohlc is wrong"
    assert arrow.get(bars.current_ohlc['date']) <= arrow.get(
        start), "current_ohlc is wrong"
    [i for i in bars._iter_data]
    assert arrow.get(bars.next_ohlc['date']) <= arrow.get(
        END), "bar should not ahead"

    # 测试变量类型
    assert isinstance(bars.open, float), "should be float"
    assert isinstance(bars.high, float), "should be float"
    assert isinstance(bars.low, float), "should be float"
    assert isinstance(bars.close, float), "should be float"
    assert isinstance(bars.volume, float), "should be float"
    assert isinstance(bars.next_ohlc['open'], float), "should be float"

    # 测试变量返回值
    assert bars.date == bars.current_ohlc['date']
    assert bars.open == bars.current_ohlc['open']
    assert bars.high == bars.current_ohlc['high']
    assert bars.low == bars.current_ohlc['low']
    assert bars.close == bars.current_ohlc['close']
    assert bars.volume == bars.current_ohlc['volume']

    bars.env.execute_on_close_or_next_open = 'open'
    assert bars.execute_price == bars.next_ohlc['open']
    bars.env.execute_on_close_or_next_open = 'close'
    assert bars.execute_price == bars.close


if __name__ == "__main__":
    test_bar()
