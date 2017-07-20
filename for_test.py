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
        if abs(self.margin[-1]/self.total[-1]) < 0.1:
            if self.data['close'] < self.data['open']:
                # self.Buy(0.04)
                self.Buy(0.1,limit =self.pips(20),stop=self.pips(40))

            # if self.data['open'] == self.data['low']:
            #     self.Sell(0.2, limit = self.pips(200))
            # if self.data['open'] == self.data['low']:
                # self.Exitall() # 问题：1.退出的话打印有问题 2. 仓位有问题
        if self.unre_profit[-1] > 1000:
            self.Exitall()


go = op.OnePiece()

data = op.Forex_CSVFeed(datapath='data/EUR_USD30m.csv',instrument='EUR_JPY',
                        fromdate='2012-02-01',todate='2012-03-10',
                         timeframe=1)

data_list = [data]
portfolio = op.PortfolioBase
strategy = MyStrategy
broker = op.SimulatedBroker

go.set_backtest(data_list,[strategy],portfolio,broker)
go.set_commission(commission=30,margin=325,mult=100000)
go.set_cash(100000)
go.set_notify()

go.sunny()
# go.plot(['margin','position'])
go.plot(['un_profit','re_profit','position'])
# go.plot(['cash','total'])
# print go.fill.re_profit_dict['EUR_JPY'][-2]
