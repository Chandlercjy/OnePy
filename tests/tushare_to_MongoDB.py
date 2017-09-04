import OnePy as op

instrument = "000001"
ktype = "D"
start = "2017-01-01"
end = None

test = op.Tushare_to_MongoDB(database=instrument, collection=ktype)
test.data_to_db(code=instrument, start=start, end=end, ktype=ktype, autype="qfq", index=False)
