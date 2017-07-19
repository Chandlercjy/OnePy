#coding=utf8

from OnePy.tools.to_Mongodb import Forex_CSV_to_MongoDB

import OnePy as op

###### save csv to MongoDB
# test = Forex_CSV_to_MongoDB(database='Forex_30m', collection='EUR_JPY')
# test.csv_to_db(path='EUR_JPY30m.csv')


####### Plot
import pandas as pd
import matplotlib.pyplot as plt
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
        if abs(self.margin[-1]/self.total[-1]) < 0.1:
            if self.data['close'] > self.data['open']:
                self.Buy(0.01,limit =self.pips(20),stop=self.pips(40))
                # self.Buy(1,limit =self.pips(200),price=self.data['open']*1.02)

            # else:
            #     self.Sell(1, limit = self.pips(200))
        # else:
        #     self.Exitall()

go = op.OnePiece()

data = op.Forex_CSVFeed(datapath='data/EUR_USD30m.csv',instrument='EUR_JPY',
                        fromdate='2012-02-01',todate='2012-05-10',
                         timeframe=1)
# data2 = op.Forex_CSVFeed(datapath='data/EUR_USD30m.csv',instrument='EUR_JPY2',
#                         fromdate='2012-02-01',todate='2012-03-10',
#                          timeframe=1)


data_list = [data]
portfolio = op.PortfolioBase
strategy = MyStrategy
broker = op.SimulatedBroker

go.set_backtest(data_list,strategy,portfolio,broker)
go.set_commission(commission=1,margin=325,mult=100000)
go.set_cash(100000)
go.set_notify()

go.sunny()
