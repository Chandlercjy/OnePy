import OnePy as op
from OnePy.builtin_module.mongodb_saver.tushare_saver import Tushare_to_MongoDB

ticker = "000001"
ktype = "D"
start = "2017-01-01"
end = None

test = Tushare_to_MongoDB(database='tushare', collection=ticker)
test.data_to_db(code=ticker, start=start, end=end,
                ktype=ktype, autype="qfq", index=False)
