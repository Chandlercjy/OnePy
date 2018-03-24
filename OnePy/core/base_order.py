from enum import Enum

from OnePy.event import EVENT, Event


class OrderType(Enum):
    BUY = 'buy'
    SELL = 'sell'
    SHORT_SELL = 'short_sell'
    SHORT_COVER = 'short_cover'
    EXIT_ALL = 'exit_all'
    CANCEL_ALL = 'cancel_all'


class ExecTypes(Enum):

    MARKET_ORDER = "MarketOrder"
    LIMIT_ORDER = "LimitOrder"
    STOP_ORDER = "StopOrder"
    STOP_LOSS_ORDER = "StopLossOrder"
    TAKE_PROFIT_ORDER = "TakeProfitOrder"
    TRALING_STOPLOSS_ORDER = "TralingStopLossOrder"
    CLOSE_ALL = "CloseAll"

    LIMIT_SELL = 'limit_sell'
    LIMIT_BUY = 'limit_buy'
    STOP_SELL = 'stop_sell'
    STOP_BUY = 'stop_buy'
    TRAILING_STOP_BUY = 'trailing_stop_buy'
    TRAILING_STOP_SELL = 'trailing_stop_sell'


class SignalGenerator(object):

    """存储Order的信息"""
    env = None
    gvar = None
    order_list = []

    def __init__(self, order_type):
        self.order_type = order_type

    def order_func(self, units, ticker, takeprofit=None, stoploss=None,
                   trailingstop=None, price=None):
        """TODO: to be defined1.

        :units: TODO
        :takeprofit: TODO
        :stoploss: TODO
        :trailingstop: TODO
        :ticker: TODO
        :price: TODO

        """
        self.units = units
        self.ticker = ticker
        self.takeprofit = takeprofit
        self.stoploss = stoploss
        self.trailingstop = trailingstop
        self.price = price
        # self.execute_price = self.env.execu
        self.order_list.append(self)
