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

            self.Buy(2)
        else:
            self.Sell(1)

go = op.OnePiece()


data = op.Futures_CSVFeed(datapath='../data/IF0000_1min.csv',instrument='IF0000',
                        fromdate='2010-04-19',todate='2010-04-20')



data_list = [data]

portfolio = op.PortfolioBase
strategy = MyStrategy
broker = op.SimulatedBroker



go.set_backtest(data_list,[strategy],portfolio,broker,'Futures')     # 期货模式
go.set_commission(commission=15,margin=0.13,mult=10,commtype='FIX')  # 固定手续费
# go.set_commission(commission=0.00025,margin=0.15,mult=10,commtype='PCT')  # 百分比手续费


go.set_cash(10000000)                 # 设置初始资金
# go.set_pricetype(‘close’)        # 设置成交价格为close，若不设置，默认为open
# go.set_notify()                    # 打印交易日志



go.sunny()                         # 开始启动策略

# print go.get_tlog()                # 打印交易记录
go.plot(instrument='IF0000')


# 简易的画图，将后面想要画的选项后面的 1 删掉即可
# go.oldplot(['un_profit','re_profit','position1','cash1','total','margin1','avg_price1'])
