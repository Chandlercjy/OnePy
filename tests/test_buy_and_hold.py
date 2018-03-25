from collections import Counter

import OnePy as op
from OnePy.core.base_broker import BrokerBase
from OnePy.core.base_cleaner import CleanerBase
from OnePy.core.base_reader import DataReaderBase
from OnePy.core.base_recorder import RecorderBase
from OnePy.core.base_riskmanager import RiskManagerBase
from OnePy.core.base_strategy import StrategyBase
from OnePy.core.components import MarketMaker, SignalGenerator
from OnePy.environment import Environment
from OnePy.event import EVENT, Event
from OnePy.model.bar import Bar
from OnePy.utils.awesome_func import dict_to_table
from OnePy.utils.easy_func import execute_run_func
from OnePy.variables import GlobalVariables


class BuyAndHold(op.StrategyBase):

    def __init__(self):
        """TODO: to be defined1. """
        super().__init__(self)
        CleanerBase('ddd')  # indicator

    def pre_trading(self):
        pass

    def handle_bar(self):
        self.buy(100, '000001', takeprofit=100, stoploss_pct=0.01)
        self.sell(100, '000001', price=99)
        self.short_sell(100, '000001')
        self.short_cover(100, '000001')
        # print(self.gvar.feed['000001'].date)
        # print(self.gvar.feed['000001'].execute_price)

    def after_trader(self):
        pass


go = op.OnePiece()
op.data_reader.CSVReader('./000001.csv', '000001')
op.data_reader.CSVReader('./000001.csv', '000002')

BuyAndHold()
RiskManagerBase()
BrokerBase()
RecorderBase()


go.sunny()

# print('readers:', go.env.readers)
# print('feeds:', go.env.feeds)
# print('cleaners:', go.env.cleaners)
# print('strategies:', go.env.strategies)

# print('signals:', go.env.signals)
# aa = go.env.signals[0]
# print(dict_to_table({k: str(v) for k, v in aa.items()}))
# print('signals_current:', go.env.signals_current)
print('orders:', go.env.orders_mkt_original)
print('orders:', go.env.orders_mkt)
print('orders_pending:', go.env.orders_pending)
print('order_pending_mkt_dict:', go.env.orders_pending_mkt_dict)
# print('recorders:', go.env.recorders)
# go.show_setting()

# print(go.env.event_loop)
