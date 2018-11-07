import OnePy as op
from OnePy.builtin_module.backtest_forex.forex_broker import ForexBroker
from OnePy.builtin_module.backtest_forex.forex_recorder import ForexRecorder
from OnePy.builtin_module.backtest_stock.stock_broker import StockBroker
from OnePy.builtin_module.backtest_stock.stock_recorder import StockRecorder

SLIPPAGE = dict(EUR_USD=1.5,
                AUD_USD=1.5,
                GBP_USD=2.0,
                USD_CAD=2.0,
                USD_JPY=1.5)


def forex(ticker_list: list, frequency: str,
          initial_cash: float, start: str, end: str, broker: str='oanda'):

    for ticker in ticker_list:
        op.data_readers.MongodbReader(
            database=f'{ticker}_{broker}', ticker=ticker)

    ForexBroker()

    ForexRecorder().set_setting(initial_cash=initial_cash,
                                margin_rate=0.02,
                                slippage=SLIPPAGE)
    go = op.OnePiece()
    go.set_date(start, end, frequency, 'Forex')

    return go


def stock(ticker_list: list, frequency: str,
          initial_cash: float, start: str, end: str, broker: str='tushare'):

    for ticker in ticker_list:
        op.data_readers.MongodbReader(
            database=f'{ticker}_{broker}', ticker=ticker)

    StockBroker()

    StockRecorder().set_setting(initial_cash=initial_cash,
                                comm=None, comm_pct=0.0016, margin_rate=0.1)

    go = op.OnePiece()
    go.set_date(start, end, frequency, 'A_shares')

    return go
