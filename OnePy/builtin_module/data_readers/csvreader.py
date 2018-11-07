import csv
from typing import Generator

import arrow

from OnePy.sys_module.base_reader import ReaderBase


class CSVReader(ReaderBase):

    def __init__(self,  data_path, file_name, key=None, ticker=None):
        super().__init__(ticker, key)
        self.data_path = data_path
        self.file_name = file_name

    def _load_raw_data(self, frequency):
        return csv.DictReader(open(f'{self.data_path}{self.file_name}_{frequency}.csv'))

    def load(self, fromdate, todate, frequency):
        generator = self._load_raw_data(frequency)
        final_data = []


        for ohlc in generator:
            if todate:
                if arrow.get(ohlc['date']) > arrow.get(todate):
                    break

            if arrow.get(ohlc['date']) >= arrow.get(fromdate):
                ohlc['open'] = float(ohlc['open'])
                ohlc['high'] = float(ohlc['high'])
                ohlc['low'] = float(ohlc['low'])
                ohlc['close'] = float(ohlc['close'])
                ohlc['volume'] = float(ohlc['volume'])

                final_data.append(ohlc)

        final_generator = (i for i in final_data)

        return final_generator
