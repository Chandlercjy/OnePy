import abc
from collections import UserDict, UserList, deque
from typing import Deque, Dict, List, Union

import pandas as pd

from OnePy.constants import ActionType
from OnePy.sys_module.metabase_env import OnePyEnvBase


class SeriesBase(OnePyEnvBase, UserDict, abc.ABC):
    name: str = None

    def __init__(self, maxlen: int = None) -> None:
        super().__init__()
        self.data = {}  # type:Dict[str,Deque]

        for ticker in self.env.feeds:
            if maxlen:
                self.data[f'{ticker}_long'] = deque([
                    dict(date=self.env.fromdate, value=0)], maxlen=maxlen)
                self.data[f'{ticker}_short'] = deque([
                    dict(date=self.env.fromdate, value=0)], maxlen=maxlen)
            else:
                self.data[f'{ticker}_long'] = [
                    dict(date=self.env.fromdate, value=0)]
                self.data[f'{ticker}_short'] = [
                    dict(date=self.env.fromdate, value=0)]

    def change_initial_value(self, ticker: str,
                             value: float, long_or_short: str):
        self.data[f'{ticker}_{long_or_short}'][0]['value'] = value

    def latest(self, ticker: str,
               long_or_short: str, index: int = -1) -> float:

        return self.data[f'{ticker}_{long_or_short}'][index]['value']

    def total_value(self) -> float:
        total = 0

        for data_list in self.data.values():
            per_dict = data_list[-1]
            total += per_dict['value']

        return total

    def _append_value(self, ticker: str, value: float, long_or_short: str):
        key = f'{ticker}_{long_or_short}'

        if self.data[key][-1]['date'] == self.env.sys_date:
            self.data[key][-1]['value'] = value
        else:
            self.data[key].append(
                {'date': self.env.sys_date, 'value': value})

    def dataframe(self) -> list:
        dataframe_list = []

        for ticker in self.env.tickers:
            long_df = pd.DataFrame(self.data[f'{ticker}_long'])
            short_df = pd.DataFrame(self.data[f'{ticker}_short'])
            long_df.rename(columns=dict(
                value=f'{self.name}_{ticker}_long'), inplace=True)
            short_df.rename(columns=dict(
                value=f'{self.name}_{ticker}_short'), inplace=True)

            long_df = long_df[~long_df.date.duplicated(keep='last')]
            short_df = short_df[~short_df.date.duplicated(keep='last')]

            long_df.set_index('date', inplace=True)
            long_df.index = pd.to_datetime(long_df.index)

            short_df.set_index('date', inplace=True)
            short_df.index = pd.to_datetime(short_df.index)

            dataframe_list.append(long_df)
            dataframe_list.append(short_df)

        return dataframe_list

    def single_dataframe(self) ->pd.DataFrame:
        dataframe_list = []

        for value in self.data.values():
            if len(value) == 1:
                continue
            df = pd.DataFrame(value)
            df = df[~df.date.duplicated(keep='last')]
            df.set_index('date', inplace=True)
            df.index = pd.to_datetime(df.index)
            dataframe_list.append(df)
        result = sum(dataframe_list)

        return result

    def plot(self, ticker: str):
        long_df = pd.DataFrame(self.data[f'{ticker}_long'])
        short_df = pd.DataFrame(self.data[f'{ticker}_short'])
        long_df.rename(columns=dict(value=f'{self.name}_long'), inplace=True)
        short_df.rename(columns=dict(value=f'{self.name}_short'), inplace=True)

        total_df = long_df.merge(short_df, how='outer')
        total_df.fillna(method='ffill', inplace=True)
        total_df.set_index('date', inplace=True)
        total_df.plot()

    def get_barly_cur_price(self, ticker: str, order_executed: bool) -> float:
        """若是订单执行，则返回成交价，否则只是更新信息，返回开盘价"""

        if order_executed:
            return self.env.feeds[ticker].execute_price
        else:
            return self.env.feeds[ticker].open

    @abc.abstractmethod
    def update_order(self):
        raise NotImplementedError


class MoneySeries(OnePyEnvBase, UserList):

    def __init__(self, name: str, initial_value: int,
                 maxlen: int = None) -> None:
        super().__init__()
        self.name = name

        if maxlen:
            self.data = deque(
                [dict(date=self.env.fromdate, value=initial_value)],
                maxlen=maxlen)  # type: Deque[Dict[str,Union[str,float]]]
        else:
            # type: List[Dict[str,Union[str,float]]]
            self.data = [dict(date=self.env.fromdate, value=initial_value)]

    def change_initial_value(self, value: int):
        self.data[0]['value'] = value

    def latest(self, index: int = -1) -> float:
        return self.data[index]['value']

    def dataframe(self) -> pd.DataFrame:
        dataframe = pd.DataFrame(self.data)
        dataframe.rename(columns=dict(value=self.name), inplace=True)
        dataframe.set_index('date', inplace=True)
        dataframe.index = pd.to_datetime(dataframe.index)
        result = dataframe[~dataframe.index.duplicated(keep='last')]

        first = dataframe.ix[: 1]
        result = pd.concat([first, result])
        result.sort_index(inplace=True)

        return result

    def plot(self):
        self.dataframe().plot()


class PositionSeries(SeriesBase):
    name = 'position'

    @staticmethod
    def direction(action_type):
        if action_type in [ActionType.Buy, ActionType.Short]:
            return 1

        elif action_type in [ActionType.Sell, ActionType.Cover]:
            return -1

    def update_order(self, ticker, size, action_type,
                     last_position, long_or_short='long'):

        new_value = last_position + size * self.direction(action_type)
        self._append_value(ticker, new_value, long_or_short)


class AvgPriceSeries(SeriesBase):
    name = 'avg_price'

    def update_order(self, ticker, size, execute_price, last_position,
                     last_avg_price, new_position, long_or_short='long'):

        if new_position == 0:
            new_value = 0

        elif new_position > last_position:
            new_value = (last_position * last_avg_price +
                         size*execute_price)/new_position
        else:
            new_value = last_avg_price

        self._append_value(ticker, new_value, long_or_short)


class RealizedPnlSeriesBase(SeriesBase):
    name = 'realized_pnl'

    @abc.abstractmethod
    def update_order(self, ticker, size, execute_price, action_type,
                     last_avg_price, long_or_short='long'):
        raise NotImplementedError


class CommissionSeriesBase(SeriesBase):
    name = 'commission'

    @abc.abstractmethod
    def update_order(self, ticker, size, execute_price, action_type,
                     last_commission,  long_or_short='long'):
        raise NotImplementedError


class HoldingPnlSeriesBase(SeriesBase):
    name = 'holding_pnl'

    @abc.abstractmethod
    def update_order(self, ticker, cur_price, new_avg_price,
                     new_position, long_or_short='long'):
        raise NotImplementedError

    @abc.abstractmethod
    def update_barly(self, order_executed: bool):
        raise NotImplementedError


class MarketValueSeriesBase(SeriesBase):
    name = 'market_value'

    @abc.abstractmethod
    def update_order(self, ticker, cur_price, new_position,
                     long_or_short='long'):

        raise NotImplementedError

    @abc.abstractmethod
    def update_barly(self, order_executed: bool):
        raise NotImplementedError


class MarginSeriesBase(SeriesBase):
    name = 'margin'

    @abc.abstractmethod
    def update_order(self, ticker, long_or_short='long'):
        raise NotImplementedError

    @abc.abstractmethod
    def update_barly(self):
        raise NotImplementedError
