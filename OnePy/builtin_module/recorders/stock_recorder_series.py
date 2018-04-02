from OnePy.constants import OrderType
from OnePy.sys_model.base_series import SeriesBase


class PositionSeries(SeriesBase):
    name = 'position'

    def append(self, order, last_position,  long_or_short='long'):
        new_value = last_position + order.size*self.direction(order)
        self._append_value(order.ticker, order.trading_date,
                           new_value, long_or_short)


class AvgPriceSeries(SeriesBase):
    name = 'avg_price'

    def append(self, order, last_position, last_avg_price, new_position,
               long_or_short='long'):

        if new_position == 0:
            new_value = 0
        else:
            new_value = (last_position * last_avg_price + self.direction(order)
                         * order.size*order.execute_price)/new_position

        self._append_value(order.ticker, order.trading_date,
                           new_value, long_or_short)


class RealizedPnlSeries(SeriesBase):
    name = 'realized_pnl'

    def append(self, order, new_avg_price, last_avg_price, long_or_short='long'):
        if order.order_type in [OrderType.Sell, OrderType.Short_cover]:
            last_realized_pnl = self.latest(order.ticker, long_or_short)
            new_value = last_realized_pnl + \
                (new_avg_price - last_avg_price)*order.size
            self._append_value(
                order.ticker, order.trading_date, new_value, long_or_short)


class CommissionSeries(SeriesBase):
    name = 'commission'

    def append(self, order, last_commission, per_comm, per_comm_pct,
               long_or_short='long'):

        if per_comm_pct:
            new_value = last_commission + per_comm*order.size*order.execute_price
        else:
            new_value = last_commission + per_comm
        self._append_value(order.ticker, order.trading_date,
                           new_value, long_or_short)


class HoldingPnlSeries(SeriesBase):
    name = 'holding_pnl'

    def append(self, ticker, trading_date, cur_price, new_avg_price, new_position,
               long_or_short='long'):
        new_value = (cur_price - new_avg_price)*new_position
        self._append_value(ticker, trading_date,
                           new_value, long_or_short)

    def update_barly(self):
        for ticker in self.env.feeds:
            for long_or_short in ['long', 'short']:
                cur_price = self.env.feeds[ticker].cur_price
                new_position = self.env.recorder.position.latest(
                    ticker, long_or_short)
                new_avg_price = self.env.recorder.avg_price.latest(
                    ticker, long_or_short)
                trading_date = self.env.gvar.trading_date

                if new_position == 0:
                    new_value = 0
                else:
                    new_value = (cur_price - new_avg_price)*new_position

                self.append(
                    ticker, trading_date, cur_price, new_avg_price, new_value,
                    long_or_short)


class MarketValueSeries(SeriesBase):
    name = 'market_value'

    def append(self, ticker, trading_date, cur_price, new_position,
               long_or_short='long'):
        new_value = new_position*cur_price
        self._append_value(ticker, trading_date,
                           new_value, long_or_short)

    def update_barly(self):
        for ticker in self.env.feeds:
            for long_or_short in ['long', 'short']:
                cur_price = self.env.feeds[ticker].cur_price
                new_position = self.env.recorder.position.latest(
                    ticker, long_or_short)
                trading_date = self.env.gvar.trading_date
                self.append(ticker, trading_date, cur_price,
                            new_position, long_or_short)


class MarginSeries(SeriesBase):
    name = 'margin'

    def append(self, ticker, trading_date, cur_price, new_position, margin_rate,
               long_or_short='long'):

        if long_or_short == 'short':
            new_value = new_position*cur_price*margin_rate
            self._append_value(
                ticker, trading_date, new_value, long_or_short)

    def update_barly(self):

        for ticker in self.env.feeds:
            for long_or_short in ['long', 'short']:
                cur_price = self.env.feeds[ticker].cur_price
                new_position = self.env.recorder.position.latest(
                    ticker, long_or_short)
                trading_date = self.env.gvar.trading_date
                margin_rate = self.env.recorder.margin_rate
                self.append(
                    ticker, trading_date, cur_price, new_position, margin_rate,
                    long_or_short)


