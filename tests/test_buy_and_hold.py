import OnePy as op
from OnePy.buildin_mod.recorders.stock_recorder import StockRecorder
from OnePy.config import SYS_MOD
from OnePy.sys_mod.base_broker import BrokerBase
from OnePy.sys_mod.base_cleaner import CleanerBase
from OnePy.sys_mod.base_recorder import RecorderBase
from OnePy.sys_mod.base_riskmanager import RiskManagerBase


class BuyAndHold(op.StrategyBase):

    def __init__(self):
        """TODO: to be defined1. """
        super().__init__(self)
        CleanerBase('ddd')  # indicator

    def pre_trading(self):
        pass

    def handle_bar(self):
        # self.buy(100, '000001', takeprofit=100,
                 # stoploss_pct=0.01, price_pct=-0.01)
        self.buy(100, '000001', price_pct=-0.01, takeprofit=10)
        # self.sell(100, '000001')
        # self.short_sell(100, '000001', takeprofit_pct=0.01)
        # self.short_cover(100, '000001')

    def after_trader(self):
        pass


op.data_reader.CSVReader('./000001.csv', '000001')
op.data_reader.CSVReader('./000001.csv', '000002')

go = op.OnePiece()
BuyAndHold()
RiskManagerBase()
BrokerBase()
StockRecorder()
# go.show_setting()
go.sunny()
# print('readers:', go.env.readers)
# print('feeds:', go.env.feeds)
# print('cleaners:', go.env.cleaners)
# print('strategies:', go.env.strategies)
# print('strategies:', go.gvar.gvar.gvar.gvar)
# print(go.env.event_loop)
print('signals_normal:', go.env.signals_normal)
print('signals_trigger:', go.env.signals_trigger)
print('orders_original:', go.env.orders_mkt_original)
print('orders_normal:', go.env.orders_mkt_normal)
print('orders_absolute:', go.env.orders_mkt_absolute)
print('orders_pending:', go.env.orders_pending)
print('order_pending_mkt_dict:', go.env.orders_pending_mkt_dict)
# print(go.env.event_loop)
