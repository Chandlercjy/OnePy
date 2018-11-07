from typing import Optional

from OnePy.constants import ActionType
from OnePy.sys_module.components.exceptions import OrderConflictError
from OnePy.sys_module.metabase_env import OnePyEnvBase
from OnePy.sys_module.models.orders.base_order import PendingOrderBase
from OnePy.sys_module.models.signals import (Signal, SignalByTrigger,
                                             SignalCancelPending,
                                             SignalCancelTST, SignalForPending)


class SignalGenerator(OnePyEnvBase):
    def __init__(self, action_type, strategy_name) -> None:
        self.action_type = action_type  # type:ActionType
        self.strategy_name = strategy_name

    def settle_price_pct(self, ticker, price, price_pct):
        if price and price_pct:
            raise OrderConflictError("$ and pct can't be set together")

        elif price_pct:
            price = (price_pct+1) * self.env.feeds[ticker].cur_price
            price_pct = None

        return price, None

    def get_signal(self, kwargs):
        """
        发送信号分三种情况：
        1. 挂单。直接通过。
        2. 市价单。
            1. 判断当前是否停牌，若停牌，则不生成信号
        """
        ticker = kwargs['ticker']

        if kwargs['price']:
            return SignalForPending(**kwargs)

        if ticker in self.env.cur_suspended_tickers:  # 停牌不生成信号
            return

        return Signal(**kwargs)

    def buy_or_short(self, size: int, ticker: str,
                     takeprofit: float = None,
                     takeprofit_pct: float = None,
                     stoploss: float = None,
                     stoploss_pct: float = None,
                     trailingstop: float = None,
                     trailingstop_pct: float = None,
                     price: float = None,
                     price_pct: float = None) -> Signal:
        """
        For Buy, ShortSell

        size: int, 
        ticker: str,
        takeprofit: float , 单位为元
        takeprofit_pct: float , 范围为(-1,1)
        stoploss: float , 单位为元
        stoploss_pct: float , 范围为(-1,1)
        trailingstop: float , 单位为元
        trailingstop_pct: float , 范围为(-1,1)
        price: float 
        price_pct: float , 范围为(-1,1)

        """

        price, price_pct = self.settle_price_pct(ticker, price, price_pct)

        kwargs = {
            'strategy_name': self.strategy_name,
            'action_type': self.action_type,
            'size': size,
            'ticker': ticker,
            'takeprofit': takeprofit,
            'takeprofit_pct': takeprofit_pct,
            'stoploss': stoploss,
            'stoploss_pct': stoploss_pct,
            'trailingstop': trailingstop,
            'trailingstop_pct': trailingstop_pct,
            'price': price,
            'price_pct': price_pct}

        return self.get_signal(kwargs)

    def sell_or_cover(self, size: int, ticker: str,
                      price: float = None, price_pct: float = None) -> Signal:
        """For Sell, ShortCover"""

        price, price_pct = self.settle_price_pct(ticker, price, price_pct)

        kwargs = {'strategy_name': self.strategy_name,
                  'action_type': self.action_type,
                  'size': size,
                  'ticker': ticker,
                  'price': price,
                  'price_pct': price_pct}

        return self.get_signal(kwargs)

    def cancel_tst(self, ticker: str, long_or_short: str,
                   takeprofit: bool = False, stoploss: bool = False,
                   trailingstop: bool = False):

        if long_or_short not in ['long', 'short']:
            raise ValueError("long_or_short should be long or short!")

        kwargs = {'strategy_name': self.strategy_name,
                  'action_type': self.action_type,
                  'ticker': ticker,
                  'long_or_short': long_or_short,
                  'takeprofit': takeprofit,
                  'stoploss': stoploss,
                  'trailingstop': trailingstop}

        return SignalCancelTST(**kwargs)

    def cancel_pending(self, ticker: str, long_or_short: str,
                       below_price: float=None, above_price: float=None):

        if long_or_short not in ['long', 'short']:
            raise ValueError("long_or_short should be long or short!")

        kwargs = {'strategy_name': self.strategy_name,
                  'action_type': self.action_type,
                  'ticker': ticker,
                  'long_or_short': long_or_short,
                  'below_price': below_price,
                  'above_price': above_price
                  }

        return SignalCancelPending(**kwargs)


class TriggeredSignalGenerator(OnePyEnvBase):
    """为触发的挂单生成挂单触发信号"""
    @classmethod
    def _generate_bare_signal(cls, order) -> SignalByTrigger:
        kwargs = {'action_type': order.action_type,
                  'strategy_name': order.strategy_name,
                  'size': order.size,
                  'ticker': order.ticker,
                  'execute_price': order.target_price,
                  'first_cur_price': order.first_cur_price,
                  'mkt_id': order.mkt_id,
                  'order_type': order.order_type,
                  'parent_order': order}

        return SignalByTrigger(**kwargs)

    @classmethod
    def _generate_full_signal(cls, order) -> SignalByTrigger:
        kwargs = {'action_type': order.action_type,
                  'strategy_name': order.strategy_name,
                  'size': order.size,
                  'ticker': order.ticker,
                  'execute_price': order.target_price,
                  'price': None,
                  'price_pct': None,
                  'takeprofit': order.signal.takeprofit,
                  'takeprofit_pct': order.signal.takeprofit_pct,
                  'stoploss': order.signal.stoploss,
                  'stoploss_pct': order.signal.stoploss_pct,
                  'trailingstop': order.signal.trailingstop,
                  'trailingstop_pct': order.signal.trailingstop_pct,
                  'order_type': order.order_type}

        return SignalByTrigger(**kwargs)

    @classmethod
    def generate_triggered_signal(cls, order: PendingOrderBase) -> Optional[Signal]:
        if order.ticker not in cls.env.cur_suspended_tickers:

            if order.is_triggered:
                if order.is_with_mkt():
                    return cls._generate_bare_signal(order)

                return cls._generate_full_signal(order)
