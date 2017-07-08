import talib.abstract as tb
import pandas as pd
import OnePy as op
import itertools

class MyStrategy(op.Strategy):
    def __init__(self,portfolio,p_list):
        super(MyStrategy,self).__init__(portfolio)
        self.sma1, \
        self.sma2 = p_list


    def luffy(self):
        for s in self.symbol_list:

            sma1=self.indicator(tb.SMA, s, self.sma1, select=[-1],add=9)
            sma2=self.indicator(tb.SMA, s, self.sma2, select=[-1],add=19)
            # if len(self.latest_bar_dict[s])>20:
            #     sma1 = pd.DataFrame(self.latest_bar_dict[s][-10:])['close'].rolling(10).mean().iat[-1]
            #     sma2 = pd.DataFrame(self.latest_bar_dict[s][-20:])['close'].rolling(20).mean().iat[-1]

            if sma1 > sma2 and self.deposit_ratio < 3:
                self.long(s,lots=0.1,percent=False,risky=True)
                # self.exitall(s)
            if sma1 < sma2 or (self.long_profit > 100) or (self.long_profit < (-300)):
                self.exitall(s)
                # self.short(s,lots=0.1,risky=True)#,strength=2,percent=True,risky=True)


df = pd.read_csv('EUR_USD_30m.csv',parse_dates=True,index_col=0)
symbol_list = ['EUR_USD']
# data = op.csv_reader('/Users/chandler/Desktop/stock/data_csv', symbol_list,start='2016')
data = op.DataFrame_reader(df, symbol_list,start='2017-05-01', caps=True)

portfolio = op.NaivePortfolio(data,initial_capital=200000)
strategy = MyStrategy(portfolio,[10,20])

go = op.OnePiece(strategy)

go.print_trade()
go.set_commission(2)
go.print_stats()
go.sunny()
go.plot(symbol_list)
#
#
