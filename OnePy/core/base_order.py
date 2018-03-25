
from enum import Enum
from itertools import count


class ActionType(Enum):

    BUY = 'buy'
    SELL = 'sell'
    SHORT = 'short'
    Cover = 'Cover'

    EXIT_ALL = 'exit_all'
    CANCEL_ALL = 'cancel_all'


class OrderType(Enum):

    MARKET = 'market'
    LIMIT = 'limit'
    STOP = 'stop'
    TRAILING_STOP = 'trailing_stop'

    LIMIT_PCT = 'limit_pct'
    STOP_PCT = 'stop_pct'
    TRAILING_STOP_PCT = 'trailing_stop_pct'

    BUY = 'buy'
    SELL = 'sell'
    SHORT_SELL = 'short_sell'
    SHORT_COVER = 'short_cover'
    EXIT_ALL = 'exit_all'
    CANCEL_ALL = 'cancel_all'


class ExecTypes(Enum):

    MARKET_ORDER = "MarketOrder"

    LIMIT_SELL = 'limit_sell'
    LIMIT_BUY = 'limit_buy'
    STOP_BUY = 'stop_buy'
    STOP_SELL = 'stop_sell'
    TRAILING_STOP_BUY = 'trailing_stop_buy'
    TRAILING_STOP_SELL = 'trailing_stop_sell'

    LIMIT_SHORT_SELL = 'limit_short_sell'
    STOP_SHORT_SELL = 'stop_short_sell'
    LIMIT_COVER_SHORT = 'limit_cover_short'
    STOP_COVER_SHORT = 'stop_cover_short'
    TRAILING_STOP_SHORT_SELL = 'trailing_stop_short_sell'

    EXIT_ALL = 'exit_all'
    CLOSE_ALL = "close_all"


class OrderBase(object):

    env = None
    gvar = None
    counter = count(1)

    def __init__(self, signal, mkt_id):
        self.signal = signal
        self.ticker = signal['ticker']
        self.execute_price = None
        self.order_id = next(self.counter)
        self.mkt_id = mkt_id

    def make_pct_clearly(self):
        for key in ['takeprofit', 'stoploss', 'trailingstop']:
            pct = self.signal[f'{key}_pct']

            if pct:
                unit = self.signal['unit']
                cur_price = self.env.feeds[self.signal['ticker']].cur_price
                self.signal[key] = abs(pct*cur_price*unit)


class MarketOrder(OrderBase):

    def target_price(self):
        return '计算出来的price'

    def current_price(self):
        return self.env.feeds[self.ticker].close


class LimitBuyOrder(OrderBase):

    pass


class LimitSellOrder(OrderBase):

    pass


class StopBuyOrder(OrderBase):

    pass


class StopSellOrder(OrderBase):

    pass


class TralingStopBuyOrder(OrderBase):

    pass


class TrailingStopSellOrder(OrderBase):

    pass


class LimitShortSellOrder(OrderBase):

    pass


class StopShortSellOrder(OrderBase):

    pass


class LimitCoverShortOrder(OrderBase):

    pass


class StopCoverShortOrder(OrderBase):

    pass


class TrailingStopShortSellOrder(OrderBase):
    pass
