import abc

from OnePy.constants import ActionType
from OnePy.sys_module.components.order_checker import SubmitOrderChecker
from OnePy.sys_module.components.order_generator import OrderGenerator
from OnePy.sys_module.metabase_env import OnePyEnvBase
from OnePy.sys_module.models.orders.general_order import (CancelPendingOrder,
                                                          CancelTSTOrder,
                                                          MarketOrder)


class BrokerBase(OnePyEnvBase, abc.ABC):

    def __init__(self):
        self.env.brokers.update({self.__class__.__name__: self})
        self._checker = SubmitOrderChecker(self._required_cash_func)
        self._order_generator = OrderGenerator()

    def _clear_submited_order(self):
        self.env.orders_mkt_submitted_cur = []
        self.env.orders_cancel_submitted_cur = []

    def _generate_order(self):
        self._order_generator.run()

    def _check_order(self):
        self._checker.run()

    def _submit_order(self):
        # 先处理mkt, 已在checker中处理完成
        # 再处理trigger, 已在checker中处理完成
        # 再处理pending, 已在checker中处理完成
        # 再处理cancel
        self._process_cancel_order()

    def _judge_long_or_short(self, order):
        if order.action_type in [ActionType.Buy, ActionType.Sell]:
            return 'long'
        elif order.action_type in [ActionType.Short, ActionType.Cover]:
            return 'short'

    def _process_cancel_order(self):
        for cancel_order in self.env.orders_cancel_submitted_cur:
            ticker = cancel_order.ticker
            long_or_short = cancel_order.long_or_short

            if isinstance(cancel_order, CancelPendingOrder):
                for order in list(self.env.orders_pending):
                    confirm_ticker = order.ticker == ticker
                    confirm_long_short = self._judge_long_or_short(
                        order) == long_or_short

                    if confirm_ticker and confirm_long_short:
                        if cancel_order.is_target(order):
                            self.env.orders_pending.remove(order)

            elif isinstance(cancel_order, CancelTSTOrder):
                for order_list in self.env.orders_child_of_mkt_dict.values():
                    for order in list(order_list):
                        if cancel_order.is_target(order):
                            order_list.remove(order)

    @abc.abstractclassmethod
    def _required_cash_func(cls, order: MarketOrder):
        raise NotImplementedError

    def run(self):
        self._clear_submited_order()
        self._generate_order()
        self._check_order()
        self._submit_order()
