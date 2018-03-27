import queue

from OnePy.config import CUSTOM_MOD, EVENT_LOOP, SYS_MOD
from OnePy.constants import EVENT
from OnePy.core.components import MarketMaker
from OnePy.environment import Environment
from OnePy.event import Event
from OnePy.utils.easy_func import execute_run_func
from OnePy.variables import GlobalVariables


class OnePiece(object):

    env = Environment()
    gvar = GlobalVariables()

    def __init__(self):
        self.market_maker = MarketMaker()
        self.initialize_trading_system()
        self.cur_event = None

    def sunny(self):
        """主循环，OnePy的核心"""
        """TODO: 写test保证event的order正确"""
        self.market_maker.trading_initialize()

        while True:
            try:
                self.cur_event = self.env.event_bus.get()
            except queue.Empty:
                if self.market_maker.update_market():
                    # TODO:更新日历
                    # TODO:检查订单
                    self.env.event_bus.put(Event(EVENT.MARKET_UPDATED))
                    pass
                else:
                    # TODO:导出结果
                    print('complete')

                    break

            else:

                for element in self.env.event_loop:
                    if self.event_is_executed(**element):
                        break

    def event_is_executed(self, if_event, then_event, module_dict):
        if self.cur_event.event_type == if_event:
            execute_run_func(module_dict)
            self.env.event_bus.put(Event(then_event)) if then_event else None

            return True

    def initialize_trading_system(self):
        for module in SYS_MOD+CUSTOM_MOD:
            module.env = self.env
            module.gvar = self.gvar

        self.env.event_loop = EVENT_LOOP

    def show_setting(self, show_name=False):
        show_list = [self.env.readers,
                     self.env.cleaners,
                     self.env.strategies,
                     self.env.brokers,
                     self.env.risk_managers,
                     self.env.recorders]
        [show.print_data(show_name) for show in show_list]
