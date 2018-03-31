from OnePy.constants import OrderType
from OnePy.environment import Environment
from OnePy.sys_mod.base_recorder import RecorderBase
from OnePy.sys_model.record_series import RecordFactory


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
        self.position = RecordFactory.long_and_short('position')
        self.avg_price = RecordFactory.long_and_short('avg_price')
        self.holding_pnl = RecordFactory.long_and_short('holding_pnl')
        self.realized_pnl = RecordFactory.long_and_short('realized_pnl')
        self.commission = RecordFactory.long_and_short(
            'commission')
        self.market_value = RecordFactory.long_and_short('market_value')

        self.margin = RecordFactory.long_and_short('margin')
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
               # 更新保证金(股票多头不需要)
                # 更新仓位
                last_position = self.position.latest_long(ticker)
                new_position = last_position + size*direction
                # 更新avg price
                last_avg_price = self.avg_price.latest_long(ticker)
                # 更新浮动盈亏
                last_holding_pnl = self.holding_pnl.latest_long(ticker)

                if new_position == 0:
                    new_avg_price = 0
                    new_holding_pnl = 0
                else:
                    new_avg_price = (last_position * last_avg_price +
                                     direction*size*execute_price)/new_position

                    new_holding_pnl = (cur_price - new_avg_price)*new_position

                # 更新已平仓盈亏
                last_realized_pnl = self.realized_pnl.latest_long(ticker)

                if order.order_type == OrderType.Sell:
                    new_realized_pnl = last_realized_pnl + \
                        (new_avg_price - last_avg_price)*size
                else:
                    new_realized_pnl = last_realized_pnl

                # 更新手续费
                last_commission = self.commission.latest_long(ticker)

                if self.per_comm_pct:
                    new_commission = last_commission + self.per_comm*size*execute_price
                else:
                    new_commission = last_commission + self.per_comm

                new_market_value = new_position*cur_price
                self.market_value.append_long(
                    ticker, trading_date, new_market_value)
                self.position.append_long(ticker, trading_date, new_position)
                self.avg_price.append_long(ticker, trading_date, new_avg_price)
                self.holding_pnl.append_long(
                    ticker, trading_date, new_holding_pnl)
                self.realized_pnl.append_long(
                    ticker, trading_date, new_realized_pnl)
                self.commission.append_long(
                    ticker, trading_date, new_commission)

            elif self.for_short(order):
                # 更新仓位
                last_position = self.position.latest_short(ticker)
                new_position = last_position + size*direction
                # 更新avg price
                last_avg_price = self.avg_price.latest_short(ticker)
                # 更新浮动盈亏
                last_holding_pnl = self.holding_pnl.latest_short(ticker)

                if new_position == 0:
                    new_avg_price = 0
                    new_holding_pnl = 0
                else:
                    new_avg_price = (last_position * last_avg_price +
                                     direction*size*execute_price)/new_position

                    new_holding_pnl = (cur_price - new_avg_price)*new_position

                # 更新已平仓盈亏
                last_realized_pnl = self.realized_pnl.latest_short(
                    ticker)

                if order.order_type == OrderType.Short_cover:
                    new_realized_pnl = last_realized_pnl + \
                        (new_avg_price - last_avg_price)*size
                else:
                    new_realized_pnl = last_realized_pnl

                # 更新手续费
                last_commission = self.commission.latest_short(ticker)

                if self.per_comm_pct:
                    new_commission = last_commission + self.per_comm*size*execute_price
                else:
                    new_commission = last_commission + self.per_comm

                # 更新保证金(股票多头不需要)
                new_margin = new_position*cur_price*self.margin_rate

                new_market_value = new_position*cur_price

                self.market_value.append_short(
                    ticker, trading_date, new_market_value)
                self.position.append_short(ticker, trading_date, new_position)
                self.avg_price.append_short(
                    ticker, trading_date, new_avg_price)
                self.holding_pnl.append_short(
                    ticker, trading_date, new_holding_pnl)
                self.realized_pnl.append_short(
                    ticker, trading_date, new_realized_pnl)
                self.commission.append_short(
                    ticker, trading_date, new_commission)
                self.margin.append_short(ticker, trading_date, new_margin)

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
