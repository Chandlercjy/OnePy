from collections import UserDict, UserList

from OnePy.constants import OrderType
from OnePy.environment import Environment


class RecordBase(UserList):
    env = Environment

    def __init__(self, name):
        super().__init__(self)
        self.name = name
        self.data.append({'date': 'start', 'value': 0})

    @property
    def latest(self):
        return self.data[-1]['value']


class RecordLong(RecordBase):
    pass


class RecordShort(RecordBase):
    pass


class RecordFactory(object):
    env = Environment

    @classmethod
    def long_and_short(self, name):
        series_dict = SeriesDict()

        for ticker in self.env.feeds:
            series_dict[f'{ticker}_long'] = RecordLong(name)
            series_dict[f'{ticker}_short'] = RecordShort(name)

        return series_dict

    @classmethod
    def long_only(self, name, initial_cash):
        series = RecordLong(name)
        series[0]['value'] = initial_cash

        return series


class SeriesDict(UserDict):

    def latest_long(self, ticker):
        return self.data[f'{ticker}_long'][-1]['value']

    def latest_short(self, ticker):
        return self.data[f'{ticker}_short'][-1]['value']

    def append_long(self, ticker, trading_date,  value):
        self.data[f'{ticker}_long'].append(
            {'date': trading_date, 'value': value})

    def append_short(self, ticker, trading_date,  value):
        self.data[f'{ticker}_short'].append(
            {'date': trading_date, 'value': value})

    def total_value(self):
        total = 0

        for data_list in self.data.values():
            per_dict = data_list[-1]
            total += per_dict['value']

        return total


class SeriesBase(UserDict):
    env = Environment

    def __init__(self):
        super().__init__()

        for ticker in self.env.feeds:
            self.data[f'{ticker}_long'] = [dict(date='start', value=0)]
            self.data[f'{ticker}_short'] = [dict(date='start', value=0)]

    def latest(self, ticker, long_or_short):
        return self.data[f'{ticker}_{long_or_short}'][-1]['value']

    def latest_long(self, ticker):
        return self.data[f'{ticker}_long'][-1]['value']

    def latest_short(self, ticker):
        return self.data[f'{ticker}_short'][-1]['value']

    def append_long(self, ticker, trading_date,  value):
        self.data[f'{ticker}_long'].append(
            {'date': trading_date, 'value': value})

    def append_short(self, ticker, trading_date,  value):
        self.data[f'{ticker}_short'].append(
            {'date': trading_date, 'value': value})

    def total_value(self):
        total = 0

        for data_list in self.data.values():
            per_dict = data_list[-1]
            total += per_dict['value']

        return total

    def direction(self, order):
        if order.order_type in [OrderType.Buy, OrderType.Short_sell]:
            return 1

        elif order.order_type in [OrderType.Sell, OrderType.Short_cover]:
            return -1

    def _append_value(self, order, value, long_or_short):
        self.data[f'{order.ticker}_{long_or_short}'].append(
            {'date': order.trading_date, 'value': value})


class PositionSeries(SeriesBase):

    def append(self, order, last_position,  long_or_short='long'):
        new_value = last_position + order.size*self.direction(order)
        self._append_value(order, new_value, long_or_short)


class AvgPriceSeries(SeriesBase):

    def append(self, order, last_position, last_avg_price, new_position,  long_or_short='long'):
        if new_position == 0:
            new_value = 0
        else:
            new_value = (last_position * last_avg_price + self.direction(order)
                         * order.size*order.execute_price)/new_position

        self._append_value(order, new_value, long_or_short)


class RealizedPnlSeries(SeriesBase):

    def append(self, order, last_realized_pnl, new_avg_price, last_avg_price, long_or_short='long'):
        if order.order_type in [OrderType.Sell, OrderType.Short_cover]:
            new_value = last_realized_pnl + \
                (new_avg_price - last_avg_price)*order.size
            self._append_value(order, new_value, long_or_short)


class CommissionSeries(SeriesBase):

    def append(self, order, last_commission, per_comm, per_comm_pct, long_or_short='long'):

        if per_comm_pct:
            new_value = last_commission + per_comm*order.size*order.execute_price
        else:
            new_value = last_commission + per_comm
        self._append_value(order, new_value, long_or_short)


class HoldingPnlSeries(SeriesBase):

    def append(self, order, cur_price, new_avg_price, new_position, long_or_short='long'):
        if new_position == 0:
            new_value = 0
        else:
            new_value = (cur_price - new_avg_price)*new_position

        self._append_value(order, new_value, long_or_short)


class MarketValueSeries(SeriesBase):

    def append(self, order, cur_price, new_position, long_or_short='long'):
        new_value = new_position*cur_price
        self._append_value(order, new_value, long_or_short)


class MarginSeries(SeriesBase):
    def append(self, order, cur_price, new_position, margin_rate, long_or_short='long'):
        if long_or_short == 'short':
            new_value = new_position*cur_price*margin_rate
            self._append_value(order, new_value, long_or_short)
