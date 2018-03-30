from OnePy.components.order_generator import OrderGenerator
from OnePy.constants import OrderStatus, OrderType
from OnePy.environment import Environment


class PendingOrderChecker(object):
    env = Environment()

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
    """可能有股票停牌情况"""
    """重新分一下发送订单和检查信号之间的关系"""
    env = Environment()

    def check_market_order(self):
        self._check(self.env.orders_mkt_absolute)
        self._check(self.env.orders_mkt_normal)

    def check_pending_order(self):
        pass  # TODO: 实盘需要检查

    def _check(self, order_list):
        for order in order_list:
            if self._is_buy_or_shortsell(order):
                if self._lack_of_cash(order):
                    order.status = OrderStatus.Rejected

                    continue
            elif self._is_sell_or_shortcover(order):
                if self._lack_of_position(order):
                    order.status = OrderStatus.Rejected

                    continue

            order.status = OrderStatus.Submitted
            self.orders_mkt_submitted.append(order)

    def _lack_of_cash(self, order):  # 用于Buy和Short Sell指令
        return True if self.cash < self.required_cash(order) else False

    def _lack_of_position(self, order):  # 用于Sell指令和Cover指令
        return True if self.position(order.ticker) < self.required_position(order) else False

    def _is_buy_or_shortsell(self, order):
        if order.order_type in [OrderType.Buy, OrderType.Short_sell]:
            return True

    def _is_sell_or_shortcover(self, order):
        if order.order_type in [OrderType.Sell, OrderType.Short_cover]:
            return True

    def position(self, ticker):
        return self.env.gvar.position.latest(ticker)

    def cash(self, ticker):
        return self.env.gvar.cash

    def run(self):
        self.check_market_order()
        self.check_pending_order()
