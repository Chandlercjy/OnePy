import csv

from OnePy.sys_mod.base_reader import DataReaderBase


class CSVReader(DataReaderBase):

    def __init__(self,  data_path, ticker, fromdate=None, todate=None):
        super().__init__(ticker, fromdate, todate)
        self.data_path = data_path

    def load(self):
        return csv.DictReader(open(self.data_path))
