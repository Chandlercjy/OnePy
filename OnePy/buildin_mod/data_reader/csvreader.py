import csv

from OnePy.environment import Environment
from OnePy.sys_mod.base_reader import DataReaderBase
from OnePy.sys_model.bars import Bar
from OnePy.utils.clean import make_it_datetime, make_it_float
from OnePy.variables import GlobalVariables


class CSVReader(DataReaderBase):

    def __init__(self,  data_path, ticker, fromdate=None, todate=None):
        super().__init__(ticker, fromdate, todate)
        self.data_path = data_path

    def load(self):
        return csv.DictReader(open(self.data_path))

    @property
    def bar(self):
        return Bar(self)
