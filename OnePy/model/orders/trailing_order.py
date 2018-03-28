from OnePy.model.orders.base_order import TrailingOrderBase


class TralingStopBuyOrder(TrailingOrderBase):

    @property
    def target_price(self):
        if self.trigger_key:
            result = self.above_price(abs(self.money/self.units))

            return result

    def is_triggered(self):
        if self.target_price < self.cur_price:
            return True


class TrailingStopSellOrder(TrailingOrderBase):

    @property
    def target_price(self):
        if self.trigger_key:
            result = self.above_price(abs(self.money/self.units))

            return result

    def is_triggered(self):
        if self.target_price < self.cur_price:
            return True


class TrailingStopShortSellOrder(TrailingOrderBase):

    @property
    def target_price(self):
        if self.trigger_key:
            result = self.above_price(abs(self.money/self.units))

            return result

    def is_triggered(self):
        if self.target_price < self.cur_price:
            return True