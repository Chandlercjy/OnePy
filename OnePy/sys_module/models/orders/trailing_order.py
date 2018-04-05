from OnePy.constants import OrderType
from OnePy.sys_module.models.orders.base_order import TrailingOrderBase


class TrailingStopBuyOrder(TrailingOrderBase):
    order_type = OrderType.Buy

    @property
    def target_below(self):
        return False


class TrailingStopSellOrder(TrailingOrderBase):
    order_type = OrderType.Sell

    @property
    def target_below(self):
        return True


class TrailingStopShortSellOrder(TrailingStopSellOrder):
    order_type = OrderType.Short_sell


class TrailingStopCoverShortOrder(TrailingStopBuyOrder):
    order_type = OrderType.Short_cover
