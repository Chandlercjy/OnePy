import logging
import time
from datetime import timedelta

import arrow

from OnePy.sys_module.models.base_bar import BarBase
from OnePy.utils.easy_func import get_day_ratio


class OandaBar(BarBase):

    def initialize(self, buffer_day=None) -> bool:
        reader = self.env.readers[self.ticker]
        ohlc_list = reader.load(count=3)
        self.previous_ohlc = ohlc_list[0]
        self.current_ohlc = ohlc_list[1]
        self.next_ohlc = ohlc_list[2]

        return True

    def next_directly(self):
        ohlc_list = self.get_brand_new_ohlc_list()
        self.previous_ohlc = self.current_ohlc

        for ohlc in ohlc_list:
            if ohlc['complete']:
                self.current_ohlc = ohlc
            else:
                self.next_ohlc = ohlc

    def get_brand_new_ohlc_list(self):
        ratio = get_day_ratio(self.frequency)
        reader = self.env.readers[self.ticker]
        ohlc_list = reader.load()

        while self.current_ohlc in ohlc_list and len(ohlc_list) == 2:
            self.check_if_weekday()

            if (arrow.utcnow() - arrow.get(self.date)) >= timedelta(ratio * 2):
                ohlc_list = reader.load()
            time.sleep(1)

        return ohlc_list

    def check_if_weekday(self):
        now = arrow.utcnow()
        weekday = now.format('dddd')

        if weekday not in ['Friday', 'Saturday', 'Sunday']:
            return

        logger = logging.getLogger('OnePy')
        date = now.format('YYYY-MM-DD')
        market_is_opened = False

        while True:
            if weekday == 'Friday':
                if now < arrow.get(f'{date} 20:45'):
                    break

            elif weekday == 'Sunday':
                if now > arrow.get(f'{date} 21:00'):
                    break

            if not market_is_opened:
                logger.warning(
                    f'Now is {now} Market is closed! I am gonna sleep~')

            market_is_opened = True
            now = arrow.utcnow()
            weekday = now.format('dddd')
            date = now.format('YYYY-MM-DD')
            time.sleep(1)

        if market_is_opened:
            logger.warning(
                f'Now is {now}. Market is opened! The weather is very good!')

    @property
    def cur_price(self):
        return self.close

    @property
    def execute_price(self):
        if self.env.execute_on_close_or_next_open == 'open':
            return float(self.next_ohlc['open'])

        return self.close

    @property
    def date(self):
        return str(self.current_ohlc['date'])

    @property
    def open(self):
        return float(self.current_ohlc['open'])

    @property
    def high(self):
        return float(self.current_ohlc['high'])

    @property
    def low(self):
        return float(self.current_ohlc['low'])

    @property
    def close(self):
        return float(self.current_ohlc['close'])

    @property
    def volume(self):
        return float(self.current_ohlc['volume'])
