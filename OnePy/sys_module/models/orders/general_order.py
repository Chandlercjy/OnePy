from OnePy.constants import ActionType, OrderType
from OnePy.sys_module.models.orders.base_order import (OrderBase,
                                                       PendingOrderBase,
                                                       TrailingOrderBase)


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

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value
        self.env.logger.info(
            f'{self.signal.datetime}, '
            f'{self.signal.ticker}, '
            f'{self.order_type.value} '
            f'{self.action_type.value} '
            f'@ {self.execute_price:.5f}, '
            f'{self.status.value}, '
            f'size: {self.size}')


class LimitBuyOrder(PendingOrderBase):
    """
    如果是挂单，只需要判断是不是触发，
    如果触发，就返回执行市价单，而且是必成的那种,而且带着其他挂单
    如果是跟随mkt的挂单，则需要判断是否触发，
        如果触发，就发送一个裸的必成市价单，即要清空signal，剩裸price

    而且如果触发了，要从list中删除
    """
    _action_type = ActionType.Buy
    order_type = OrderType.Limit

    @property
    def target_below(self):
        return True


class LimitSellOrder(PendingOrderBase):
    _action_type = ActionType.Sell
    order_type = OrderType.Limit

    @property
    def target_below(self):
        return False


class StopBuyOrder(LimitSellOrder):
    _action_type = ActionType.Buy
    order_type = OrderType.Stop


class StopSellOrder(LimitBuyOrder):
    _action_type = ActionType.Sell
    order_type = OrderType.Stop


class LimitShortSellOrder(LimitSellOrder):
    _action_type = ActionType.Short_sell
    order_type = OrderType.Limit


class StopShortSellOrder(StopSellOrder):
    _action_type = ActionType.Short_sell
    order_type = OrderType.Stop


class LimitCoverShortOrder(LimitBuyOrder):
    _action_type = ActionType.Short_cover
    order_type = OrderType.Limit


class StopCoverShortOrder(StopBuyOrder):
    _action_type = ActionType.Short_cover
    order_type = OrderType.Stop


class TrailingStopSellOrder(TrailingOrderBase):
    _action_type = ActionType.Sell
    order_type = OrderType.Trailing_stop

    @property
    def target_below(self):
        return True


class TrailingStopCoverShortOrder(TrailingOrderBase):
    _action_type = ActionType.Short_cover
    order_type = OrderType.Trailing_stop

    @property
    def target_below(self):
        return False
