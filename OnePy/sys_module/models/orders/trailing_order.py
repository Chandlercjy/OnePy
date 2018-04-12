from OnePy.constants import OrderType
from OnePy.sys_module.models.orders.base_order import TrailingOrderBase


class TrailingStopBuyOrder(TrailingOrderBase):
    order_type = OrderType.Trailing_stop

    @property
    def target_below(self):
        return False


class TrailingStopSellOrder(TrailingOrderBase):
    order_type = OrderType.Trailing_stop

    @property
    def target_below(self):
        return True


class TrailingStopShortSellOrder(TrailingStopSellOrder):
    order_type = OrderType.Trailing_stop


class TrailingStopCoverShortOrder(TrailingStopBuyOrder):
    order_type = OrderType.Trailing_stop
