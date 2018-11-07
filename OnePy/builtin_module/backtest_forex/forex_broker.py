from OnePy.builtin_module.backtest_forex.calculate_func import (dollar_per_pips,
                                                                market_value_multiplayer)
from OnePy.sys_module.base_broker import BrokerBase
from OnePy.sys_module.models.orders.general_order import MarketOrder


class ForexBroker(BrokerBase):

    @classmethod
    def _required_cash_func(cls, order: MarketOrder) -> float:
        ticker = order.ticker
        size = order.size
        execute_price = order.execute_price
        margin_rate = cls.env.recorder.margin_rate
        mult = market_value_multiplayer(order.ticker, execute_price)

        slippage = cls.env.recorder.slippage[ticker]
        commission = (slippage*size/1e5 *
                      dollar_per_pips(ticker, execute_price))

        return size*execute_price*margin_rate*mult+commission
