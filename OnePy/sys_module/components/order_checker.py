from OnePy.constants import OrderStatus, OrderType
from OnePy.environment import Environment
from OnePy.sys_module.components.signal_generator import \
    TriggeredSignalGenerator


class PendingOrderChecker(object):
    env = Environment

    def check_orders_pending(self):
        for order in self.env.orders_pending:
            self.send_signal(order)
            # TODO：成交的单子需要删除

    def check_orders_pending_with_mkt(self):
        for key in list(self.env.orders_pending_mkt_dict):
            for order in self.env.orders_pending_mkt_dict[key]:

                if self.send_signal(order):
                    # TODO: 有Flaw，当多个pending order同时触，只用了第一个
                    del self.env.orders_pending_mkt_dict[key]

                    break

    def send_signal(self, order):
        if TriggeredSignalGenerator.generate_triggered_signal(order):
            return True

    def run(self):
        self.check_orders_pending_with_mkt()
        self.check_orders_pending()


class SubmitOrderChecker(object):
    env = Environment
    """可能有股票停牌情况"""
    """重新分一下发送订单和检查信号之间的关系"""

    def __init__(self, required_cash_func):
        self.required_cash_func = required_cash_func
        self.cash_acumulate = None
        self.position_long_cumu = None
        self.position_short_cumu = None

    @property
    def cash(self):
        return self.env.gvar.cash[-1]['value']

    def position_long(self, order):
        return self.env.gvar.position.latest(order.ticker, 'long')

    def position_short(self, order):
        return self.env.gvar.position.latest(order.ticker, 'short')

    def required_cash(self, order):
        return self.required_cash_func(order)

    def _lack_of_cash(self, order):  # 用于Buy和Short Sell
        if order.order_type in [OrderType.Buy, OrderType.Short_sell]:
            return True if self.cash_acumulate > self.cash else False

    def _lack_of_position(self, order):  # 用于Sell指令和Cover指令

        if order.order_type == OrderType.Sell:
            if self.position_long_cumu >= self.position_long(order):
                return True

        elif order.order_type == OrderType.Short_cover:
            if self.position_short_cumu >= self.position_short(order):
                return True

        return False

    def _check(self, order_list):
        for order in order_list:
            if self._lack_of_cash(order) or self._lack_of_position(order):
                order.status = OrderStatus.Rejected

                continue
            self.add_cash(order)
            self.add_position(order)
            order.status = OrderStatus.Submitted
            self.env.orders_mkt_submitted.append(order)

    def add_cash(self, order):
        self.cash_acumulate += self.required_cash(order)

    def add_position(self, order):
        if order.order_type == OrderType.Sell:
            self.position_long_cumu += order.size
        elif order.order_type == OrderType.Short_cover:
            self.position_short_cumu += order.size

    def check_market_order(self):
        self.cash_acumulate = 0
        self.position_long_cumu = 0
        self.position_short_cumu = 0

        self._check(self.env.orders_mkt_absolute)
        self._check(self.env.orders_mkt_normal)

    def check_pending_order(self):
        pass  # TODO: 实盘需要检查

    def clear_all_mkt_order(self):
        self.env.orders_mkt_absolute = []
        self.env.orders_mkt_normal = []

    def run(self):
        self.check_market_order()
        self.check_pending_order()
        self.clear_all_mkt_order()
