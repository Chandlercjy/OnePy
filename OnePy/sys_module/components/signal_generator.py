from OnePy.constants import ActionType
from OnePy.sys_module.metabase_env import OnePyEnvBase
from OnePy.sys_module.models.signals import Signal, SignalByTrigger


class SignalGenerator(OnePyEnvBase):
    def __init__(self, action_type):
        self.action_type = action_type

    def func_1(self, size, ticker,
               takeprofit=None, takeprofit_pct=None,
               stoploss=None, stoploss_pct=None,
               trailingstop=None, trailingstop_pct=None,
               price=None, price_pct=None):  # For Buy, ShortSell

        return Signal(
            action_type=self.action_type,
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

    def func_2(self, size, ticker, price=None, price_pct=None):  # For Sell, ShortCover

        return Signal(
            action_type=self.action_type,
            size=size,
            ticker=ticker,
            price=price,
            price_pct=price_pct,
        )


class TriggeredSignalGenerator:
    """为触发的挂单生成挂单触发信号"""
    @classmethod
    def _generate_bare_signal(cls, order):
        return SignalByTrigger(
            action_type=order.action_type,
            size=order.size,
            ticker=order.ticker,
            execute_price=order.target_price,
            first_cur_price=order.first_cur_price,
            mkt_id=order.mkt_id,
            order_type=order.order_type)

    @classmethod
    def _generate_full_signal(cls, order):
        return SignalByTrigger(action_type=order.action_type,
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
                               order_type=order.order_type)

    @classmethod
    def generate_triggered_signal(cls, order):
        if order.is_triggered:
            if order.is_with_mkt():
                return cls._generate_bare_signal(order)

            return cls._generate_full_signal(order)
