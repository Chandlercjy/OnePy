from functools import partial

import matplotlib.pyplot as plt

import OnePy as op
from OnePy.builtin_module.recorders.stock_recorder import StockRecorder
from OnePy.custom_module.cleaner_sma import SMA


class BuyAndHold(op.StrategyBase):

    def __init__(self):
        super().__init__()
        self.sma1 = SMA(3, 40).calculate
        self.sma2 = SMA(5, 40).calculate

    def handle_bar(self):
        if self.sma1('000001') > self.sma2('000001'):
            self.buy(100, '000001', takeprofit_pct=20)
        else:
            self.sell(60, '000001')

        # self.short_sell(100, '000001', takeprofit=10,
        # stoploss_pct=0.01)
        # self.buy(100, '000001')
        # self.sell(100, '000001', price_pct=0.1)

        # self.short_sell(100, '000001', takeprofit_pct=0.01, stoploss=100)
        # self.short_sell(100, '000001', takeprofit=10)
        # self.short_cover(100, '000001', price_pct=0.2)

        # if self.env.recorder.holding_pnl.latest('000001', 'long') <= 0:
        # self.buy(100, '000001')
        # elif self.env.recorder.holding_pnl.latest('000001', 'long') > 10:
        # self.sell(100, '000001')

    # op.data_readers.CSVReader('./000001.csv', '000001',
    # fromdate=None, todate=None)
op.data_readers.MongodbReader(
    database='tushare', collection='000001', ticker='000001',
    fromdate='2017-02-25', todate='2017-07-09')
BuyAndHold()
op.RiskManagerBase()
op.BrokerBase()
StockRecorder().set_setting(initial_cash=100000,
                            comm=1, comm_pct=None, margin_rate=0.1)
go = op.OnePiece()
go.logger.set_info(False)
go.sunny(False)
# go.output.show_setting()
# go.output.plot('000001')
# print(go.env.gvar.ohlc['000001'][0])
# print(go.env.gvar.position.data['000001_long'][0])
# print(go.env.orders_pending_mkt_dict)
# print(go.env.cleaners)
# recorder.position.plot('000001')
# recorder.balance.plot()
# recorder.realized_pnl.plot('000001')
# print(recorder.realized_pnl)
# print('total re_profit:', recorder.realized_pnl.total_value())
# print('total holding_pnl:', recorder.holding_pnl.total_value())
# print('total commission:', recorder.commission.total_value())
# print(recorder.position.latest('000001', 'long'))
# print(recorder.position)
# plt.show()

# print(go.env.recorder.cash)
# print('readers:', go.env.readers)
# print('feeds:', go.env.feeds)
# print('cleaners:', go.env.cleaners)
# print('strategies:', go.env.strategies)
# print('strategies:', go.gvar.gvar.gvar.gvar)
# print(go.env.event_loop)
# print('signals_normal:',  go.env.signals_normal)
# print('signals_trigger:', go.env.signals_trigger)
# print('orders_original:', go.env.orders_mkt_original)
# print('orders_normal:', go.env.orders_mkt_normal)
# print('orders_absolute:', go.env.orders_mkt_absolute)
# print('orders_pending:', go.env.orders_pending)
# print('order_pending_mkt_dict:', go.env.orders_pending_mkt_dict)
# # print(go.env.event_loop)
