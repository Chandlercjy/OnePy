import csv

import arrow

from OnePy.sys_module.base_reader import DataReaderBase
from OnePy.sys_module.models.bar_backtest import BarBacktest


class CSVReader(DataReaderBase):

    def __init__(self,  data_path, ticker, fromdate=None, todate=None):
        super().__init__(ticker, fromdate, todate)
        self.data_path = data_path

    def get_bar(self):
        return BarBacktest(self)

    def _load_raw_data(self):
        return csv.DictReader(open(self.data_path))

    def load(self, fromdate=None, todate=None):
        if fromdate is None:
            fromdate = self.fromdate

        if todate is None:
            todate = self.todate

        generator = self._load_raw_data()
        final_data = []

        for ohlc in generator:
            if todate:
                if arrow.get(ohlc['date']) >= arrow.get(todate):
                    break

            if arrow.get(ohlc['date']) >= arrow.get(fromdate):
                ohlc['open'] = float(ohlc['open'])
                ohlc['high'] = float(ohlc['high'])
                ohlc['low'] = float(ohlc['low'])
                ohlc['close'] = float(ohlc['close'])
                ohlc['volume'] = float(ohlc['volume'])

                final_data.append(ohlc)
        final_generator = (i for i in final_data)
        del final_data

        return final_generator
