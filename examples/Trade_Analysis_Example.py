import OnePy as op
from OnePy.custom_module.cleaner_sma import SMA

class SmaStrategy(op.StrategyBase):

    def __init__(self):

        super().__init__()
        self.sma1 = SMA(3, 40).calculate
        self.sma2 = SMA(5, 40).calculate

    def handle_bar(self):
        for ticker in self.env.tickers:

            if self.sma1(ticker) > self.sma2(ticker):

                self.buy(100, ticker, takeprofit=15,
                         stoploss=100)
            else:
                self.sell(100, ticker)


TICKER_LIST = ['000001', '000002'] # 多品种
INITIAL_CASH = 20000
FREQUENCY = 'D'
START, END = '2012-08-07', '2018-08-07'

SmaStrategy()

# 用MongoDB数据库回测
go = op.backtest.stock(TICKER_LIST, FREQUENCY, INITIAL_CASH, START, END)

go.sunny()
go.output.plot('000001')
go.output.analysis.trade_analysis()
