from OnePy.tools.to_Mongodb import Forex_CSV_to_MongoDB
import OnePy as op

###### save csv to MongoDB
# test = Forex_CSV_to_MongoDB(database='Forex_30m', collection='EUR_JPY')
# test.csv_to_db(path='EUR_JPY30m.csv')




####### Test demo
go = op.OnePiece()

data = op.Forex_CSVFeed(datapath='data/EUR_JPY30m.csv',name='EUR_JPY',
                         timeframe=1)


go.adddata(data)
go.sunny()
