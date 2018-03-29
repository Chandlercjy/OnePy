from abc import ABCMeta

from OnePy.components.signal_generator import SignalGenerator
from OnePy.constants import OrderType
from OnePy.environment import Environment


class StrategyBase(metaclass=ABCMeta):

    env = Environment()

    def __init__(self, marketevent):
        self._signal_list = []
        self.g = self.env.gvar

        self.env.strategies.update({self.__class__.__name__: self})

        # Order Function
        self.buy = SignalGenerator(OrderType.BUY).func_1
        self.sell = SignalGenerator(OrderType.SELL).func_2
        self.short_sell = SignalGenerator(OrderType.SHORT_SELL).func_1
        self.short_cover = SignalGenerator(OrderType.SHORT_COVER).func_2
        self.exit_all = SignalGenerator(
            OrderType.EXIT_ALL).func_1  # TODO：多个信号出现如何处理冲突
        self.cancel_all = SignalGenerator(
            OrderType.CANCEL_ALL).func_1  # TODO：多个信号出现如何处理冲突

    def prepare_for_trading(self):
        """TODO: 计算好indicator的值"""
        pass

    def pre_trading(self):
        """每天只在开盘前运行一次"""
        pass

    def start_trading(self):
        pass

    def after_trading(self):
        """每天只在开盘后运行一次"""
        pass

    def run(self):
        self.prepare_for_trading()
        self.pre_trading()
        self.handle_bar()
        self.after_trader()
