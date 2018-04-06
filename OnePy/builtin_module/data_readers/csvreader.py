import csv

import arrow

from OnePy.sys_module.base_reader import DataReaderBase
from OnePy.sys_module.models.bars import Bar


class CSVReader(DataReaderBase):

    def __init__(self,  data_path, ticker, fromdate=None, todate=None):
        super().__init__(ticker, fromdate, todate)
        self.data_path = data_path

    def load(self):
        return self.roll_to_fromdate() if self.fromdate else self.load_raw_data()

    def get_bar(self):
        return Bar(self)

    def load_raw_data(self):
        return csv.DictReader(open(self.data_path))

    def roll_to_fromdate(self):
        generator = self.load_raw_data()
        date = next(generator)['date']

        while arrow.get(self.fromdate) > arrow.get(date):
            date = next(generator)['date']

        return generator
