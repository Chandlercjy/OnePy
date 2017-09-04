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
            self.buy(2)
        else:
            self.sell(1)


go = op.OnePiece()
data = op.FuturesCSVFeed(datapath='../data/IF0000_1min.csv', instrument='IF0000',
                            fromdate='2010-04-19', todate='2010-04-20')

# 注意若要用MongoDB_Backtest_Feed，请自己研究参考下Forex和Stock的demo，然后照抄过来：）


data_list = [data]
portfolio = op.Portfolio
strategy = MyStrategy

go.set_backtest(data_list, [strategy], portfolio, 'Futures')  # 期货模式
go.set_commission(commission=15, margin=0.13, mult=10, commtype='FIX')  # 固定手续费
# go.set_commission(commission=0.00025,margin=0.15,mult=10,commtype='PCT')  # 百分比手续费

go.set_cash(1000000)  # 设置初始资金
# go.set_executemode("close")        # 设置成交价格为close，若不设置，默认为open
go.set_notify()  # 打印交易日志

go.sunny()  # 开始启动策略
# go.get_analysis('IF0000')         # Futures的get_analysis暂时不可用
print(go.get_tlog('IF0000'))  # 打印交易记录
go.plot(instrument='IF0000')
