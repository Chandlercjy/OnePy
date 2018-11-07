import abc
from collections import defaultdict, deque
from functools import partial
from itertools import count

import arrow

from OnePy.sys_module.components.market_maker import MarketMaker
from OnePy.sys_module.metabase_env import OnePyEnvBase


class CleanerBase(OnePyEnvBase):
    counter = count(1)

    def __init__(self, rolling_window: int, buffer_day: int,
                 frequency: str = None) -> None:
        self.name = f'{self.__class__.__name__}_{next(self.counter)}'
        self.env.cleaners.update({self.name: self})
        self.rolling_window = rolling_window
        self.buffer_day = buffer_day
        self.frequency = frequency
        self.data = defaultdict(dict)  # type:defaultdict

        assert buffer_day <= 500, 'buffer_day should not bigger than 500!'

    def _check_length(self, key: str, buffer_day: int):
        ticker = key.replace(f'_{self.frequency}', '')

        if buffer_day > 500 or not self.data[key]:  # 超过长度说明没有数据了
            del self.data[key]
            self.env.logger.warning(
                f'{ticker}_{self.frequency} is not enough for cleaners. Deleted!!!!')

            if ticker in self.env.tickers:
                self.env.tickers.remove(ticker)

                return

        elif len(self.data[key]['close']) < self.data[key]['close'].maxlen:

            buffer_day += 2
            self.buffer_day = buffer_day
            self.initialize_buffer_data(ticker, buffer_day)
            self.env.logger.warning(
                f'Retry {self.name}, perfect buffer_day = {buffer_day}')

    def initialize_buffer_data(self, ticker: str, buffer_day: int):
        self._settle_frequency(ticker)
        reader = self.env.readers[ticker]

        buffer_start_date = arrow.get(self.env.sys_date).shift(
            days=-buffer_day).format('YYYY-MM-DD HH:mm:ss')
        buffer_end_date = arrow.get(self.env.sys_date).shift(
            seconds=-1).format('YYYY-MM-DD HH:mm:ss')
        key = f'{ticker}_{self.frequency}'
        single_data = defaultdict(partial(deque, maxlen=self.rolling_window))
        buffer_data = reader.load_by_cleaner(fromdate=buffer_start_date,
                                             todate=buffer_end_date,
                                             frequency=self.frequency)

        for value in buffer_data:
            single_data['open'].append(value['open'])
            single_data['high'].append(value['high'])
            single_data['low'].append(value['low'])
            single_data['close'].append(value['close'])
            single_data['volume'].append(value['volume'])
            single_data['date'].append(value['date'])
        self.data[key].update(single_data)
        self._check_length(key, buffer_day)

    def _append_data_to_buffer(self):
        for key in list(self.data):
            ticker = key.replace(f'_{self.frequency}', '')

            if ticker not in self.env.cur_suspended_tickers:  # 不停牌才进行更新
                if self.frequency == self.env.sys_frequency:
                    cleaners_ohlc = self.env.feeds[ticker]
                    self._save_data(key, cleaners_ohlc)

                else:
                    cleaners_ohlc = self.env.cleaners_feeds[f'{key}_{self.name}']
                    next_datetime = arrow.get(cleaners_ohlc.next_ohlc['date'])
                    sys_date = arrow.get(self.env.sys_date)

                    while next_datetime <= sys_date:
                        try:
                            cleaners_ohlc.next_directly()
                            self._save_data(key, cleaners_ohlc)
                        except StopIteration:
                            # 报错的话可能是因为cleaner的frequency比sys大
                            cur_datetime = arrow.get(
                                cleaners_ohlc.current_ohlc['date'])

                            if cur_datetime > sys_date:  # 希望永不触发
                                self.env.logger.warning(
                                    "框架回测逻辑出现错误！！")

                            break
                        next_datetime = arrow.get(
                            cleaners_ohlc.next_ohlc['date'])
                        sys_date = arrow.get(self.env.sys_date)

    def _settle_frequency(self, ticker):
        if self.frequency:
            self._save_cleaners_feeds(ticker)
        else:
            self.frequency = self.env.sys_frequency

    def _save_cleaners_feeds(self, ticker: str):
        key = f'{ticker}_{self.frequency}_{self.name}'

        value = MarketMaker.get_bar(ticker, self.frequency)

        if value.initialize(7):
            self.env.cleaners_feeds.update({key: value})

    def _save_data(self, key, cleaners_ohlc):
        self.data[key]['date'].append(cleaners_ohlc.date)
        self.data[key]['open'].append(cleaners_ohlc.open)
        self.data[key]['high'].append(cleaners_ohlc.high)
        self.data[key]['low'].append(cleaners_ohlc.low)
        self.data[key]['close'].append(cleaners_ohlc.close)
        self.data[key]['volume'].append(cleaners_ohlc.volume)

    def run(self):
        self._append_data_to_buffer()

    @abc.abstractmethod
    def calculate(self, ticker: str):
        raise NotImplementedError
