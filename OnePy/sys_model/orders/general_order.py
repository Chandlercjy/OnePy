from OnePy.constants import OrderType
from OnePy.sys_model.orders.base_order import OrderBase, PendingOrderBase


class MarketOrder(OrderBase):

    @property
    def execute_price(self):
        if self.is_absolute_mkt():
            return self.signal.execute_price

        return self.env.feeds[self.ticker].execute_price

    def is_absolute_mkt(self):
        return True if self.signal.execute_price else False

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
    order_type = OrderType.Buy

    @property
    def target_below(self):
        return True


class LimitSellOrder(PendingOrderBase):
    order_type = OrderType.Sell

    @property
    def target_below(self):
        return False


class StopBuyOrder(LimitSellOrder):
    pass


class StopSellOrder(LimitBuyOrder):
    pass


class LimitShortSellOrder(LimitSellOrder):
    order_type = OrderType.Short_sell


class StopShortSellOrder(StopSellOrder):
    order_type = OrderType.Short_sell


class LimitCoverShortOrder(LimitBuyOrder):
    order_type = OrderType.Short_cover


class StopCoverShortOrder(StopBuyOrder):
    order_type = OrderType.Short_cover
