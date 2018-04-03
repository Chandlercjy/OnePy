from itertools import count

from OnePy.constants import OrderType
from OnePy.environment import Environment
from OnePy.sys_model.orders.general_order import (LimitBuyOrder,
                                                  LimitCoverShortOrder,
                                                  LimitSellOrder,
                                                  LimitShortSellOrder,
                                                  MarketOrder, StopBuyOrder,
                                                  StopCoverShortOrder,
                                                  StopSellOrder,
                                                  StopShortSellOrder)
from OnePy.sys_model.orders.trailing_order import (TrailingStopCoverShortOrder,
                                                   TrailingStopSellOrder,
                                                   TrailingStopShortSellOrder)


class OrderGenerator(object):

    env = Environment
    counter = count(1)

    def __init__(self):
        self.signal = None
        self.mkt_id = None

        self.market_order = None
        self.orders_pending_mkt = None
        self.orders_pending = None

    def initialize(self, signal):
        self.signal = signal
        self.mkt_id = next(self.counter)

        self.market_order = None
        self.orders_pending_mkt = []
        self.orders_pending = []

    @property
    def cur_price(self):
        return self.env.feeds[self.signal.ticker].cur_price

    def is_buy(self):
        return True if self.signal.order_type == OrderType.Buy else False

    def is_sell(self):
        return True if self.signal.order_type == OrderType.Sell else False

    def is_shortsell(self):
        return True if self.signal.order_type == OrderType.Short_sell else False

    def is_shortcover(self):
        return True if self.signal.order_type == OrderType.Short_cover else False

    def is_exitall(self):
        return True if self.signal.order_type == OrderType.Exit_all else False

    def is_cancelall(self):
        return True if self.signal.order_type == OrderType.Cancel_all else False

    def is_absolute_mkt(self):
        return True if self.signal.execute_price else False

    def is_normal_mkt(self):
        return False if self.signal.price or self.signal.price_pct else True

    def is_marketorder(self):
        if self.is_absolute_mkt() or self.is_normal_mkt():
            return True

        return False

    def set_market_order(self):
        self.market_order = MarketOrder(self.signal, self.mkt_id, None)

    def clarify_price_pct(self):
        if self.signal.price_pct:
            self.signal.price = (self.signal.price_pct+1)*self.cur_price

    def child_of_mkt(self, order_class, key):
        if self.signal.get(key):
            self.orders_pending_mkt.append(
                order_class(self.signal, self.mkt_id, key))
        elif self.signal.get(f'{key}_pct'):
            self.orders_pending_mkt.append(
                order_class(self.signal, self.mkt_id, f'{key}_pct'))

    def pending_order_only(self, order_class):
        self.orders_pending.append(order_class(
            self.signal, self.mkt_id, 'price'))

    def _generate_child_order_of_mkt(self):

        if self.is_buy():
            self.child_of_mkt(StopSellOrder, 'stoploss')
            self.child_of_mkt(LimitSellOrder, 'takeprofit')
            self.child_of_mkt(TrailingStopSellOrder, 'trailingstop')

        elif self.is_shortsell():
            self.child_of_mkt(StopCoverShortOrder, 'stoploss')
            self.child_of_mkt(LimitCoverShortOrder, 'takeprofit')
            self.child_of_mkt(
                TrailingStopCoverShortOrder, 'trailingstop')

    def _generate_pending_order_only(self):
        self.clarify_price_pct()

        if self.signal.price > self.cur_price:
            if self.is_buy():
                self.pending_order_only(StopBuyOrder)
            elif self.is_shortcover():
                self.pending_order_only(StopCoverShortOrder)
            elif self.is_sell():
                self.pending_order_only(LimitSellOrder)
            elif self.is_shortsell():
                self.pending_order_only(LimitShortSellOrder)
        elif self.signal.price < self.cur_price:
            if self.is_buy():
                self.pending_order_only(LimitBuyOrder)
            elif self.is_shortcover():
                self.pending_order_only(LimitCoverShortOrder)
            elif self.is_sell():
                self.pending_order_only(StopSellOrder)
            elif self.is_shortsell():
                self.pending_order_only(StopShortSellOrder)
        else:
            self.signal.execute_price = self.cur_price
            self.generate_order()

    def generate_order(self):

        if self.is_exitall():
            pass  # TODO:写逻辑

        elif self.is_cancelall():
            pass  # TODO:写逻辑

        elif self.is_marketorder():
            self.set_market_order()
            self._generate_child_order_of_mkt()

        else:
            self._generate_pending_order_only()

    def submit_order_to_env(self):
        if self.market_order:
            self.env.orders_mkt_original.append(self.market_order)

            if self.is_absolute_mkt():
                self.env.orders_mkt_absolute.append(self.market_order)
            elif self.is_normal_mkt():
                self.env.orders_mkt_normal.append(self.market_order)

            if self.orders_pending_mkt != []:
                self.env.orders_pending_mkt_dict.update(
                    {self.mkt_id: self.orders_pending_mkt})
        else:
            self.env.orders_pending += self.orders_pending

    def process_every_signals_in(self, signals_list):
        for signal in signals_list:
            self.initialize(signal)
            self.generate_order()
            self.submit_order_to_env()

    def clear_current_signals_memory(self):
        self.env.signals_normal_cur = []
        self.env.signals_trigger_cur = []

    def run(self):
        self.process_every_signals_in(self.env.signals_normal_cur)
        self.process_every_signals_in(self.env.signals_trigger_cur)
        self.clear_current_signals_memory()
