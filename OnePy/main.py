import logging
import queue

from OnePy.core.base_broker import BrokerBase
from OnePy.core.base_cleaner import CleanerBase
from OnePy.core.base_order import SignalGenerator
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
                get = self.env.event_bus.get()
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
                if get.event_type == EVENT.MARKET_UPDATED:
                    execute_run_func(self.env.cleaner_dict)
                    self.put_event(EVENT.DATA_CLEANED)

                elif get.event_type == EVENT.DATA_CLEANED:
                    [strategy.run() for strategy in self.env.strategy_list]
                    self.env.event_bus.put(Event(EVENT.SIGNAL_GENERATED))

                elif get.event_type == EVENT.SIGNAL_GENERATED:
                    [risk_manager.run()
                     for risk_manager in self.env.risk_manager_list]
                    self.env.event_bus.put(Event(EVENT.SUBMIT_ORDER))

                elif get.event_type == EVENT.SUBMIT_ORDER:
                    [broker.run() for broker in self.env.broker_list]
                    self.env.event_bus.put(Event(EVENT.RECORD_RESULT))

                elif get.event_type == EVENT.RECORD_RESULT:
                    [recorder.run() for recorder in self.env.recorder_list]

    def put_event(self, event_type):
        self.env.event_bus.put(Event(event_type))

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
            SignalGenerator.env = self.env

        MarketMaker.gvar = \
            CleanerBase.gvar =\
            StrategyBase.gvar = \
            RiskManagerBase.gvar = \
            BrokerBase.gvar =\
            RecorderBase.gvar =\
            DataReaderBase.gvar = \
            SignalGenerator.gvar = self.gvar

    def load_data(self):
        for key, value in self.env.reader_dict.items():
            self.env.feed_dict.update({key: Bar(value)})
