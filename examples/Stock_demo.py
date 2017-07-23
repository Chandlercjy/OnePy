#coding=utf8
import pandas as pd
import matplotlib.pyplot as plt
import OnePy as op


####### Strategy Demo
class MyStrategy(op.StrategyBase):
        # 可用参数：
        #     list格式： self.cash, self.position, self.margin,
        #                self.total, self.unre_profit
    def __init__(self,marketevent):
        super(MyStrategy,self).__init__(marketevent)

    def prenext(self):
        # print sum(self.re_profit)
        # print self.unre_profit[-1]
        pass

    def next(self):
        """这里写主要的策略思路"""

        if self.i.SMA(period=5, index=-1) > self.i.SMA(period=10,index=-1):

            self.Buy(200)
        else:
            self.Sell(100)

go = op.OnePiece()

data = op.Tushare_CSVFeed(datapath='../data/000001.csv',instrument='000001',
                        # fromdate='2012-03-01',todate='2012-04-02',
                         timeframe=1)




data_list = [data]

portfolio = op.PortfolioBase
strategy = MyStrategy
broker = op.SimulatedBroker


go.set_backtest(data_list,[strategy],portfolio,broker,'Stock')   # 股票模式
go.set_commission(commission=0.01,margin=0,mult=1)


# go.set_commission(commission=10,margin=325,mult=100000)
go.set_cash(10000)                 # 设置初始资金
# go.set_pricetype(‘close’)        # 设置成交价格为close，若不设置，默认为open
# go.set_notify()                    # 打印交易日志



go.sunny()                         # 开始启动策略

# print go.get_tlog()                # 打印交易记录
go.plot(instrument='000001')


# 简易的画图，将后面想要画的选项后面的 1 删掉即可
# go.oldplot(['un_profit','re_profit','position1','cash1','total','margin1','avg_price1'])
