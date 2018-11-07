from dataclasses import dataclass, field

from OnePy.sys_module.models.base_log import TradeLogBase


@dataclass
class StockTradeLog(TradeLogBase):

    buy: float = None
    sell: float = None
    size: float = None

    def generate(self):
        sell_order_type = self._get_order_type(self.sell)
        buy_order_type = self._get_order_type(self.buy)
        per_comm_pct = self.env.recorder.per_comm_pct
        per_comm = self.env.recorder.per_comm

        self.entry_date = self.buy.trading_date
        self.entry_price = self.buy.first_cur_price
        self.entry_type = f'{buy_order_type} {self.buy.action_type.value}'
        self.exit_price = self.sell.first_cur_price
        self.exit_type = f'{sell_order_type} {self.sell.action_type.value}'
        self.pl_points = (self.sell.first_cur_price -
                          self.buy.first_cur_price)*self._earn_short()
        self.re_pnl = self.pl_points*self.size

        if per_comm_pct:
            self.commission = per_comm_pct*self.size*self.entry_price
        else:
            self.commission = per_comm*self.size/100

        if self.env.execute_on_close_or_next_open == 'open':
            self.exit_date = self.sell.signal.next_datetime
        elif self.env.execute_on_close_or_next_open == 'close':
            self.exit_date = self.sell.trading_date

        return self

    def settle_left_trade(self):
        cur_price = self.env.feeds[self.buy.ticker].execute_price
        buy_order_type = self._get_order_type(self.buy)
        per_comm_pct = self.env.recorder.per_comm_pct
        per_comm = self.env.recorder.per_comm

        self.entry_date = self.buy.trading_date
        self.entry_price = self.buy.first_cur_price
        self.entry_type = f'{buy_order_type} {self.buy.action_type.value}'
        self.exit_date = None
        self.exit_price = None
        self.exit_type = None
        self.pl_points = (
            cur_price - self.buy.first_cur_price)*self._earn_short()
        self.re_pnl = self.pl_points*self.size

        if per_comm_pct:
            self.commission = per_comm_pct*self.size*self.entry_price
        else:
            self.commission = per_comm*self.size/100

        return self
