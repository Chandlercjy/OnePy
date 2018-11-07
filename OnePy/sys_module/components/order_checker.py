from collections import defaultdict
from typing import Optional

from OnePy.constants import ActionType, OrderStatus
from OnePy.sys_module.components.signal_generator import \
    TriggeredSignalGenerator
from OnePy.sys_module.metabase_env import OnePyEnvBase


class PendingOrderChecker(OnePyEnvBase):
    def _check_orders_pending(self):
        for order in self.env.orders_pending[:]:
            if TriggeredSignalGenerator.generate_triggered_signal(order):
                order.status = OrderStatus.Triggered
                self.env.orders_pending.remove(order)  # 成交的单子需要删除

    def _check_orders_pending_with_mkt(self):
        # TODO: 有Flaw，当多个pending order同时触，只用了第一个

        for key in list(self.env.orders_child_of_mkt_dict):
            for order in self.env.orders_child_of_mkt_dict[key]:

                if TriggeredSignalGenerator.generate_triggered_signal(order):
                    order.status = OrderStatus.Triggered
                    del self.env.orders_child_of_mkt_dict[key]

                    break

    def run(self):
        self._check_orders_pending_with_mkt()
        self._check_orders_pending()


class SubmitOrderChecker(OnePyEnvBase):
    def __init__(self, required_cash_func):
        self.required_cash_func = required_cash_func
        self.cash_acumu: float = None
        self.plong_acumu: dict = None
        self.pshort_acumu: dict = None

    @property
    def cur_cash(self) -> float:
        return self.env.recorder.cash[-1]["value"]

    def required_cash(self, order) -> float:
        return self.required_cash_func(order)

    def _lack_of_cash(self) -> bool:
        """用于Buy和Short指令"""

        return True if self.cash_acumu > self.cur_cash else False

    def _lack_of_position(self, cur_position, acumu_position) -> bool:
        """用于Sell指令和Cover指令"""

        if cur_position == 0 or acumu_position > cur_position:
            return True

        return False

    def _add_to_position_cumu(self, order):

        if order.action_type == ActionType.Sell:
            self.plong_acumu[order.ticker] += order.size
        elif order.action_type == ActionType.Cover:
            self.pshort_acumu[order.ticker] += order.size

    def _add_to_cash_cumu(self, order):
        self.cash_acumu += self.required_cash(order)

    def _delete_from_cash_cumu(self, order):
        self.cash_acumu -= self.required_cash(order)

    def _delete_from_position_cumu(self, order):

        if order.action_type == ActionType.Sell:
            self.plong_acumu[order.ticker] -= order.size
        elif order.action_type == ActionType.Cover:
            self.pshort_acumu[order.ticker] -= order.size

    def _make_position_cumu_full(self, order):
        if order.action_type == ActionType.Sell:
            self.plong_acumu[order.ticker] = self.cur_position(order)
        elif order.action_type == ActionType.Cover:
            self.pshort_acumu[order.ticker] = self.cur_position(order)

    def cur_position(self, order) -> Optional[float]:
        """根据order自动判断需要选取long还是short的position"""

        if order.action_type == ActionType.Sell:
            return self.env.recorder.position.latest(order.ticker, "long")
        elif order.action_type == ActionType.Cover:
            return self.env.recorder.position.latest(order.ticker, "short")
        else:
            raise Exception

    def _acumu_position(self, order) -> Optional[float]:
        if order.action_type == ActionType.Sell:
            return self.plong_acumu[order.ticker]
        elif order.action_type == ActionType.Cover:
            return self.pshort_acumu[order.ticker]
        else:
            raise Exception

    def order_pass_checker(self, order):
        order.status = OrderStatus.Submitted
        self.env.orders_mkt_submitted_cur.append(order)

    def _is_partial(self, order, cur_position, acumu_position) -> bool:
        diff = cur_position - (acumu_position - order.size)

        if diff > 0:
            order.size = diff
            order.signal.size = diff
            order.status = OrderStatus.Partial

            return True

        return False

    def _check_normal(self, order_list):

        for order in order_list:

            if order.action_type in [ActionType.Buy, ActionType.Short]:
                self._add_to_cash_cumu(order)

                if self._lack_of_cash():
                    self.env.logger.warning("Cash is not enough for trading!")
                    order.status = OrderStatus.Rejected
                    self._delete_from_cash_cumu(order)

                    if order.mkt_id in self.env.orders_child_of_mkt_dict:
                        del self.env.orders_child_of_mkt_dict[order.mkt_id]

                    continue
            elif order.action_type in [ActionType.Sell, ActionType.Cover]:
                self._add_to_position_cumu(order)
                cur_position = self.cur_position(order)
                acumu_position = self._acumu_position(order)

                if self._lack_of_position(cur_position, acumu_position):
                    if self._is_partial(order, cur_position, acumu_position):
                        self._make_position_cumu_full(order)
                    else:
                        order.status = OrderStatus.Rejected
                        self._delete_from_position_cumu(order)

                        continue
            self.order_pass_checker(order)

    def _check_absolute(self, order_list):
        for order in order_list:
            if order.action_type in [ActionType.Sell, ActionType.Cover]:
                self._add_to_position_cumu(order)
            self.order_pass_checker(order)

    def _check_market_order(self):
        self.cash_acumu = 0
        self.plong_acumu = defaultdict(int)
        self.pshort_acumu = defaultdict(int)

        self._check_absolute(self.env.orders_mkt_absolute_cur)
        self._check_normal(self.env.orders_mkt_normal_cur)

    def _check_pending_order(self):  # TODO: 实盘需要检查
        pass

    def _check_cancel_order(self):
        cancel_orders = self.env.orders_cancel_cur

        for order in cancel_orders:
            order.status = OrderStatus.Submitted
        self.env.orders_cancel_submitted_cur += cancel_orders

    def _clear_all_cur_order(self):
        self.env.orders_mkt_absolute_cur = []
        self.env.orders_mkt_normal_cur = []
        self.env.orders_cancel_cur = []

    def run(self):
        self._check_market_order()
        self._check_pending_order()
        self._check_cancel_order()
        self._clear_all_cur_order()
