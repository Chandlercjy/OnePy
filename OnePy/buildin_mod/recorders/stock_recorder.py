from OnePy.constants import OrderType
from OnePy.environment import Environment
from OnePy.sys_mod.base_recorder import RecorderBase
from OnePy.sys_model.record_series import RecordFactory


class StockRecorder(RecorderBase):

    """Docstring for StockRecorder. """

    def __init__(self):
        super().__init__()

        # self.margin = RecordSeries('margin')

    def initialize(self):
        self.initial_cash = 100000
        self.cash = RecordFactory.long_only('cash')
        self.frozen_cash = RecordFactory.long_only('frozen_cash')
        self.position = RecordFactory.long_and_short('position')
        self.avg_price = RecordFactory.long_and_short('avg_price')
        self.holding_pnl = RecordFactory.long_and_short('holding_pnl')
        self.realized_pnl = RecordFactory.long_and_short('realized_pnl')
        self.commission = RecordFactory.long_and_short(
            'commission')
        self.balance = RecordFactory.long_only('balance')

    @property
    def submitted_order(self):
        return self.env.orders_mkt_submitted

    def update_position(self):
        for order in self.submitted_order:
            if self.for_long(order):
                cur_price = self.env.feeds[order.ticker].cur_price
                direction = self.direction(order)
                size = order.size
                execute_price = order.execute_price
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

                if order.order_type == OrderType.Sell:
                    last_realized_pnl = self.realized_pnl.latest_long(order)
                    new_realized_pnl = last_realized_pnl + \
                        (new_avg_price - last_avg_price)*size

                # 更新手续费
                last_commission = self.commission.latest_long(order)
                new_commission = last_commission + order.commission

                self.position.append_long(order, new_position)
            elif self.for_short(order):
                new = self.position.latest_short(order) + \
                    order.size*self.direction(order)

                self.position.append_short(order, new)

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
        self.update_position()
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
