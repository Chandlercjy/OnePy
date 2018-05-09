import OnePy as op
from OnePy.sys_module.base_cleaner import CleanerBase


class SMA(CleanerBase):

    def calculate(self, ticker):
        close = self.data[ticker]

        return sum(close)/len(close)  # TODO:尝试用numpy看能否提高性能


if __name__ == "__main__":
    db = op.data_readers.MongodbReader(
        'tushare', '000001', '000001', fromdate='2017-02-12')

    a = SMA(10, 21)
    a.initialize_buffer_data()
    a.calculate('000001')
    print(a.data)
