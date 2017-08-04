import matplotlib.pyplot as plt
import OnePy as op

class MyStrategy(op.StrategyBase):
        # 可用参数：
        #     list格式： self.cash, self.position, self.margin,
        #                self.total, self.unre_profit
    def __init__(self,marketevent):
        super(MyStrategy,self).__init__(marketevent)

    def prenext(self):
        # print(self.unre_profit[-1])
        pass

    def next(self):
        """这里写主要的策略思路"""
        if self.i.SMA(period=30, index=-1) > self.i.SMA(period=50,index=-1):
            if self.unre_profit[-1] <= 0:
                self.Buy(0.1,takeprofit=self.pips(200),stoploss=self.pct(1),
                             trailingstop=self.pips(60))
        else:
            self.Sell(0.05,price=self.pips(50),takeprofit=self.pips(200),
                           stoploss=self.pips(200),trailingstop=self.pips(60))

            if self.unre_profit[-2] > self.unre_profit[-1] and self.unre_profit[-2] > 100:
                self.Exitall()


go = op.OnePiece()

Forex = op.Forex_CSVFeed(datapath='../data/EUR_USD30m.csv',instrument='EUR_USD',
                        fromdate='2016-04-01',todate='2016-05-01')


data_list = [Forex]

portfolio = op.PortfolioBase
strategy = MyStrategy
broker = op.SimulatedBroker


go.set_backtest(data_list,[strategy],portfolio,broker,'Forex')
go.set_commission(commission=30,margin=325,mult=100000)
go.set_cash(10000)                 # 设置初始资金
# go.set_pricetype(‘close’)        # 设置成交价格为close，若不设置，默认为open
go.set_notify()                    # 打印交易日志


go.sunny()                         # 开始启动策略

# print(go.get_tlog())                # 打印交易日志
go.get_analysis('EUR_USD')
go.plot(instrument='EUR_USD',notebook=False)
# 简易的画图，将后面想要画的选项后面的 1 删掉即可
# go.oldplot(['un_profit','re_profit','position1','cash1','total','margin1','avg_price1'])
