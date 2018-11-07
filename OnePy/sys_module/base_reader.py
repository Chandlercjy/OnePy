import abc
from typing import Generator

from OnePy.sys_module.metabase_env import OnePyEnvBase


class ReaderBase(OnePyEnvBase, abc.ABC):
    """负责读取数据"""

    def __init__(self, ticker: str, key: str = None) -> None:
        self.ticker = ticker
        self.key = key

        if key:
            self.env.readers[f'{ticker}_{key}'] = self
        else:
            self.env.readers[ticker] = self

    @abc.abstractmethod
    def load(self, fromdate: str, todate: str, frequency: str) -> Generator:
        """需要返回已过滤好的从fromdate开始的数据,cleander需要用"""
        raise NotImplementedError

    def load_by_cleaner(self, fromdate: str, todate: str,
                        frequency: str) -> Generator:

        return self.load(fromdate, todate, frequency)

