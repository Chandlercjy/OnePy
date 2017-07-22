#coding=utf8

from OnePy.tools.to_Mongodb import Forex_CSV_to_MongoDB



###### save csv to MongoDB Demo
test = Forex_CSV_to_MongoDB(database='Forex_30m', collection='EUR_JPY')
test.csv_to_db(path='EUR_JPY30m.csv')     # 输入csv文件路径
