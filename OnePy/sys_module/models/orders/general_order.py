from OnePy.constants import ActionType, OrderStatus, OrderType
from OnePy.sys_module.models.orders.base_order import (CancelOrderBase,
                                                       OrderBase,
                                                       PendingOrderBase,
                                                       TrailingOrderBase)
from OnePy.sys_module.models.signals import (Signal, SignalCancelPending,
                                             SignalCancelTST)


class MarketOrder(OrderBase):

    order_type: OrderType = OrderType.Market

    def __init__(self, signal: Signal, mkt_id: int) -> None:
        super().__init__(signal, mkt_id)
        self.long_or_short = self._set_long_or_short()

    @property
    def execute_price(self) -> float:
        return self.first_cur_price

    def is_pure(self) -> bool:
        return self.mkt_id not in self.env.orders_child_of_mkt_dict

    @property
    def father_mkt_id(self):
        return self.signal.mkt_id

    @property
    def status(self) -> OrderStatus:
        return self._status

    @status.setter
    def status(self, value: OrderStatus):
        self._status = value
        self.env.logger.info(
            f'{self.signal.datetime}, '
            f'{self.signal.ticker}, '
            f'{self.order_type.value} '
            f'{self.action_type.value} '
            f'@ {self.execute_price:.5f}, '
            f'{self.status.value}, '
            f'size: {self.size}')

    @property
    def action_type(self) -> ActionType:
        return self.signal.action_type

    def _set_long_or_short(self):
        if self.signal.action_type in [ActionType.Buy, ActionType.Sell]:
            return 'long'
        elif self.signal.action_type in [ActionType.Short, ActionType.Cover]:
            return 'short'


class LimitBuyOrder(PendingOrderBase):
    """
    如果是挂单，只需要判断是不是触发，
    如果触发，就返回执行市价单，而且是必成的那种,而且带着其他挂单
    如果是跟随mkt的挂单，则需要判断是否触发，
        如果触发，就发送一个裸的必成市价单，即要清空signal，剩裸price

    而且如果触发了，要从list中删除
    """
    _action_type: ActionType = ActionType.Buy
    order_type: OrderType = OrderType.Limit

    @property
    def target_below(self) -> bool:
        return True


class LimitSellOrder(PendingOrderBase):
    _action_type: ActionType = ActionType.Sell
    order_type: OrderType = OrderType.Limit

    @property
    def target_below(self) -> bool:
        return False


class StopBuyOrder(LimitSellOrder):
    _action_type: ActionType = ActionType.Buy
    order_type: OrderType = OrderType.Stop


class StopSellOrder(LimitBuyOrder):
    _action_type: ActionType = ActionType.Sell
    order_type: OrderType = OrderType.Stop


class LimitShortOrder(LimitSellOrder):
    _action_type: ActionType = ActionType.Short
    order_type: OrderType = OrderType.Limit


class StopShortOrder(StopSellOrder):
    _action_type: ActionType = ActionType.Short
    order_type: OrderType = OrderType.Stop


class LimitCoverOrder(LimitBuyOrder):
    _action_type: ActionType = ActionType.Cover
    order_type: OrderType = OrderType.Limit


class StopCoverOrder(StopBuyOrder):
    _action_type: ActionType = ActionType.Cover
    order_type: OrderType = OrderType.Stop


class TrailingStopSellOrder(TrailingOrderBase):
    _action_type: ActionType = ActionType.Sell
    order_type: OrderType = OrderType.Trailing_stop

    @property
    def target_below(self) -> bool:
        return True


class TrailingStopCoverOrder(TrailingOrderBase):
    _action_type: ActionType = ActionType.Cover
    order_type: OrderType = OrderType.Trailing_stop

    @property
    def target_below(self) -> bool:
        return False


class CancelTSTOrder(CancelOrderBase):

    def __init__(self, signal: SignalCancelTST) -> None:
        super().__init__(signal)
        self.takeprofit = signal.takeprofit
        self.stoploss = signal.stoploss
        self.trailingstop = signal.trailingstop

    def is_target(self, order) -> bool:
        trigger_key = order.trigger_key

        if 'pct' in trigger_key:
            trigger_key = trigger_key.replace('_pct', '')

        return getattr(self, trigger_key)


class CancelPendingOrder(CancelOrderBase):

    def __init__(self, signal: SignalCancelPending) -> None:
        super().__init__(signal)
        self.below_price = signal.below_price
        self.above_price = signal.above_price

    def is_target(self, order) -> bool:
        if self.below_price is not None:
            return order.target_price <= self.below_price
        elif self.above_price is not None:
            return order.target_price >= self.above_price
        else:
            raise Exception
