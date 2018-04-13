import OnePy as op
from OnePy.builtin_module.recorders.stock_recorder import StockRecorder
from OnePy.custom_module.cleaner_sma import SMA


class BuyAndHold(op.StrategyBase):

    def handle_bar(self):
        self.buy(100, '000001')


op.data_readers.CSVReader('./000001.csv', '000001', fromdate=None, todate=None)

# op.data_readers.MongodbReader(
# database='tushare', collection='000001', ticker='000001',
# fromdate='2017-02-25', todate='2017-07-09')

BuyAndHold()
op.RiskManagerBase()
op.BrokerBase()

StockRecorder().set_setting(initial_cash=100000,
                            comm=1, comm_pct=None, margin_rate=0.1)
go = op.OnePiece()
go.logger.set_info(file=False)
go.sunny()
# go.output.show_setting()
# go.output.plot('000001')
