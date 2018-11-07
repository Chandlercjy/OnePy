from dataclasses import dataclass

from OnePy.builtin_module.backtest_forex.calculate_func import dollar_per_pips
from OnePy.sys_module.models.base_log import TradeLogBase


@dataclass
class ForexTradeLog(TradeLogBase):

    buy: float = None
    sell: float = None
    size: float = None

    def generate(self):
        sell_order_type = self._get_order_type(self.sell)
        buy_order_type = self._get_order_type(self.buy)
        slippage = self.env.recorder.slippage

        self.entry_date = self.buy.trading_date
        self.entry_price = self.buy.first_cur_price
        self.entry_type = f'{buy_order_type} {self.buy.action_type.value}'
        self.exit_price = self.sell.first_cur_price
        self.exit_type = f'{sell_order_type} {self.sell.action_type.value}'
        self.pl_points = (self.sell.first_cur_price -
                          self.buy.first_cur_price)*self._earn_short()
        self.re_pnl = self.pl_points*self.size * \
            dollar_per_pips(self.ticker, self.exit_price)

        self.commission = (
            slippage[self.ticker]*self.size/1e5*dollar_per_pips(self.ticker, self.entry_price))

        if self.env.execute_on_close_or_next_open == 'open':
            self.exit_date = self.sell.signal.next_datetime
        elif self.env.execute_on_close_or_next_open == 'close':
            self.exit_date = self.sell.trading_date

        return self

    def settle_left_trade(self):
        cur_price = self.env.feeds[self.ticker].cur_price
        buy_order_type = self._get_order_type(self.buy)
        slippage = self.env.recorder.slippage

        self.entry_date = self.buy.trading_date
        self.entry_price = self.buy.first_cur_price
        self.entry_type = f'{buy_order_type} {self.buy.action_type.value}'
        self.exit_date = None
        self.exit_price = None
        self.exit_type = None
        self.pl_points = (
            cur_price - self.buy.first_cur_price)*self._earn_short()
        self.re_pnl = self.pl_points*self.size * \
            dollar_per_pips(self.ticker, cur_price)

        self.commission = (
            slippage[self.ticker]*self.size/1e5*dollar_per_pips(self.ticker, self.entry_price))

        return self
