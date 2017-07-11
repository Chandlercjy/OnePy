from OnePy.tools.to_Mongodb import Forex_CSV_to_MongoDB


# save csv to MongoDB
test = Forex_CSV_to_MongoDB(database='Forex_30m', collection='EUR_JPY')
# test.csv_to_db(path='EUR_JPY30m.csv')
