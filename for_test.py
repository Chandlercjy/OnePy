#coding=utf8

# from OnePy.tools.to_Mongodb import Forex_CSV_to_MongoDB
import pandas as pd
import matplotlib.pyplot as plt
import OnePy as op
from OnePy import indicator as ind
###### save csv to MongoDB Demo
# test = Forex_CSV_to_MongoDB(database='Forex_30m', collection='EUR_JPY')
# test.csv_to_db(path='EUR_JPY30m.csv')

"""声明：目前只开发了 Forex 模式，其他模式缓慢更新ing"""
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
        # if ind.SMA(period=5, index=-1)

        # print self.i
        if self.i.SMA(period=5, index=-1) > self.i.SMA(period=10,index=-1):
            if self.position[-1] == 0:
                self.Buy(1,stop=self.pct(0.2))
        else:
            if self.position[-1] == 1:
                self.Sell(1,limit=self.pips(20),stop=self.pct(1))

go = op.OnePiece()

data = op.Forex_CSVFeed(datapath='data/EUR_USD30m.csv',instrument='EUR_JPY',
                        fromdate='2012-05-01',todate='2012-06-02',
                         timeframe=1)

data_list = [data]
portfolio = op.PortfolioBase
strategy = MyStrategy
broker = op.SimulatedBroker

go.set_backtest(data_list,[strategy],portfolio,broker)
go.set_commission(commission=30,margin=325,mult=100000)
go.set_cash(10000)                 # 设置初始资金

# go.set_notify()                    # 打印交易日志
# go.set_pricetype(‘close’)        # 设置成交价格为close，若不设置，默认为open
go.sunny()                         # 开始启动策略


# 画图模块缓慢开发中，先随意画出价格图
df = pd.DataFrame(go.feed_list[0].bar_dict['EUR_JPY'])
# df.set_index('date',inplace=True)
# df['close'].plot()
# plt.show()
# print df

# 简易的画图，将后面想要画的选项后面的 1 删掉即可
# go.plot(['un_profit1','re_profit1','position1','cash1','total','margin1'])
