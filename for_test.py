from OnePy.tools.to_Mongodb import Forex_CSV_to_MongoDB

import OnePy as op

###### save csv to MongoDB
# test = Forex_CSV_to_MongoDB(database='Forex_30m', collection='EUR_JPY')
# test.csv_to_db(path='EUR_JPY30m.csv')




####### Test demo
go = op.OnePiece()

data = op.Forex_CSVFeed(datapath='data/EUR_JPY30m.csv',instrument='EUR_JPY',
                        fromdate='2017-01-01',todate='2017-02-02',
                         timeframe=1)

portfolio = op.PortfolioBase
strategy = op.MyStrategy
broker = op.SimulatedBroker


go.set_backtest([data],[strategy],portfolio,broker)
go.sunny()
