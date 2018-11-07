from collections import defaultdict, deque
from functools import partial

import OnePy as op
from OnePy.sys_module.base_cleaner import CleanerBase


class SMA(CleanerBase):
    def calculate(self, ticker):
        key = f'{ticker}_{self.frequency}'
        close = self.data[key]['close']

        return sum(close)/len(close)  # TODO:尝试用numpy看能否提高性能
