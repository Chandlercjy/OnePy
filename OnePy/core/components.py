from itertools import count

from OnePy.core.base_order import StopSellOrder, LimitSellOrder, TrailingStopSellOrder, StopShortSellOrder, \
    LimitShortSellOrder, TrailingStopShortSellOrder, StopBuyOrder, StopCoverShortOrder, LimitCoverShortOrder, \
    LimitBuyOrder, MarketOrder, OrderType


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
    counter = count(0)

    def __init__(self, order_type):
        self.order_type = order_type

        self.units = None
        self.ticker = None
        self.takeprofit = None
        self.stoploss = None
        self.trailingstop = None
        self.price = None
        self.signal_id = next(self.counter)

    def func_1(self, units, ticker,
               takeprofit=None, takeprofit_pct=None,
               stoploss=None, stoploss_pct=None,
               trailingstop=None, trailingstop_pct=None,
               price=None, price_pct=None):

        signal = dict(
            order_type=self.order_type,
            units=units,
            ticker=ticker,
            takeprofit=takeprofit,
            takeprofit_pct=takeprofit_pct,
            stoploss=stoploss,
            stoploss_pct=stoploss_pct,
            trailingstop=trailingstop,
            trailingstop_pct=trailingstop_pct,
            price=price,
            price_pct=price_pct,
            datetime=self.env.feeds[ticker].date,
            signal_id=self.signal_id
        )

        self.save_signals(signal)
        self.check_conflict(
            signal, ['takeprofit', 'stoploss', 'trailingstop', 'price'])

    def func_2(self, units, ticker, price=None, price_pct=None):

        signal = dict(
            order_type=self.order_type,
            units=units,
            ticker=ticker,
            price=price,
            price_pct=price_pct,
            datetime=self.env.feeds[ticker].date,
            signal_id=self.signal_id
        )

        self.save_signals(signal)
        self.check_conflict(signal, ['price'])

    def save_signals(self, signal):
        self.env.signals.append(signal)
        self.env.signals_current.append(signal)

    @staticmethod
    def check_conflict(signal, keys):
        for key in keys:
            if signal[key] and signal[f'{key}_pct']:
                raise Exception("$ and pct can't be set together")


class OrderGenerator(object):

    env = None
    gvar = None
    counter = count(1)

    def __init__(self, signal):
        self.signal = signal
        self.order_type = signal['order_type']
        self.mkt_id = next(self.counter)
        self.cur_price = self.env.feeds[self.signal['ticker']].cur_price
        self.market_order = None
        self.orders_pending_mkt = []
        self.orders_pending = []

        self.price_pct = self.signal['price_pct']

    @property
    def price(self):
        return self.signal['price']

    def generate_order(self):

        if self.is_exitall():
            pass  # TODO:写逻辑

        elif self.is_cancelall():
            pass  # TODO:写逻辑

        elif self.is_marketorder():
            self.set_market_order()
            self.generate_pending_order_with_mkt()

        else:
            self.generate_pending_order_without_mkt()

    def submit_order_to_env(self):
        if self.market_order:
            self.env.orders_mkt_original.append(self.market_order)
            self.env.orders_mkt.append(self.market_order)

            if self.orders_pending_mkt != []:
                self.env.orders_pending_mkt_dict.update(
                    {self.mkt_id: self.orders_pending_mkt})
        else:
            self.env.orders_pending += self.orders_pending

    def generate_pending_order_with_mkt(self):

        if self.is_buy():
            self.order_with_mkt(StopSellOrder, 'stoploss')
            self.order_with_mkt(LimitSellOrder, 'takeprofit')
            self.order_with_mkt(TrailingStopSellOrder, 'trailingstop')

        elif self.is_shortsell():
            self.order_with_mkt(StopShortSellOrder, 'stoploss')
            self.order_with_mkt(LimitShortSellOrder, 'takeprofit')
            self.order_with_mkt(
                TrailingStopShortSellOrder, 'trailingstop')

    def generate_pending_order_without_mkt(self):

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

    def order_with_mkt(self, order_class, key):
        if self.signal[key] or self.signal[f'{key}_pct']:
            self.orders_pending_mkt.append(
                order_class(self.signal, self.mkt_id))

    def order_without_mkt(self, order_class):
        self.orders_pending.append(order_class(self.signal, self.mkt_id))

    def set_market_order(self):
        self.market_order = MarketOrder(self.signal, self.mkt_id)

    def is_marketorder(self):
        return self.no_price_specified()

    def no_price_specified(self):
        if self.price:
            return False
        elif self.price_pct:
            self.signal['price'] = (self.price_pct+1)*self.cur_price

            return False

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