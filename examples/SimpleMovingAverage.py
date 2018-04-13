
import OnePy as op
from OnePy.builtin_module.recorders.stock_recorder import StockRecorder
from OnePy.custom_module.cleaner_sma import SMA


class SmaStrategy(op.StrategyBase):

    def __init__(self):

        super().__init__()
        self.sma1 = SMA(3, 40).calculate
        self.sma2 = SMA(5, 40).calculate

        self.sma3 = SMA(15, 40).calculate
        self.sma4 = SMA(30, 60).calculate

    def handle_bar(self):
        if self.sma1('000001') > self.sma2('000001'):
            self.buy(100, '000001', takeprofit=15,
                     stoploss=100, trailingstop_pct=0.1)
        else:
            self.sell(100, '000001')

        if self.sma3('000001') < self.sma4('000001'):
            self.short_sell(100, '000001', takeprofit=15,
                            stoploss=100, trailingstop_pct=0.1)
        else:
            self.short_cover(100, '000001')


# cleaner暂时不支持CSVReader
    # op.data_readers.CSVReader('./000001.csv', '000001',
    # fromdate=None, todate=None)
op.data_readers.MongodbReader(
    database='tushare', collection='000001', ticker='000001',
    fromdate='2017-05-25', todate='2018-03-09')

SmaStrategy()

op.RiskManagerBase()
op.BrokerBase()

StockRecorder().set_setting(initial_cash=100000,
                            comm=1, comm_pct=None, margin_rate=0.1)
go = op.OnePiece()
# go.logger.set_info(file=False)
go.sunny()
# go.output.show_setting()
go.output.plot('000001')
# print(go.output.trade_log())
