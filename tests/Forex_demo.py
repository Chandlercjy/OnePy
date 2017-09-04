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
        if self.i.SMA(period=30, index=-1) > self.i.SMA(period=50, index=-1):
            if self.unrealizedPL[-1] <= 0:
                self.buy(0.1, takeprofit=self.pips(200),  # 设置止盈为200个pips，不可为负
                         stoploss=self.pct(1),  # 设置止损为成交价的1%，不可为负
                         trailingstop=self.pips(60))  # 设置追踪止损，盈利时触发
        else:
            self.sell(0.05, price=self.pips(50),  # 设置挂单，默认为第二天open价格加50点，也可为负数
                      takeprofit=self.pips(200),
                      stoploss=self.pips(200),
                      trailingstop=self.pips(60))

            if self.unrealizedPL[-2] > self.unrealizedPL[-1] and self.unrealizedPL[-2] > 100:
                self.exitall()  # 设置浮亏浮盈大于100元且出现下降时清仓


go = op.OnePiece()

Forex = op.ForexCSVFeed(datapath='../data/EUR_USD30m.csv', instrument='EUR_USD',
                        fromdate='2012-04-01', todate='2012-05-01')

# 注意若要用MongoDB_Backtest_Feed，先运行tests里面的csv_to_MongoDB.py，推荐用MongoDB
# Forex = op.MongoDB_Backtest_Feed(database='EUR_USD', collection='M30',
#                                  fromdate='2012-04-01', todate='2012-05-01')

data_list = [Forex]

portfolio = op.Portfolio
strategy = MyStrategy

go.set_backtest(data_list, [strategy], portfolio, 'Forex')
go.set_commission(commission=10, margin=325, mult=100000)
go.set_cash(100000)  # 设置初始资金
# go.set_pricetype(‘close’)        # 设置成交价格为close，若不设置，默认为open
go.set_notify()  # 打印交易日志

go.sunny()  # 开始启动策略

print(go.get_tlog('EUR_USD'))  # 打印交易日志
go.get_analysis('EUR_USD')
go.plot(instrument='EUR_USD', notebook=False)
