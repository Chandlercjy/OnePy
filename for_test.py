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

    def prenext(self):
        # print sum(self.re_profit)
        # print self.unre_profit[-1]
        pass

    def next(self):
        """这里写主要的策略思路"""

        if len(self.close) > 30:
            if sum(self.close[-10:])/10 > sum(self.close[-30:])/30:
                if self.position[-1] == 0:
                    self.Buy(1)
            else:
                if self.position[-1] == 0.1:
                    self.Sell(1)
        # print self.cash[-1]
        # if self.data['open'] == self.data['low']:
        #     self.Sell(0.2, limit = self.pips(200))
        # if self.data['open'] == self.data['low']:
        #     self.Exitall() # 问题：1.退出的话打印有问题 2. 仓位有问题
        # if self.unre_profit[-1] < -1000 or self.unre_profit[-1] > 1500:
        #     self.Exitall()


go = op.OnePiece()

data = op.Forex_CSVFeed(datapath='data/EUR_USD30m.csv',instrument='EUR_JPY',
                        fromdate='2012-01-01',todate='2012-05-01',
                         timeframe=1)

data_list = [data]
portfolio = op.PortfolioBase
strategy = MyStrategy
broker = op.SimulatedBroker

go.set_backtest(data_list,[strategy],portfolio,broker)
go.set_commission(commission=30,margin=325,mult=100000)
go.set_cash(10000)
# go.set_notify()
# go.set_pricetype()
go.sunny()
# go.plot(['margin','position'])


df = pd.DataFrame(go.feed_list[0].bar_dict['EUR_JPY'])
df.set_index('date',inplace=True)
df['close'].plot()
# plt.show()
go.plot(['un_profit1','re_profit1','position','cash1','total'])
