from collections import Counter

import OnePy as op
from OnePy.core.base_cleaner import CleanerBase


class BuyAndHold(op.StrategyBase):

    def __init__(self):
        """TODO: to be defined1. """
        super().__init__(self)

    def pre_trading(self):
        pass

    def handle_bar(self):
        self.buy(100, '000001')
        print(self.gvar.feed['000001'].date)
        # print(self.gvar.feed['000001'].execute_price)

    def after_trader(self):
        pass


go = op.OnePiece()
op.data_reader.CSVReader('./000001.csv', '000001')

BuyAndHold()
CleanerBase('ddd')

go.sunny()

print('readers:', go.env.readers)
print('feeds:', go.env.feeds)
print('cleaners:', go.env.cleaners)
print('strategies:', go.env.strategies)
print('order_list:', go.env.order_list)
# print(go.env.event_loop)
