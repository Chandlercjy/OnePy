from OnePy.constants import OrderType
from OnePy.environment import Environment
from OnePy.sys_mod.base_recorder import RecorderBase
from OnePy.sys_model.record_series import (AvgPriceSeries, CommissionSeries,
                                           HoldingPnlSeries, MarginSeries,
                                           MarketValueSeries, PositionSeries,
                                           RealizedPnlSeries, RecordFactory)


class StockRecorder(RecorderBase):

    """Docstring for StockRecorder. """

    def __init__(self):
        super().__init__()
        self.initial_cash = 100000

        # self.margin = RecordSeries('margin')
    def set_setting(self, initial_cash=100000, comm=1, comm_pct=None, margin_rate=0.1, loan_rate=0.01):
        self.initial_cash = initial_cash
        self.per_comm = comm
        self.per_comm_pct = comm_pct
        self.margin_rate = margin_rate
        self.loan_rate = loan_rate

    def initialize(self):
        self.set_setting()
        self.position = PositionSeries()
        self.avg_price = AvgPriceSeries()
        self.holding_pnl = HoldingPnlSeries()
        self.realized_pnl = RealizedPnlSeries()
        self.commission = CommissionSeries()
        self.market_value = MarketValueSeries()

        self.margin = MarginSeries()
        self.balance = RecordFactory.long_only('balance', self.initial_cash)
        self.cash = RecordFactory.long_only('cash', self.initial_cash)
        self.frozen_cash = RecordFactory.long_only('frozen_cash', 0)

    @property
    def submitted_order(self):
        return self.env.orders_mkt_submitted

    def record_order(self):
        for order in self.submitted_order:
            # TODO:这里cur_price有争议，需要考虑成交价
            cur_price = self.env.feeds[order.ticker].cur_price
            direction = self.direction(order)
            size = order.size
            execute_price = order.execute_price
            ticker = order.ticker
            trading_date = order.trading_date

            if self.for_long(order):
                long_or_short = 'long'
            elif self.for_short(order):
                long_or_short = 'short'

            last_position = self.position.latest(ticker, long_or_short)
            last_avg_price = self.avg_price.latest(ticker, long_or_short)
            last_realized_pnl = self.realized_pnl.latest(
                ticker, long_or_short)
            last_commission = self.commission.latest(ticker, long_or_short)

            new_position = last_position + size*direction

            if new_position == 0:
                new_avg_price = 0
                new_holding_pnl = 0
            else:
                new_avg_price = (last_position * last_avg_price +
                                 direction*size*execute_price)/new_position
                new_holding_pnl = (cur_price - new_avg_price)*new_position

            if order.order_type == OrderType.Sell:
                new_realized_pnl = last_realized_pnl + \
                    (new_avg_price - last_avg_price)*size
            else:
                new_realized_pnl = last_realized_pnl

            if self.per_comm_pct:
                new_commission = last_commission + self.per_comm*size*execute_price
            else:
                new_commission = last_commission + self.per_comm

            new_market_value = new_position*cur_price
            self.position.append(order, last_position, long_or_short)
            self.market_value.append(
                order, cur_price, new_position, long_or_short)
            self.avg_price.append(order,
                                  last_position,
                                  last_avg_price,
                                  new_position,
                                  long_or_short)
            self.holding_pnl.append(order,
                                    cur_price,
                                    new_avg_price,
                                    new_position,
                                    long_or_short)
            self.commission.append(order,
                                   last_commission,
                                   self.per_comm,
                                   self.per_comm_pct,
                                   long_or_short)
            self.realized_pnl.append(order,
                                     last_realized_pnl,
                                     new_avg_price,
                                     last_avg_price,
                                     long_or_short)
            self.margin.append(order,
                               cur_price,
                               new_position,
                               self.margin_rate,
                               long_or_short)
            self.update_balance_and_cash(trading_date)

    def update_balance_and_cash(self, trading_date):
        # 更新Balance
        total_realized_pnl = self.realized_pnl.total_value()
        total_holding_pnl = self.holding_pnl.total_value()
        total_commission = self.commission.total_value()
        total_position = self.position.total_value()
        total_margin = self.margin.total_value()
        total_market_value = self.market_value.total_value()
        new_balance = self.initial_cash + total_realized_pnl + \
            total_holding_pnl - total_commission
        # 更新frozen_cash
        new_frozen_cash = total_margin+total_market_value

        # 更新cash
        new_cash = new_balance - new_frozen_cash

        self.balance.append({'date': trading_date, 'value': new_balance})
        self.frozen_cash.append(
            {'date': trading_date, 'value': new_frozen_cash})
        self.cash.append({'date': trading_date, 'value': new_cash})

    def direction(self, order):
        if order.order_type in [OrderType.Buy, OrderType.Short_sell]:
            return 1

        elif order.order_type in [OrderType.Sell, OrderType.Short_cover]:
            return -1

    def for_long(self, order):
        if order.order_type in [OrderType.Buy, OrderType.Sell]:
            return True

    def for_short(self, order):
        if order.order_type in [OrderType.Short_sell, OrderType.Short_cover]:
            return True

    def update_market_value(self):
        for ticker in self.env.feeds:
            cur_price = self.env.feeds[ticker].cur_price
            new_long = self.position.latest_long(ticker)*cur_price
            new_short = self.position.latest_short(ticker)*cur_price
            trading_date = self.env.gvar.trading_date
            self.market_value.append_long(ticker, trading_date, new_long)
            self.market_value.append_short(ticker, trading_date, new_short)

    def update_holding_pnl(self):
        for ticker in self.env.feeds:
            cur_price = self.env.feeds[ticker].cur_price
            long_position = self.position.latest_long(ticker)
            short_position = self.position.latest_short(ticker)
            long_avg_price = self.avg_price.latest_long(ticker)
            short_avg_price = self.avg_price.latest_short(ticker)

            if long_position == 0:
                new_long = 0
            else:
                new_long = (cur_price - long_avg_price)*long_position

            if short_position == 0:
                new_short = 0
            else:
                new_short = (cur_price - short_avg_price)*short_position
            trading_date = self.env.gvar.trading_date
            self.holding_pnl.append_long(ticker, trading_date, new_long)
            self.holding_pnl.append_short(ticker, trading_date, new_short)

    def update_margin(self):
        for ticker in self.env.feeds:
            cur_price = self.env.feeds[ticker].cur_price
            short_position = self.position.latest_short(ticker)
            new_short = short_position*cur_price*self.margin_rate
            trading_date = self.env.gvar.trading_date
            self.margin.append_short(ticker, trading_date, new_short)

    def run(self):
        self.record_order()

    def update(self):
        """根据最新价格更新信息,
        需要更新cash，frozen cash, market_value, holding_pnl, balance"""
        self.update_market_value()
        self.update_holding_pnl()
        self.update_margin()
        self.update_balance_and_cash(self.env.gvar.trading_date)
