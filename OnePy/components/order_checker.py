from OnePy.components.order_generator import OrderGenerator
from OnePy.constants import OrderStatus, OrderType
from OnePy.environment import Environment


class PendingOrderChecker(object):
    env = Environment

    def check_orders_pending(self):
        for order in self.env.orders_pending:
            self.send_signal(order)

    def check_orders_pending_with_mkt(self):
        for key in list(self.env.orders_pending_mkt_dict):
            for order in self.env.orders_pending_mkt_dict[key]:

                if self.send_signal(order):
                    # TODO: 有Flaw，当多个pending order同时触，只用了第一个
                    del self.env.orders_pending_mkt_dict[key]

                    break

    def send_signal(self, order):
        signal = order.get_triggered_signal()

        if signal:
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
        self.cash_left = None

    @property
    def cash(self):
        return self.env.gvar.cash[-1]['value']

    def position(self, order):
        if order.order_type == OrderType.Sell:
            return self.env.gvar.position.latest(order.ticker, 'long')

        return self.env.gvar.position.latest(order.ticker, 'short')

    def required_cash(self, order):
        return self.required_cash_func(order)

    def required_position(self, order):
        return abs(order.size)

    def _lack_of_cash(self, order):  # 用于Buy和Short Sell指令
        return True if self.cash_left < self.required_cash(order) else False

    def _lack_of_position(self, order):  # 用于Sell指令和Cover指令
        return True if self.position(order) < self.required_position(order) else False

    def _is_buy_or_shortsell(self, order):
        if order.order_type in [OrderType.Buy, OrderType.Short_sell]:
            return True

    def _is_sell_or_shortcover(self, order):
        if order.order_type in [OrderType.Sell, OrderType.Short_cover]:
            return True

    def _check(self, order_list):
        for order in order_list:
            if self._is_buy_or_shortsell(order):
                # TODO:检查思路有问题，因为一些订单成交后cash可能就不够了，不可能能够继续submit

                if self._lack_of_cash(order):
                    order.status = OrderStatus.Rejected

                    continue
            elif self._is_sell_or_shortcover(order):
                if self._lack_of_position(order):  # TODO:部分成交
                    order.status = OrderStatus.Rejected

                    continue

            self.cash_left -= order.size*order.execute_price
            order.status = OrderStatus.Submitted
            self.env.orders_mkt_submitted.append(order)

    def check_market_order(self):
        self.cash_left = self.cash
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
