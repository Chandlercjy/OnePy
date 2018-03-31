from OnePy.constants import OrderType
from OnePy.environment import Environment
from OnePy.sys_mod.base_recorder import RecorderBase
from OnePy.sys_model.record_series import RecordFactory


class StockRecorder(RecorderBase):

    """Docstring for StockRecorder. """

    def __init__(self):
        super().__init__()
        self.initial_cash = 100000
        self.set_setting()

        # self.margin = RecordSeries('margin')
    def set_setting(self, initial_cash=100000, comm=1, comm_pct=None, margin_rate=0.1, loan_rate=0.01):
        self.initial_cash = initial_cash
        self.per_comm = comm
        self.per_comm_pct = comm_pct
        self.margin_rate = margin_rate
        self.loan_rate = loan_rate

    def initialize(self):
        self.position = RecordFactory.long_and_short('position')
        self.avg_price = RecordFactory.long_and_short('avg_price')
        self.holding_pnl = RecordFactory.long_and_short('holding_pnl')
        self.realized_pnl = RecordFactory.long_and_short('realized_pnl')
        self.commission = RecordFactory.long_and_short(
            'commission')
        self.market_value = RecordFactory.long_and_short('market_value')

        self.margin = RecordFactory.long_and_short('margin')
        self.balance = RecordFactory.long_only('balance')
        self.cash = RecordFactory.long_only('cash')
        self.frozen_cash = RecordFactory.long_only('frozen_cash')

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

            if self.for_long(order):
               # 更新保证金(股票多头不需要)
                # 更新仓位
                last_position = self.position.latest_long(order)
                new_position = last_position + size*direction
                # 更新avg price
                last_avg_price = self.avg_price.latest_long(order)
                # 更新浮动盈亏
                last_holding_pnl = self.holding_pnl.latest_long(order)

                if new_position == 0:
                    new_avg_price = 0
                    new_holding_pnl = 0
                else:
                    new_avg_price = (last_position * last_avg_price +
                                     direction*size*execute_price)/new_position

                    new_holding_pnl = (cur_price - new_avg_price)*new_position

                # 更新已平仓盈亏
                last_realized_pnl = self.realized_pnl.latest_long(order)

                if order.order_type == OrderType.Sell:
                    new_realized_pnl = last_realized_pnl + \
                        (new_avg_price - last_avg_price)*size
                else:
                    new_realized_pnl = last_realized_pnl

                # 更新手续费
                last_commission = self.commission.latest_long(order)

                if self.per_comm_pct:
                    new_commission = last_commission + self.per_comm*size*execute_price
                else:
                    new_commission = last_commission + self.per_comm

                new_market_value = new_position*cur_price
                self.market_value.append_long(order, new_market_value)
                self.position.append_long(order, new_position)
                self.avg_price.append_long(order, new_avg_price)
                self.holding_pnl.append_long(order, new_holding_pnl)
                self.realized_pnl.append_long(order, new_realized_pnl)
                self.commission.append_long(order, new_commission)

            elif self.for_short(order):
                # 更新仓位
                last_position = self.position.latest_short(order)
                new_position = last_position + size*direction
                # 更新avg price
                last_avg_price = self.avg_price.latest_short(order)
                # 更新浮动盈亏
                last_holding_pnl = self.holding_pnl.latest_short(order)

                if new_position == 0:
                    new_avg_price = 0
                    new_holding_pnl = 0
                else:
                    new_avg_price = (last_position * last_avg_price +
                                     direction*size*execute_price)/new_position

                    new_holding_pnl = (cur_price - new_avg_price)*new_position

                # 更新已平仓盈亏
                last_realized_pnl = self.realized_pnl.latest_short(order)

                if order.order_type == OrderType.Short_cover:
                    new_realized_pnl = last_realized_pnl + \
                        (new_avg_price - last_avg_price)*size
                else:
                    new_realized_pnl = last_realized_pnl

                # 更新手续费
                last_commission = self.commission.latest_short(order)

                if self.per_comm_pct:
                    new_commission = last_commission + self.per_comm*size*execute_price
                else:
                    new_commission = last_commission + self.per_comm

                # 更新保证金(股票多头不需要)
                new_margin = new_position*cur_price*self.margin_rate

                new_market_value = new_position*cur_price

                self.market_value.append_short(order, new_market_value)
                self.position.append_short(order, new_position)
                self.avg_price.append_short(order, new_avg_price)
                self.holding_pnl.append_short(order, new_holding_pnl)
                self.realized_pnl.append_short(order, new_realized_pnl)
                self.commission.append_short(order, new_commission)
                self.margin.append_short(order, new_margin)

                self.update_balance_and_cash(order.trading_date)

    def update_balance_and_cash(self, tradidng_date):
        # 更新Balance
        total_realized_pnl = self.realized_pnl.total_value()
        total_holding_pnl = self.holding_pnl.total_value()
        total_commission = self.holding_pnl.total_value()
        total_position = self.position.total_value()
        total_margin = self.margin.total_value()
        total_market_value = self.market_value.total_value()
        new_balance = self.initial_cash + total_realized_pnl + \
            total_holding_pnl - total_commission
        # 更新frozen_cash
        new_frozen_cash = total_margin+total_market_value

        # 更新cash
        new_cash = new_balance - new_frozen_cash

        self.balance['balance'].append({tradidng_date: new_balance})
        self.frozen_cash['frozen_cash'].append(
            {tradidng_date: new_frozen_cash})
        self.cash['cash'].append({tradidng_date: new_cash})

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

    def run(self):
        self.record_order()
        pass

    def update(self):
        """根据最新价格更新信息"""
        pass

    def update_cash(self):
        pass


class StockAccount(object):

    def __init__(self):
        pass

    def cash(self):
        pass

    def frozen_cash(self):
        pass

    def market_value(self):
        pass

    def commission(self):
        pass

    def positions(self):
        pass

    def get_state(self):
        pass

    def set_state(self):
        pass


class StockPosition(object):
    env = Environment

    def __init__(self):
        self.env.position = RecordSeries('position')

    def market_value(self):
        pass

    def commission(self):
        pass

    @property
    def latest(self):
        return self.env.position.latest

    def get_state(self):
        pass

    def set_state(self):
        pass


class Portfolio(object):
    def __init__(self):
        self.initial_cash
        self.cash = None
        self.frozen_cash = None
        self.total_returns = None
        self.daily_returns = None
        self.daily_pnl = None
        self.market_value = None
        self.total_value = None
        self.commission = None
        self.pnl = None
        self.start_date = None
        self.annulized_return = None
        self.positions = None
