import OnePy as op
from OnePy.sys_module.base_cleaner import CleanerBase


class SMA(CleanerBase):

    def __init__(self,  length=None, buffer_day=None):
        super().__init__(length, buffer_day)

    def run(self):
        super().run()

    def calculate(self, ticker):
        close = self.data[ticker]

        return sum(close)/len(close)


if __name__ == "__main__":
    db = op.data_readers.MongodbReader(
        'tushare', '000001', '000001', fromdate='2017-02-12')

    a = SMA(10, 21)

    a.calculate('000001')
    print(a.data)
