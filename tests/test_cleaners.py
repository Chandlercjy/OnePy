import arrow

from OnePy.builtin_module.backtest_stock.stock_recorder import StockRecorder
from OnePy.builtin_module.data_readers.csvreader import CSVReader
from OnePy.custom_module.cleaner_sma import SMA
from OnePy.sys_module.components.market_maker import MarketMaker
from setting_for_test import (END, FREQUENCY, INSTRUMENT, START, TICKER,
                              global_setting, set_easy_context)


def func_test_update_cleaner(frequency):
    set_easy_context()
    StockRecorder()
    reader = CSVReader(data_path='./', file_name=TICKER, ticker=TICKER)
    cleaner = SMA(rolling_window=10, buffer_day=10, frequency=frequency)
    cleaner2 = SMA(rolling_window=10, buffer_day=1, frequency=frequency)
    env = reader.env

    # 初始化
    MarketMaker._initialize_feeds()
    MarketMaker._initialize_calendar()
    MarketMaker._initialize_cleaners()  # 以sys_date初始化

    # 以 sys_date 来进行初始化数据，因为一开始 sys_date 会比 fromdate 向前一步
    # 测试开始回测时 buffer 数据最新一条是否为 Start 前一根 bar 的数据。
    key = f'{TICKER}_{frequency}'
    assert arrow.get(cleaner.data[key]['date'][-1]
                     ) <= arrow.get(env.sys_date)

    # sys_date和cleaner中的数据都更新到和fromdate同步
    MarketMaker.calendar.update_calendar()
    MarketMaker._update_bar()
    cleaner.run()

    if INSTRUMENT == 'A_Shares':  # 测试buffer_day是否会自动变化
        assert cleaner2.buffer_day == 5

    if cleaner.frequency == env.sys_frequency:
        cur_bar = env.feeds[TICKER]
    else:
        cur_bar = env.cleaners_feeds[key+'_'+cleaner.name]

    # cleaner run之后日期一切正常
    latest_date = cleaner.data[key]['date'][-1]
    assert latest_date == cur_bar.date, f'{latest_date} != {cur_bar.date}'

    # 测试更新后是否成功
    env.execute_on_close_or_next_open = 'open'
    env.cur_suspended_tickers.clear()
    MarketMaker.calendar.update_calendar()
    MarketMaker._update_bar()

    cleaner.run()
    latest_date = cleaner.data[key]['date'][-1]
    assert latest_date == cur_bar.date, f'{latest_date} != {cur_bar.date}'
    assert cleaner.data[key]['open'][-1] == cur_bar.current_ohlc['open']
    assert cleaner.data[key]['high'][-1] == cur_bar.current_ohlc['high']
    assert cleaner.data[key]['low'][-1] == cur_bar.current_ohlc['low']
    assert cleaner.data[key]['close'][-1] == cur_bar.current_ohlc['close']
    assert cleaner.data[key]['volume'][-1] == cur_bar.current_ohlc['volume']


def test_frequency_generate():
    # 若不指定 frequency， 是否会产生新的 frequency
    set_easy_context()
    StockRecorder()
    reader = CSVReader(data_path='./', file_name=TICKER, ticker=TICKER)
    MarketMaker._initialize_feeds()
    MarketMaker._initialize_calendar()

    cleaner = SMA(rolling_window=10, buffer_day=20)
    cleaner.initialize_buffer_data(TICKER, buffer_day=20)
    assert cleaner.frequency == FREQUENCY


def test_different_frequency():
    set_easy_context()
    StockRecorder()
    reader = CSVReader(data_path='./', file_name=TICKER, ticker=TICKER)
    MarketMaker._initialize_feeds()
    MarketMaker._initialize_calendar()

    cleaner = SMA(rolling_window=10, buffer_day=20, frequency=FREQUENCY)
    cleaner.initialize_buffer_data(TICKER, buffer_day=20)
    key = f'{TICKER}_{FREQUENCY}'

    # 测试不同 frequency 是否会新建 cleaner feed
    assert key+'_'+cleaner.name in reader.env.cleaners_feeds

    # 低 frequency 的 cleaners feed 中 bar 的更新不超过系统 bar 时间
    MarketMaker.env.cur_suspended_tickers.clear()
    MarketMaker.calendar.update_calendar()
    MarketMaker._update_bar()
    cleaner.run()
    cleaner_latest_date = cleaner.data[key]['date'][-1]
    bar_latest_date = cleaner.env.feeds[TICKER].date
    assert arrow.get(cleaner_latest_date) == arrow.get(bar_latest_date)
    assert arrow.get(cleaner_latest_date) <= arrow.get(cleaner.env.sys_date)
    func_test_update_cleaner(FREQUENCY)
    func_test_update_cleaner('H1')


if __name__ == "__main__":
    test_different_frequency()
