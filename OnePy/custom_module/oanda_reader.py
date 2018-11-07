import logging
from typing import Generator

import arrow

from oandakey import access_token, accountID
from OnePy.custom_module.api.oanda_api import OandaAPI
from OnePy.custom_module.oanda_bar import OandaBar
from OnePy.sys_module.base_reader import ReaderBase
from OnePy.sys_module.components.logger import LoggerFactory


class OandaReader(ReaderBase):
    host = 'localhost'
    port = 27017

    def __init__(self, ticker: str, log: bool=True, no_console: bool=True):
        super().__init__(ticker)
        self.ticker = ticker
        if not (accountID and access_token):
            raise Exception("oandakey should hasn't been settled!")

        self.oanda = OandaAPI(accountID, access_token)

        if log:
            LoggerFactory('oandapyV20', info_log=False)

        if no_console:
            logging.getLogger('oandapyV20').propagate = False

    def load(self, fromdate=None, todate=None, frequency=None, count=2):
        return self.get_candles(count)

    def get_candles(self, count: int, frequency: str=None) -> list:
        if not frequency:
            frequency = self.env.sys_frequency
        data = self.oanda.get_candlestick_list(ticker=self.ticker,
                                               granularity=frequency,
                                               count=count)

        return self._format_candle(data)

    def load_by_cleaner(self, fromdate: str, todate: str,
                        frequency: str) -> Generator:

        return (i for i in self.get_candles(5000, frequency))

    @staticmethod
    def _format_candle(candle_data: list):
        ohlc_list = []

        for candle in candle_data['candles']:
            ohlc = candle['mid']
            ohlc['open'] = float(ohlc.pop("o"))
            ohlc['high'] = float(ohlc.pop("h"))
            ohlc['low'] = float(ohlc.pop("l"))
            ohlc['close'] = float(ohlc.pop("c"))

            ohlc['date'] = arrow.get(candle['time']).format(
                "YYYY-MM-DD HH:mm:ss")
            ohlc['volume'] = float(candle['volume'])
            ohlc['complete'] = candle['complete']
            ohlc_list.append(ohlc)

        return ohlc_list

    @property
    def bar_class(self):
        raise OandaBar
