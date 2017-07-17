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

    # def prenext(self):
    #     if self.cash[-1] > 200000:
    #         print 'total: ',self.total[-1]
    #         print self.margin[-2]
    #         print 'profit: ',self.profit[-1]
    #         print 'avg: ', self.avg_price[-2]
    #     pass

    def next(self):
        """这里写主要的策略思路"""
        if abs(self.margin[-1]/self.total[-1]) < 0.1:
            if self.data['close'] > self.data['open']:
                self.Buy(1,limit = self.data['close']*1.01,price = self.data['close'] + self.pips(200))
            # else:
            #     self.Sell(1, limit = self.data['close']*0.99)
        else:
            self.Exitall()


"""笔记：记得设置多单limit应大于price等"""

go = op.OnePiece()

data = op.Forex_CSVFeed(datapath='data/EUR_USD30m.csv',instrument='EUR_JPY',
                        fromdate='2012-02-01',todate='2012-03-10',
                         timeframe=1)

portfolio = op.PortfolioBase
strategy = MyStrategy
broker = op.SimulatedBroker

go.set_backtest(data,strategy,portfolio,broker)
go.set_commission(commission=1,margin=325,mult=100000)
go.set_cash(100000)
go.set_notify()
go.sunny()
