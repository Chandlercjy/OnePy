from OnePy.constants import ActionType
from OnePy.sys_module.models.base_series import SeriesBase


class PositionSeries(SeriesBase):
    name = 'position'

    def append(self, order, last_position,  long_or_short='long'):
        new_value = last_position + order.size*self.direction(order)
        self._append_value(order.ticker, new_value, long_or_short)


class AvgPriceSeries(SeriesBase):
    name = 'avg_price'

    def append(self, order, last_position, last_avg_price, new_position,
               long_or_short='long'):

        if new_position == 0:
            new_value = 0

        elif new_position > last_position:
            new_value = (last_position * last_avg_price +
                         order.size*order.execute_price)/new_position
        else:
            new_value = last_avg_price  # TODO 错误

        self._append_value(order.ticker, new_value, long_or_short)


class RealizedPnlSeries(SeriesBase):
    """
    1. Buy and Sell对冲
    2. short sell 和short cover
    要添加负号
    """
    name = 'realized_pnl'

    def append(self, order, last_avg_price, new_avg_price, long_or_short='long'):
        new_value = None

        if order.action_type == ActionType.Sell:
            new_value = self.latest(
                order.ticker, long_or_short)+(order.execute_price - last_avg_price)*order.size
        elif order.action_type == ActionType.Short_cover:
            new_value = self.latest(
                order.ticker, long_or_short)-(order.execute_price - last_avg_price)*order.size

        if new_value:
            self._append_value(order.ticker,  new_value, long_or_short)


class CommissionSeries(SeriesBase):
    name = 'commission'

    def append(self, order, last_commission, per_comm, per_comm_pct,
               long_or_short='long'):

        if per_comm_pct:
            new_value = last_commission + per_comm*order.size*order.execute_price
        else:
            new_value = last_commission + per_comm
        self._append_value(order.ticker, new_value, long_or_short)


class HoldingPnlSeries(SeriesBase):
    name = 'holding_pnl'

    def append(self, ticker, cur_price, new_avg_price, new_position,
               long_or_short='long'):

        if new_position == 0:
            new_value = 0
        else:
            new_value = (cur_price - new_avg_price)*new_position * \
                self.earn_short(long_or_short)
        self._append_value(ticker, new_value, long_or_short)

    def update_barly(self, order_executed):
        for ticker in self.env.feeds:
            cur_price = self.get_barly_cur_price(ticker, order_executed)

            for long_or_short in ['long', 'short']:
                new_position = self.env.recorder.position.latest(
                    ticker, long_or_short)
                new_avg_price = self.env.recorder.avg_price.latest(
                    ticker, long_or_short)

                self.append(ticker, cur_price, new_avg_price, new_position,
                            long_or_short)


class MarketValueSeries(SeriesBase):
    name = 'market_value'

    def append(self, ticker,  cur_price, new_position,
               long_or_short='long'):
        new_value = new_position*cur_price
        self._append_value(ticker,  new_value, long_or_short)

    def update_barly(self, order_executed):
        for ticker in self.env.feeds:
            cur_price = self.get_barly_cur_price(ticker, order_executed)

            for long_or_short in ['long', 'short']:
                new_position = self.env.recorder.position.latest(
                    ticker, long_or_short)
                self.append(ticker,  cur_price,
                            new_position, long_or_short)


class MarginSeries(SeriesBase):
    name = 'margin'

    def append(self, ticker,  cur_price, new_position, margin_rate,
               long_or_short='long'):

        if long_or_short == 'short':
            new_value = new_position*cur_price*margin_rate
            self._append_value(
                ticker,  new_value, long_or_short)

    def update_barly(self, order_executed):

        for ticker in self.env.feeds:
            cur_price = self.get_barly_cur_price(ticker, order_executed)

            for long_or_short in ['long', 'short']:
                new_position = self.env.recorder.position.latest(
                    ticker, long_or_short)

                margin_rate = self.env.recorder.margin_rate
                self.append(ticker,  cur_price, new_position, margin_rate,
                            long_or_short)
