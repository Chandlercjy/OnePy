from OnePy.constants import ActionType, OrderStatus
from OnePy.environment import Environment
from OnePy.sys_module.components.signal_generator import \
    TriggeredSignalGenerator


class PendingOrderChecker(object):
    env = Environment

    def _check_orders_pending(self):
        for order in self.env.orders_pending[:]:
            if self._send_signal(order):
                self.env.orders_pending.remove(order)  # 成交的单子需要删除

    def _check_orders_pending_with_mkt(self):
        for key in list(self.env.orders_pending_mkt_dict):
            for order in self.env.orders_pending_mkt_dict[key]:

                if self._send_signal(order):
                    # TODO: 有Flaw，当多个pending order同时触，只用了第一个
                    del self.env.orders_pending_mkt_dict[key]

                    break

    def _send_signal(self, order):
        if TriggeredSignalGenerator.generate_triggered_signal(order):
            return True

    def run(self):
        self._check_orders_pending_with_mkt()
        self._check_orders_pending()


class SubmitOrderChecker(object):
    env = Environment
    """可能有股票停牌情况"""
    """重新分一下发送订单和检查信号之间的关系"""

    def __init__(self, required_cash_func):
        self.required_cash_func = required_cash_func
        self.cash_acumu = None
        self.plong_acumu = None
        self.pshort_acumu = None

    @property
    def cur_cash(self):
        return self.env.gvar.cash[-1]['value']

    def required_cash(self, order):
        return self.required_cash_func(order)

    def _lack_of_cash(self, order):  # 用于Buy和Short Sell
        if order.action_type in [ActionType.Buy, ActionType.Short_sell]:
            return True if self.cash_acumu > self.cur_cash else False

    def _lack_of_position(self, cur_position, acumu_position):  # 用于Sell指令和Cover指令
        if cur_position == 0 or acumu_position > cur_position:
            return True

        return False

    def add_to_cumu(self, order):
        self.cash_acumu += self.required_cash(order)

        if order.action_type == ActionType.Sell:
            self.plong_acumu += order.size
        elif order.action_type == ActionType.Short_cover:
            self.pshort_acumu += order.size

    def delete_from_cumu(self, order):
        self.cash_acumu -= self.required_cash(order)

        if order.action_type == ActionType.Sell:
            self.plong_acumu -= order.size
        elif order.action_type == ActionType.Short_cover:
            self.pshort_acumu -= order.size

    def order_rejected(self, order):
        order.status = OrderStatus.Rejected
        self.delete_from_cumu(order)

    def cur_position(self, order):
        """根据order自动判断需要选取long还是short的position"""

        if order.action_type == ActionType.Sell:
            return self.env.gvar.position.latest(order.ticker, 'long')
        elif order.action_type == ActionType.Short_cover:
            return self.env.gvar.position.latest(order.ticker, 'short')

    def acumu_position(self, order):
        if order.action_type == ActionType.Sell:
            return self.plong_acumu
        elif order.action_type == ActionType.Short_cover:
            return self.pshort_acumu

    def order_pass_checker(self, order):
        order.status = OrderStatus.Submitted
        self.env.orders_mkt_submitted.append(order)

    def is_partial(self, order, cur_position, acumu_position):
        diff = cur_position-(acumu_position-order.size)

        if diff > 0:
            order.size = diff
            order.status = OrderStatus.Partial

            return True

    def _check(self, order_list):

        for order in order_list:
            self.add_to_cumu(order)

            if order.action_type in [ActionType.Buy, ActionType.Short_sell]:
                if self._lack_of_cash(order):
                    self.order_rejected(order)

                    continue
            else:

                cur_position = self.cur_position(order)
                acumu_position = self.acumu_position(order)

                if self._lack_of_position(cur_position, acumu_position):
                    if self.is_partial(order, cur_position, acumu_position):
                        pass
                    else:
                        self.order_rejected(order)

                        continue

            self.order_pass_checker(order)

    def _check_market_order(self):
        self.cash_acumu = 0
        self.plong_acumu = 0
        self.pshort_acumu = 0

        self._check(self.env.orders_mkt_absolute)
        self._check(self.env.orders_mkt_normal)

    def _check_pending_order(self):
        pass  # TODO: 实盘需要检查

    def _clear_all_mkt_order(self):
        self.env.orders_mkt_absolute = []
        self.env.orders_mkt_normal = []

    def run(self):
        self._check_market_order()
        self._check_pending_order()
        self._clear_all_mkt_order()
