from copy import copy
from itertools import count


class OrderBase(object):

    env = None
    gvar = None
    counter = count(1)

    def __init__(self, signal, mkt_id, trigger_key):
        self.trigger_key = trigger_key
        self.signal = signal
        self.ticker = signal.ticker
        self.order_id = next(self.counter)
        self.mkt_id = mkt_id
        self.price = signal.price

    def target_price(self):
        return '计算出来的price'

    def cur_price(self):
        return self.env.feeds[self.ticker].cur_price


class MarketOrder(OrderBase):

    @property
    def execute_price(self):
        """
        price_pct已经在orderGenerator中转换过，
        所以不用考，但是要考虑如果是其他单转化为市价单，
        那price就会不一样
        """

        if self.signal.execute_price:
            return self.signal.execute_price

        elif self.price:
            return self.price


class PendingOrderBase(OrderBase):

    def get_triggered_signal(self):
        if self.is_triggered():
            if self.is_with_mkt():
                return self.generate_bare_signal()
            else:
                return self.generate_full_signal()

    def generate_bare_signal(self):
        return SignalByTrigger(order_type=self.signal.order_type,
                               units=self.signal.units,
                               ticker=self.signal.ticker,
                               price=self.target_price,
                               datetime=self.env.feeds[ticker].date,
                               exec_type=self.__class__.__name__)

    def generate_full_signal(self):
        """重新想一下price的判定思路, 可以考虑给signal加一个金牌"""

        full_signal = copy(self.signal)
        full_signal.execute_price = self.target_price

        return full_signal

    def is_with_mkt(self):
        return False if self.trigger_key else True

    def below_price(self, diff):
        return self.price - diff

    def above_price(self, diff):
        return self.price + diff


class LimitBuyOrder(PendingOrderBase):
    """
    如果是挂单，只需要判断是不是触发，
    如果触发，就返回执行市价单，而且是必成的那种,而且带着其他挂单
    如果是跟随mkt的挂单，则需要判断是否触发，
        如果触发，就发送一个裸的必成市价单，即要清空signal，剩裸price

    而且如果触发了，要从list中删除
    """

    def is_triggered(self):
        if self.target_price > self.cur_price:
            return True

    @property
    def target_price(self):
        if self.trigger_key:
            money = self.signal[self.trigger_key]
            units = self.signal['units']
            result = self.below_price(abs(money/units))

            return result


class LimitSellOrder(PendingOrderBase):

    pass


class StopBuyOrder(PendingOrderBase):

    pass


class StopSellOrder(PendingOrderBase):

    pass


class TralingStopBuyOrder(PendingOrderBase):

    pass


class TrailingStopSellOrder(PendingOrderBase):

    pass


class LimitShortSellOrder(PendingOrderBase):

    pass


class StopShortSellOrder(PendingOrderBase):

    pass


class LimitCoverShortOrder(PendingOrderBase):

    pass


class StopCoverShortOrder(PendingOrderBase):

    pass


class TrailingStopShortSellOrder(PendingOrderBase):
    pass
