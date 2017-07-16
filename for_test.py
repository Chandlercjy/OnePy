from OnePy.tools.to_Mongodb import Forex_CSV_to_MongoDB

import OnePy as op

###### save csv to MongoDB
# test = Forex_CSV_to_MongoDB(database='Forex_30m', collection='EUR_JPY')
# test.csv_to_db(path='EUR_JPY30m.csv')


####### Plot
# import pandas as pd
# import matplotlib.pyplot as plt
#
# df = pd.read_csv('data/EUR_USD30m.csv',parse_dates=True, index_col=0)
# df['Close'].plot()
# plt.show()


####### Test demo
go = op.OnePiece()

data = op.Forex_CSVFeed(datapath='data/EUR_USD30m.csv',instrument='EUR_JPY',
                        fromdate='2014-02-01',todate='2014-05-05',
                         timeframe=1)

portfolio = op.PortfolioBase
strategy = op.MyStrategy
broker = op.SimulatedBroker

go.set_backtest(data,strategy,portfolio,broker)
go.set_commission(commission=1,margin=325,muli=100000)
go.set_cash(100000)
go.sunny()
