from itertools import count

from OnePy.constants import OrderType
from OnePy.core.base_order import (LimitBuyOrder, LimitCoverShortOrder,
                                   LimitSellOrder, LimitShortSellOrder,
                                   MarketOrder, StopBuyOrder,
                                   StopCoverShortOrder, StopSellOrder,
                                   StopShortSellOrder, TrailingStopSellOrder,
                                   TrailingStopShortSellOrder)
from OnePy.model.signals import Signal


class MarketMaker(object):

    env = None
    gvar = None

    def __init__(self):

        self.data_Buffer = None
        self.ohlc = None
        self.tick_data = None
        self.execute_price = None

    def update_market(self):
        try:
            for bar in self.env.feeds.values():
                bar.next()

            return True
        except StopIteration:
            return False


class SignalGenerator(object):

    """存储Signal的信息"""
    env = None
    gvar = None

    def __init__(self, order_type):
        self.order_type = order_type

    def func_1(self, units, ticker,
               takeprofit=None, takeprofit_pct=None,
               stoploss=None, stoploss_pct=None,
               trailingstop=None, trailingstop_pct=None,
               price=None, price_pct=None):

        return Signal(
            order_type=self.order_type,
            units=units,
            ticker=ticker,
            datetime=self.env.feeds[ticker].date,
            takeprofit=takeprofit,
            takeprofit_pct=takeprofit_pct,
            stoploss=stoploss,
            stoploss_pct=stoploss_pct,
            trailingstop=trailingstop,
            trailingstop_pct=trailingstop_pct,
            price=price,
            price_pct=price_pct,
        )

    def func_2(self, units, ticker, price=None, price_pct=None):

        return Signal(
            order_type=self.order_type,
            units=units,
            ticker=ticker,
            datetime=self.env.feeds[ticker].date,
            price=price,
            price_pct=price_pct,
        )


class OrderGenerator(object):

    env = None
    gvar = None
    counter = count(1)

    def __init__(self, signal):
        self.signal = signal
        self.order_type = signal.order_type
        self.mkt_id = next(self.counter)

        self.market_order = None
        self.orders_pending_mkt = []
        self.orders_pending = []

        self.price_pct = self.signal.price_pct

    @property
    def cur_price(self):
        return self.env.feeds[self.signal.ticker].cur_price

    @property
    def price(self):
        return self.signal.price

    def generate_order(self):

        if self.is_exitall():
            pass  # TODO:写逻辑

        elif self.is_cancelall():
            pass  # TODO:写逻辑

        elif self.is_marketorder():
            self.set_market_order()
            self._generate_pending_order_with_mkt()

        else:
            self._generate_pending_order_without_mkt()

    def submit_order_to_env(self):
        if self.market_order:
            self.env.orders_mkt_original.append(self.market_order)
            self.env.orders_mkt_normal.append(self.market_order)

            if self.orders_pending_mkt != []:
                self.env.orders_pending_mkt_dict.update(
                    {self.mkt_id: self.orders_pending_mkt})
        else:
            self.env.orders_pending += self.orders_pending

    def submit_absolute_mkt_to_env(self):
        self.env.orders_mkt_original.append(self.market_order)
        self.env.orders_mkt_normal.append(self.market_order)

    def _generate_pending_order_with_mkt(self):

        if self.is_buy():
            self.order_with_mkt(StopSellOrder, 'stoploss')
            self.order_with_mkt(LimitSellOrder, 'takeprofit')
            self.order_with_mkt(TrailingStopSellOrder, 'trailingstop')

        elif self.is_shortsell():
            self.order_with_mkt(StopShortSellOrder, 'stoploss')
            self.order_with_mkt(LimitShortSellOrder, 'takeprofit')
            self.order_with_mkt(
                TrailingStopShortSellOrder, 'trailingstop')

    def _generate_pending_order_without_mkt(self):

        if self.price > self.cur_price:
            if self.is_buy():
                self.order_without_mkt(StopBuyOrder)
            elif self.is_shortcover():
                self.order_without_mkt(StopCoverShortOrder)
            elif self.is_sell():
                self.order_without_mkt(LimitSellOrder)
            elif self.is_shortsell():
                self.order_without_mkt(LimitCoverShortOrder)
        elif self.price < self.cur_price:
            if self.is_buy():
                self.order_without_mkt(LimitBuyOrder)
            elif self.is_shortcover():
                self.order_without_mkt(LimitBuyOrder)
            elif self.is_sell():
                self.order_without_mkt(StopSellOrder)
            elif self.is_shortsell():
                self.order_without_mkt(StopShortSellOrder)
        else:
            pass  # TODO: 思考相同情况下会如何

    def make_pct_clearly(self):
        for key in ['takeprofit', 'stoploss', 'trailingstop']:
            pct = self.signal.get(f'{key}_pct')

            if pct:
                units = self.signal.units
                cur_price = self.env.feeds[self.signal.ticker].cur_price
                self.signal.set(key, abs(pct*cur_price*units))

    def order_with_mkt(self, order_class, key):
        if self.signal.get(key) or self.signal.get(f'{key}_pct'):
            self.make_pct_clearly()
            self.orders_pending_mkt.append(
                order_class(self.signal, self.mkt_id, key))

    def order_without_mkt(self, order_class):  # 这里就不计算pct了，因为要挂单成交后才计算。
        self.orders_pending.append(order_class(self.signal, self.mkt_id, None))

    def set_market_order(self):
        self.market_order = MarketOrder(self.signal, self.mkt_id, None)

    def is_marketorder(self):
        """计算price_pct"""

        if self.signal.execute_price:
            return True

        elif self.price:
            return False
        elif self.price_pct:
            self.signal.price = (self.price_pct+1)*self.cur_price

            return False

        self.signal.execute_price = self.env.feeds[self.ticker].execute_price

        return True

    def is_buy(self):
        return True if self.order_type == OrderType.BUY else False

    def is_sell(self):
        return True if self.order_type == OrderType.SELL else False

    def is_shortsell(self):
        return True if self.order_type == OrderType.SHORT_SELL else False

    def is_shortcover(self):
        return True if self.order_type == OrderType.SHORT_COVER else False

    def is_exitall(self):
        return True if self.order_type == OrderType.EXIT_ALL else False

    def is_cancelall(self):
        return True if self.order_type == OrderType.CANCEL_ALL else False
