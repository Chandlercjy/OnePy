from dataclasses import dataclass, field

from OnePy.constants import ActionType
from OnePy.sys_module.metabase_env import OnePyEnvBase


@dataclass
class TradeLogBase(OnePyEnvBase):

    buy: float = None
    sell: float = None
    size: float = None

    ticker: str = field(init=False)

    entry_date: str = field(init=False)
    exit_date: str = field(init=False)

    entry_price: float = field(init=False)
    exit_price: float = field(init=False)
    pl_points: float = field(init=False)
    re_pnl: float = field(init=False)

    # commission: float = field(init=False)
    # cumulative_total: float = field(init=False)

    def generate(self):
        raise NotImplementedError

    def _earn_short(self):
        return -1 if self.buy.action_type == ActionType.Short_sell else 1

    def _get_order_type(self, order):
        if order.signal.order_type:
            return order.signal.order_type.value
        else:
            return order.order_type.value

    def settle_left_trade(self):
        raise NotImplementedError
