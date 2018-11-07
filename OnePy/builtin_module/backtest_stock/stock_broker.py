from OnePy.builtin_module.backtest_stock.stock_limit_filter_risk_manager import \
    StockLimitFilterRiskManager
from OnePy.sys_module.base_broker import BrokerBase
from OnePy.sys_module.models.orders.general_order import MarketOrder


class StockBroker(BrokerBase):

    def __init__(self):
        super().__init__()
        StockLimitFilterRiskManager()

    @classmethod
    def _required_cash_func(cls, order: MarketOrder) -> float:
        # TODO：还要加上手续费,和保证金

        return order.size * order.execute_price
