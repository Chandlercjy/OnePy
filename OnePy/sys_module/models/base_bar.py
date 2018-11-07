from copy import copy
from typing import Generator

import arrow

from OnePy.sys_module.metabase_env import OnePyEnvBase
from OnePy.utils.easy_func import format_date, get_day_ratio


class BarBase(OnePyEnvBase):

    def __init__(self, ticker: str, frequency: str) -> None:
        self.frequency = frequency
        self.ticker: str = ticker

        self._iter_data: Generator = None
        self.previous_ohlc: dict = None
        self.current_ohlc: dict = None
        self.next_ohlc: dict = None

    @property
    def cur_price(self) -> float:
        return self.close

    @property
    def execute_price(self) -> float:
        if self.env.execute_on_close_or_next_open == 'open':
            return self.next_ohlc['open']

        return self.close

    @property
    def date(self) -> str:
        return self.current_ohlc['date']

    @property
    def open(self) -> float:
        return self.current_ohlc['open']

    @property
    def high(self) -> float:
        return self.current_ohlc['high']

    @property
    def low(self) -> float:
        return self.current_ohlc['low']

    @property
    def close(self) -> float:
        return self.current_ohlc['close']

    @property
    def volume(self) -> float:
        return self.current_ohlc['volume']

    def is_suspended(self) -> bool:  # 判断明天是否停牌
        now = arrow.get(self.env.sys_date)
        tomorrow = arrow.get(self.next_ohlc['date'])

        if tomorrow <= now:
            return False

        return True

    def next(self):
        """更新行情"""

        if self.is_suspended():
            self.env.cur_suspended_tickers.append(self.ticker)
            self.env.suspended_tickers_record[self.ticker].append(
                self.env.sys_date)
        else:
            self.next_directly()

    def next_directly(self):
        """不判断，直接next到下一个数据"""
        self.previous_ohlc = self.current_ohlc
        self.current_ohlc = self.next_ohlc
        self.next_ohlc = next(self._iter_data)

    def initialize(self, buffer_day: int) -> bool:
        sys_date = self.env.sys_date
        start = arrow.get(self.env.fromdate).shift(
            days=-buffer_day).format('YYYY-MM-DD HH:mm:ss')
        end = format_date(self.env.todate)

        if buffer_day > 500:  # 为了构建pre_ohlc而load,若生成不了就删除
            self._delete_ohlc('Delete OHLC for PRE_OHLC')

            return False

        if self._iter_data is None:  # 加载数据并初始化
            self._update_iter_data(start, end)

            try:
                for i in range(3):
                    self.next_directly()
            except StopIteration:
                self._delete_ohlc('Delete OHLC for ALL')

                return False

        while arrow.get(self.next_ohlc.get('date')) <= arrow.get(sys_date):
            try:
                self.next_directly()  # sys_date为fromdate前一个周期,所以重复load数据到next_ohlc为fromdate
            except StopIteration:
                self._delete_ohlc('Delete OHLC for SOME')

                return False

        if arrow.get(self.previous_ohlc['date']) >= arrow.get(sys_date):
            buffer_day += 300       # 更新好后，若当前pre_ohlc数据不对，表明
            self._iter_data = None  # next_ohlc数据也不对，要重新load

            return self.initialize(buffer_day)

        return True

    def _update_iter_data(self, start: str, end: str):
        reader = self.env.readers[self.ticker]
        self._iter_data = reader.load(start, end, self.frequency)

    def _delete_ohlc(self, message: str):
        """删除数据,并记录"""
        del self.env.readers[self.ticker]
        self.env.logger.warning(
            f'Delete {self.ticker}_{self.frequency} for lack of {message}!!!!')
        self.env.cur_suspended_tickers.append(self.ticker)
        self.env.suspended_tickers_record[self.ticker].append(
            self.env.sys_date)

    def move_next_ohlc_to_cur_ohlc(self):
        """
        用于伪造最新的next bar，骗过系统产生最新日期的信号
        会导致回测结果不准确。
        """
        date_format = "YYYY-MM-DD HH:mm:ss"
        next_date = arrow.get(self.next_ohlc['date']).format(date_format)
        todate = arrow.get(self.env.todate).format(date_format)

        if todate == next_date:
            self.current_ohlc = copy(self.next_ohlc)
            self.next_ohlc['date'] = arrow.get(todate).shift(
                days=get_day_ratio(self.env.sys_frequency)).format(date_format)
        else:
            self.env.cur_suspended_tickers.append(self.ticker)
