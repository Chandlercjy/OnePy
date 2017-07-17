#coding=utf8

from OnePy.tools.to_Mongodb import Forex_CSV_to_MongoDB

import OnePy as op

###### save csv to MongoDB
# test = Forex_CSV_to_MongoDB(database='Forex_30m', collection='EUR_JPY')
# test.csv_to_db(path='EUR_JPY30m.csv')


####### Plot
# import pandas as pd
# import matplotlib.pyplot as plt
#
# df = pd.read_csv('data/EUR_USD30m.csv',parse_dates=True, index_col=0)
# df['Close'].plot()
# plt.show()


####### Test demo
class MyStrategy(op.StrategyBase):
    def __init__(self,marketevent):
        super(MyStrategy,self).__init__(marketevent)

    def next(self):
        """这里写主要的策略思路"""
        if self.data['close'] > self.data['open']:
            if self.margin[self.instrument][-1]['margin']/self.total < 0.1:
                self.Buy(1,limit = self.data['close']*1.01)
        else:
            if self.margin[self.instrument][-1]['margin']/self.total < 0.1:
                self.Sell(1, limit = self.data['close']*0.99)

"""笔记：记得设置多单limit应大于price等"""

go = op.OnePiece()

data = op.Forex_CSVFeed(datapath='data/EUR_USD30m.csv',instrument='EUR_JPY',
                        fromdate='2012-02-01',todate='2015-05-05',
                         timeframe=1)

portfolio = op.PortfolioBase
strategy = MyStrategy
broker = op.SimulatedBroker

go.set_backtest(data,strategy,portfolio,broker)
go.set_commission(commission=1,margin=325,muli=100000)
go.set_cash(100000)
# go.set_notify()
go.sunny()
