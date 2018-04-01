import queue

from OnePy.components.market_maker import MarketMaker
from OnePy.components.order_checker import PendingOrderChecker
from OnePy.config import CUSTOM_MODULE, EVENT_LOOP, SYS_MODULE, SYS_MODEL
from OnePy.constants import EVENT
from OnePy.environment import Environment
from OnePy.event import Event
from OnePy.variables import GlobalVariables


class OnePiece(object):

    env = Environment()

    def __init__(self):
        self.market_maker = MarketMaker()
        self.order_checker = PendingOrderChecker()
        self.initialize_trading_system()
        self.cur_event = None

    def sunny(self):
        """主循环，OnePy的核心"""
        """TODO: 写test保证event的order正确"""

        while True:
            try:
                self.cur_event = self.env.event_bus.get()
            except queue.Empty:
                if self.market_maker.update_market():
                    self.order_checker.run()  # TODO:检查订单
                else:
                    # TODO:导出结果
                    print('complete')

                    break

            else:
                self.run_event_loop()

    def run_event_loop(self):
        for element in self.env.event_loop:
            if self.event_is_executed(**element):
                break

    def event_is_executed(self, if_event, then_event, module_dict):
        if self.cur_event.event_type == if_event:
            [value.run() for value in module_dict.values()]
            self.env.event_bus.put(Event(then_event)) if then_event else None

            return True

    def initialize_trading_system(self):
        self.env.refresh()

        for module in SYS_MODULE+CUSTOM_MODULE+SYS_MODEL:
            module.env = self.env

        self.env.event_loop = EVENT_LOOP
        self.market_maker.initialize_feeds()
        self.env.gvar = GlobalVariables()
        self.custom_initialize()

        if self.env.recorder:
            self.env.recorder.initialize()

    def custom_initialize(self, *funcs):
        for func in funcs:
            func()

    def show_setting(self, check_only=False):
        show_list = [self.env.readers,
                     self.env.cleaners,
                     self.env.strategies,
                     self.env.brokers,
                     self.env.risk_managers,
                     self.env.recorders]
        [show.print_data(check_only) for show in show_list]
