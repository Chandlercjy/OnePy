from OnePy.builtin_module.backtest_forex import forex_recorder_series
from OnePy.builtin_module.backtest_forex.forex_log import ForexTradeLog
from OnePy.sys_module.base_recorder import RecorderBase
from OnePy.sys_module.components.match_engine import MatchEngine
from OnePy.builtin_module.backtest_forex.forex_bar import BarForex


class ForexRecorder(RecorderBase):

    def __init__(self):
        super().__init__()
        self.slippage = None

    def _update_cash(self, trading_date: str):
        total_margin = self.margin.total_value()
        new_balance = self.balance.latest()
        new_frozen_cash = total_margin  # 更新frozen_cash
        new_cash = new_balance - new_frozen_cash

        self.frozen_cash.append(
            {'date': trading_date, 'value': new_frozen_cash})
        self.cash.append({'date': trading_date, 'value': new_cash})

    def set_setting(self, initial_cash: int, margin_rate: float,
                    slippage: dict):
        self.initial_cash = initial_cash
        self.slippage = slippage
        self.margin_rate = margin_rate

    def settle_match_engine_and_series(self):
        self.match_engine = MatchEngine(ForexTradeLog)
        self.series = forex_recorder_series

    @property
    def bar_class(self):
        return BarForex
