from OnePy.sys_model.orders.base_order import TrailingOrderBase


class TrailingStopBuyOrder(TrailingOrderBase):

    @property
    def target_below(self):
        return False


class TrailingStopSellOrder(TrailingOrderBase):

    @property
    def target_below(self):
        return True


class TrailingStopShortSellOrder(TrailingStopSellOrder):
    pass
