import OnePy as op

# 运行前请确保已经将 MongoDB 的服务打开
# test = op.Tushare_csv_to_MongoDB(database='tushare', collection='000001')
# test.data_to_db(path='../data/000001.csv')     # 输入csv文件路径

test2 = op.Forex_csv_to_MongoDB(database='EUR_USD', collection='M30')
test2.data_to_db(path='../data/EUR_USD30m.csv')     # 输入csv文件路径
