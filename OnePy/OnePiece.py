import logging
import sys

import arrow

from OnePy.builtin_module.optimizer import Optimizer
from OnePy.config import EVENT_LOOP
from OnePy.constants import EVENT
from OnePy.custom_module.forward_analysis import ForwardAnalysis
from OnePy.sys_module.components.exceptions import BacktestFinished
from OnePy.sys_module.components.logger import LoggerFactory
from OnePy.sys_module.components.market_maker import MarketMaker
from OnePy.sys_module.components.order_checker import PendingOrderChecker
from OnePy.sys_module.components.output import OutPut
from OnePy.sys_module.metabase_env import OnePyEnvBase
from OnePy.utils.awesome_func import show_process


class OnePiece(OnePyEnvBase):
    def __init__(self):
        # 内置模块
        self.market_maker: MarketMaker = None
        self.pending_order_checker: PendingOrderChecker = None
        self.event_loop: list = None

        # 其他模块
        self.optimizer = Optimizer()
        self.forward_analysis = ForwardAnalysis()

    def _pre_initialize_trading_system(self):
        self.event_loop = EVENT_LOOP
        self.market_maker = MarketMaker()
        self.pending_order_checker = PendingOrderChecker()

    def initialize_trading_system(self):  # 清空内存，便于参数优化
        self._pre_initialize_trading_system()
        self.env.initialize_env()
        self.market_maker.initialize()
        self.env.recorder.initialize()

    def sunny(self, summary: bool = True, show_process: bool = False):
        """主循环，OnePy的核心"""
        self.initialize_trading_system()

        while True:
            try:
                if self.env.event_engine.is_empty():
                    self.market_maker.update_market()
                    self.pending_order_checker.run()

                    if show_process:
                        self._show_process()
                else:
                    cur_event = self.env.event_engine.get()
                    self._run_event_loop(cur_event)

            except BacktestFinished:
                if summary:
                    print("\n")
                    self.output.summary()

                break

    def _run_event_loop(self, cur_event):
        for element in self.event_loop:
            if self._event_is_executed(cur_event, **element):
                break

    def _event_is_executed(
        self, cur_event, if_event: EVENT, then_event: EVENT, module_dict: dict
    ) -> bool:

        if cur_event is None:
            return True

        elif cur_event == if_event:
            [value.run() for value in module_dict.values()]
            self.env.event_engine.put(then_event)

            return True
        else:
            return False

    def _show_process(self):
        fromdate = arrow.get(self.env.fromdate)
        todate = arrow.get(self.env.todate)
        curdate = arrow.get(self.env.sys_date)
        total_days = (todate - fromdate).days
        finished_days = (curdate - fromdate).days
        show_process(finished_days, total_days)

    def set_date(self, fromdate: str, todate: str, frequency: str, instrument: str):
        """
        Instrument: A_shares, Forex
        Frequency:
                (S5, S10, S30, M1, M2, M4, M5) <- BAD Interval
                M10, M15, M30, H1, H2, H3, H4, H6, H8, H12
        """
        self.env.instrument = instrument
        self.env.fromdate = fromdate
        self.env.todate = todate
        self.env.sys_frequency = frequency

    def set_forex_live_trading(self, frequency: str):
        """
        Frequency:
                (S5, S10, S30, M1, M2, M4, M5) <- BAD Interval
                M10, M15, M30, H1, H2, H3, H4, H6, H8, H12
        """
        fromdate = arrow.utcnow().format("YYYY-MM-DD HH:mm:ss")
        self.set_date(fromdate, None, frequency, "Forex")
        self.env.sys_date = fromdate
        self.env.is_live_trading = True

    def show_today_signals(self):
        """
        能够显示当天的最新信号，但是会导致回测结果不准确。
        """
        self.env.is_show_today_signals = True

    @classmethod
    def show_log(cls, file=False, no_console=False):
        if file:
            LoggerFactory("OnePy")

        if no_console:
            logging.getLogger("OnePy").propagate = False
        logging.basicConfig(level=logging.INFO)

    @classmethod
    def set_recursion_limit(cls, limit: int = 2000):
        """
        突破递归次数限制，有时候信号太多会导致撮合引擎递归太多次而假死
        """
        sys.setrecursionlimit(limit)

    def save_original_signal(self):
        self.env.is_save_original = True

    @property
    def output(self) -> OutPut:
        return OutPut()
