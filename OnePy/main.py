import logging
import queue

from OnePy.core.base_broker import BrokerBase
from OnePy.core.base_cleaner import CleanerBase
from OnePy.core.base_order import SignalGenerator, SignalInfo
from OnePy.core.base_reader import DataReaderBase, MarketMaker
from OnePy.core.base_recorder import RecorderBase
from OnePy.core.base_riskmanager import RiskManagerBase
from OnePy.core.base_strategy import StrategyBase
from OnePy.environment import Environment
from OnePy.event import EVENT, Event
from OnePy.model.bar import Bar
from OnePy.utils.easy_func import execute_run_func
from OnePy.variables import GlobalVariables


class OnePiece(object):

    env = Environment()
    gvar = GlobalVariables()

    def __init__(self):
        self.market_maker = MarketMaker()
        self.set_environment_and_global_var()

    def sunny(self):
        """主循环，OnePy的核心"""
        """TODO: 写test保证event的order正确"""
        self.load_data()

        while True:
            try:
                self.get = self.env.event_bus.get()
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
        if self.get.event_type == if_event:
            execute_run_func(module_dict)
            self.env.event_bus.put(Event(then_event)) if then_event else None

            return True

    def set_environment_and_global_var(self):
        Bar.env = \
            GlobalVariables.env = \
            MarketMaker.env = \
            CleanerBase.env =\
            StrategyBase.env = \
            RiskManagerBase.env = \
            BrokerBase.env =\
            RecorderBase.env =\
            DataReaderBase.env = \
            SignalInfo.env =\
            SignalGenerator.env = self.env

        MarketMaker.gvar = \
            CleanerBase.gvar =\
            StrategyBase.gvar = \
            RiskManagerBase.gvar = \
            BrokerBase.gvar =\
            RecorderBase.gvar =\
            DataReaderBase.gvar = \
            SignalGenerator.gvar =\
            SignalInfo.gvar = self.gvar

    def load_data(self):
        for key, value in self.env.readers.items():
            self.env.feeds.update({key: Bar(value)})
