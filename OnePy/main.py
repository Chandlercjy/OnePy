import logging
import queue

from OnePy.config import EVENT_LOOP
from OnePy.environment import Environment
from OnePy.event import Event
from OnePy.sys_module.components.exceptions import BacktestFinished
from OnePy.sys_module.components.logger import LoggerFactory
from OnePy.sys_module.components.market_maker import MarketMaker
from OnePy.sys_module.components.order_checker import PendingOrderChecker
from OnePy.sys_module.components.output import OutPut
from OnePy.sys_module.metabase_env import OnePyEnvBase


class OnePiece(object):

    env = Environment()

    def __init__(self):
        self.market_maker = MarketMaker()
        self.order_checker = PendingOrderChecker()
        self.cur_event = None
        self.env.logger = logging.getLogger("OnePy")

    def sunny(self, summary=True):
        """主循环，OnePy的核心"""
        self._initialize_trading_system()

        while True:
            try:
                self.cur_event = self.env.event_bus.get()
            except queue.Empty:
                try:
                    self.market_maker.update_market()
                    self.order_checker.run()
                except BacktestFinished:
                    self.output.summary() if summary else None

                    break
            else:
                self._run_event_loop()

    def _run_event_loop(self):
        for element in self.env.event_loop:
            if self._event_is_executed(**element):
                break

    def _event_is_executed(self, if_event, then_event, module_dict):
        if self.cur_event.event_type == if_event:
            [value.run() for value in module_dict.values()]
            self.env.event_bus.put(Event(then_event)) if then_event else None

            return True

    def _initialize_trading_system(self):
        self.env.refresh()
        OnePyEnvBase.env = self.env
        self.env.event_loop = EVENT_LOOP
        self.market_maker.initialize()

        if self.env.recorder:
            self.env.recorder.initialize()

    @property
    def output(self):
        return OutPut()

    def show_log(self, file=False):
        if file:
            LoggerFactory("OnePy").logger
        logging.basicConfig(level=logging.INFO)
