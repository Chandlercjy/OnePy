from dataclasses import dataclass, field

from OnePy.builtin_module.trade_log.base_log import TradeLogBase
from OnePy.constants import ActionType


@dataclass
class StockTradeLog(TradeLogBase):
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

    def generate(self):
        sell_order_type = self._get_order_type(self.sell)
        buy_order_type = self._get_order_type(self.buy)

        self.ticker = self.buy.ticker
        self.entry_date = self.buy.trading_date
        self.entry_price = self.buy.first_cur_price
        self.entry_type = f'{buy_order_type} {self.buy.action_type.value}'
        self.exit_date = self.sell.trading_date
        self.exit_price = self.sell.first_cur_price
        self.exit_type = f'{sell_order_type} {self.sell.action_type.value}'
        self.pl_points = (self.sell.first_cur_price -
                          self.buy.first_cur_price)*self._earn_short()
        self.re_pnl = self.pl_points*self.size

        return self

    def settle_left_trade(self):
        ticker = self.buy.ticker
        cur_price = self.env.feeds[ticker].cur_price
        buy_order_type = self._get_order_type(self.buy)

        self.ticker = ticker
        self.entry_date = self.buy.trading_date
        self.entry_price = self.buy.first_cur_price
        self.entry_type = f'{buy_order_type} {self.buy.action_type.value}'
        self.exit_date = None
        self.exit_price = None
        self.exit_type = None
        self.pl_points = (
            cur_price - self.buy.execute_price)*self._earn_short()
        self.re_pnl = self.pl_points*self.size

        return self
