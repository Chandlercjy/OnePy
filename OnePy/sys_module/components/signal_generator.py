from OnePy.constants import OrderType
from OnePy.environment import Environment
from OnePy.sys_module.models.signals import Signal, SignalByTrigger


class SignalGenerator(object):

    """存储Signal的信息"""
    env = Environment

    def __init__(self, order_type):
        self.order_type = order_type

    def func_1(self, size, ticker,
               takeprofit=None, takeprofit_pct=None,
               stoploss=None, stoploss_pct=None,
               trailingstop=None, trailingstop_pct=None,
               price=None, price_pct=None):

        return Signal(
            order_type=self.order_type,
            size=size,
            ticker=ticker,
            takeprofit=takeprofit,
            takeprofit_pct=takeprofit_pct,
            stoploss=stoploss,
            stoploss_pct=stoploss_pct,
            trailingstop=trailingstop,
            trailingstop_pct=trailingstop_pct,
            price=price,
            price_pct=price_pct,
        )

    def func_2(self, size, ticker, price=None, price_pct=None):

        return Signal(
            order_type=self.order_type,
            size=size,
            ticker=ticker,
            price=price,
            price_pct=price_pct,
        )


class TriggeredSignalGenerator:

    @classmethod
    def _opposite_order_type(cls, order):
        if order.order_type == OrderType.Buy:
            return OrderType.Sell
        elif order.order_type == OrderType.Short_sell:
            return OrderType.Short_cover

    @classmethod
    def _generate_bare_signal(cls, order):
        return SignalByTrigger(
            order_type=cls._opposite_order_type(order),
            size=order.size,
            ticker=order.ticker,
            execute_price=order.target_price,
            first_cur_price=order.first_cur_price,
            mkt_id=order.mkt_id,
            exec_type=order.__class__.__name__)

    @classmethod
    def _generate_full_signal(cls, order):
        return SignalByTrigger(order_type=order.order_type,
                               size=order.size,
                               ticker=order.ticker,
                               execute_price=order.target_price,
                               price=None, price_pct=None,
                               takeprofit=order.signal.takeprofit,
                               takeprofit_pct=order.signal.takeprofit_pct,
                               stoploss=order.signal.stoploss,
                               stoploss_pct=order.signal.stoploss_pct,
                               trailingstop=order.signal.trailingstop,
                               trailingstop_pct=order.signal.trailingstop_pct,
                               exec_type=order.__class__.__name__)

    @classmethod
    def generate_triggered_signal(cls, order):
        if order.is_triggered:
            if order.is_with_mkt():
                return cls._generate_bare_signal(order)

            return cls._generate_full_signal(order)
