import OnePy as op


class MyStrategy(op.StrategyBase):
    def __init__(self, marketevent):
        super(MyStrategy, self).__init__(marketevent)

    def prenext(self):
        """以下条件均可用于next中进行策略逻辑判断"""
        # print(self.position[-1])
        # print(self.margin[-1])
        # print(self.avg_price[-1])
        # print(self.unrealizedPL[-1])
        # print(self.realizedPL[-1])
        # print(self.commission[-1])
        # print(self.cash[-1])
        # print(self.balance[-1])
        pass

    def next(self):
        """这里写主要的策略思路"""
        if self.i.SMA(period=5, index=-1) > self.i.SMA(period=10, index=-1):
            self.buy(200)
        else:
            self.sell(100)


go = op.OnePiece()

data = op.TushareCSVFeed(datapath='../data/000001.csv', instrument='000001',
                            fromdate='2017-01-01', todate='2017-03-01'
                            )
# 注意若要用MongoDB_Backtest_Feed，先运行tests里面的csv_to_MongoDB.py, 推荐用MongoDB
# data = op.MongoDB_Backtest_Feed(database='000001', collection='D',instrument='000001',
#                                  fromdate='2017-01-01', todate='2017-03-01')

data_list = [data]
portfolio = op.Portfolio
strategy = MyStrategy

go.set_backtest(data_list, [strategy], portfolio, 'Stock')  # 股票模式
go.set_commission(commission=0.001, margin=0, mult=1)

go.set_cash(100000)  # 设置初始资金
# go.set_pricetype(‘close’)        # 设置成交价格为close，若不设置，默认为open
go.set_notify()  # 打印交易日志

go.sunny()  # 开始启动策略
print(go.get_tlog('000001'))  # 打印交易记录
# go.get_analysis('000001')# Stock的get_analysis暂时不可用
go.plot(instrument='000001')
