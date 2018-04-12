from OnePy.constants import OrderType
from OnePy.sys_module.models.orders.base_order import (OrderBase,
                                                       PendingOrderBase)


class MarketOrder(OrderBase):

    order_type = OrderType.Market

    @property
    def execute_price(self):
        return self.first_cur_price

    def is_pure(self):
        return False if self.mkt_id in self.env.orders_pending_mkt_dict else True

    @property
    def father_mkt_id(self):
        return self.signal.mkt_id


class LimitBuyOrder(PendingOrderBase):
    """
    如果是挂单，只需要判断是不是触发，
    如果触发，就返回执行市价单，而且是必成的那种,而且带着其他挂单
    如果是跟随mkt的挂单，则需要判断是否触发，
        如果触发，就发送一个裸的必成市价单，即要清空signal，剩裸price

    而且如果触发了，要从list中删除
    """
    order_type = OrderType.Limit

    @property
    def target_below(self):
        return True


class LimitSellOrder(PendingOrderBase):
    order_type = OrderType.Limit

    @property
    def target_below(self):
        return False


class StopBuyOrder(LimitSellOrder):
    order_type = OrderType.Stop


class StopSellOrder(LimitBuyOrder):
    order_type = OrderType.Stop


class LimitShortSellOrder(LimitSellOrder):
    order_type = OrderType.Limit


class StopShortSellOrder(StopSellOrder):
    order_type = OrderType.Stop


class LimitCoverShortOrder(LimitBuyOrder):
    order_type = OrderType.Limit


class StopCoverShortOrder(StopBuyOrder):
    order_type = OrderType.Stop
