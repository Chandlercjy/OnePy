from OnePy.builtin_module.backtest_stock import stock_recorder_series
from OnePy.builtin_module.backtest_stock.stock_bar import BarAshares
from OnePy.builtin_module.backtest_stock.stock_log import StockTradeLog
from OnePy.sys_module.base_recorder import RecorderBase
from OnePy.sys_module.components.match_engine import MatchEngine


class StockRecorder(RecorderBase):

    def __init__(self):
        super().__init__()

    def _update_cash(self, trading_date: str):
        total_margin = self.margin.total_value()
        total_market_value = self.market_value.total_value()
        new_balance = self.balance.latest()
        new_frozen_cash = total_margin+total_market_value  # 更新frozen_cash
        new_cash = new_balance - new_frozen_cash  # 更新cash

        self.frozen_cash.append(
            {'date': trading_date, 'value': new_frozen_cash})
        self.cash.append({'date': trading_date, 'value': new_cash})

    def set_setting(self, initial_cash=100000,
                    comm=1, comm_pct=None, margin_rate=0.1):
        self.initial_cash = initial_cash
        self.per_comm = comm
        self.per_comm_pct = comm_pct
        self.margin_rate = margin_rate

    def settle_match_engine_and_series(self):
        self.match_engine = MatchEngine(StockTradeLog)
        self.series = stock_recorder_series

    @property
    def bar_class(self):
        return BarAshares
