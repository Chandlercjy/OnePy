
from collections import defaultdict, deque

import numpy as np
import pandas as pd

from OnePy.sys_module.base_cleaner import CleanerBase


def rank(x):
    return sorted(x)


def ts_argmax(x):
    return len(x)-np.argwhere(x == max(x))[0][0]


def signed_power(x, t):
    return abs(x) ** t * sign(x)


def sign(x: np.array):
    x = x.copy()
    x[x > 0] = 1
    x[x < 0] = -1
    x[x == 0] = 0

    return x


def stddev(x, n):
    return np.std(x[-n:])


class AlphaBase(CleanerBase):

    def returns(self, ticker):
        key = f'{ticker}_{self.frequency}'
        close_series = self.data[key]['close']

        return (close_series[-1] - close_series[-2])/close_series[-1]

    def initialize_buffer_data(self, ticker: str, buffer_day: int):
        super().initialize_buffer_data(ticker, buffer_day)

        if ticker in self.env.tickers:  # 因为ticker有可能在check length中被删除

            key = f'{ticker}_{self.frequency}'
            close_series = pd.Series(self.data[key]['close'])

            returns = (close_series - close_series.shift(1)) / \
                close_series.shift(1)

            returns[0] = 0
            std = returns.rolling(self.rolling_window).std()
            std[0] = 0
            self.data[key]['returns'] = deque(
                returns, maxlen=self.rolling_window)
            self.data[key]['std'] = deque(returns, maxlen=self.rolling_window)

    def _save_data(self, key, cleaners_ohlc):
        super()._save_data(key, cleaners_ohlc)

        last_close = self.data[key]['close'][-2]

        returns = (cleaners_ohlc.close-last_close)/last_close
        self.data[key]['returns'].append(returns)
        std = np.std(self.data[key]['returns'])
        self.data[key]['std'].append(std)


class Alpha101(AlphaBase):

    def calculate001(self, look_back_days=5):
        result = []
        final = []

        for ticker in self.env.tickers:
            if ticker not in self.env.cur_suspended_tickers:

                key = f'{ticker}_{self.frequency}'

                series = self.data[key]

                if self.returns(ticker) < 0:
                    x1 = np.array(series['std'])[-look_back_days:]
                else:
                    x1 = np.array(series['close'])[-look_back_days:]

                x2 = signed_power(x1, 2)
                x3 = ts_argmax(x2)
                result.append((x3, ticker))
        result.sort()
        length = len(result)

        for index, value in enumerate(result):
            rank_value = index/length - 0.5

            if rank_value > 0:
                final.append(value[1])

        return final

    def calculate002(self, look_back_days=5):
        result = []
        final = []

        for ticker in self.env.tickers:
            if ticker not in self.env.cur_suspended_tickers:

                key = f'{ticker}_{self.frequency}'

                series = self.data[key]

                if self.returns(ticker) < 0:
                    x1 = np.array(series['std'])[-look_back_days:]
                else:
                    x1 = np.array(series['close'])[-look_back_days:]

                x2 = signed_power(x1, 2)
                x3 = ts_argmax(x2)
                result.append((x3, ticker))
        result.sort()
        length = len(result)

        for index, value in enumerate(result):
            rank_value = index/length - 0.5

            if rank_value > 0:
                final.append(value[1])

        return final
