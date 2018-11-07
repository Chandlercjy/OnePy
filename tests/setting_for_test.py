import arrow

import OnePy as op
from OnePy import StockBroker
from OnePy.builtin_module.backtest_stock.stock_recorder import StockRecorder
from OnePy.environment import Environment

MODE = 1

if MODE == 1:
    INSTRUMENT = 'A_shares'
    TICKER = '000001'
    BROKER = 'tushare'
    FREQUENCY = 'D'
elif MODE == 2:
    INSTRUMENT = 'Forex'
    TICKER = 'EUR_USD'
    BROKER = 'oanda'
    FREQUENCY = 'D'
elif MODE == 3:
    INSTRUMENT = 'Forex'
    TICKER = 'EUR_USD'
    BROKER = 'oanda'
    FREQUENCY = 'H1'


START = '2018-03-07'
END = '2018-03-14'


DATABASE = f'{TICKER}_{BROKER}'
COLLECTION = FREQUENCY


def shift_date(date, num_days):
    return arrow.get(date).shift(days=num_days).format("YYYY-MM-DD HH:mm:ss")


class DemoStrategy(op.StrategyBase):

    def handle_bar(self):
        pass


def set_easy_context():
    Environment.clear_modules()
    Environment.fromdate = START
    Environment.todate = END
    Environment.sys_frequency = FREQUENCY
    Environment.instrument = INSTRUMENT
    Environment.initialize_env()


def global_setting():
    set_easy_context()
    op.data_readers.CSVReader(data_path='./', file_name=TICKER, ticker=TICKER)
    # op.data_readers.MongodbReader(database=DATABASE, ticker=TICKER)
    DemoStrategy()
    StockBroker()
    StockRecorder().set_setting(initial_cash=100000,
                                comm=1, comm_pct=None, margin_rate=0.1)
    go = op.OnePiece()
    go.set_date(START, END, FREQUENCY, INSTRUMENT)
    go.initialize_trading_system()

    return go
