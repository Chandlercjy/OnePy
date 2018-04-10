from collections import defaultdict, deque
from functools import partial
from itertools import count

import arrow

import OnePy as op
from OnePy.environment import Environment


class CleanerBase(object):
    env = Environment
    counter = count(1)

    """Docstring for RiskManagerBase. """

    def __init__(self, length, buffer_day):
        self.name = f'{self.__class__.__name__}_{next(self.counter)}'
        self.env.cleaners.update({self.name: self})

        self.data = defaultdict(partial(deque, maxlen=length))
        self.buffer_day = buffer_day
        self.initialize_buffer_data()

    @property
    def startdate(self):
        date = arrow.get(self.env.fromdate).shift(days=-self.buffer_day)

        return date.format('YYYY-MM-DD HH:mm:ss')

    def _check_length(self, ticker):
        if len(self.data[ticker]) < self.data[ticker].maxlen:
            raise Exception('data length is not enough for cleaner')

    def initialize_buffer_data(self):
        for key, value in self.env.readers.items():
            buffer_data = value.load(
                fromdate=self.startdate, todate=self.env.fromdate)

            self.data[key].extend((i['close'] for i in buffer_data))
            self._check_length(key)

    def _append_data_to_buffer(self):
        for ticker, ohlc in self.env.feeds.items():
            self.data[ticker].append(ohlc.close)

    def run(self):
        self._append_data_to_buffer()
