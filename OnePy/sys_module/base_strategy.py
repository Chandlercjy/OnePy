from abc import ABCMeta

from OnePy.constants import OrderType
from OnePy.environment import Environment
from OnePy.sys_module.components.signal_generator import SignalGenerator


class StrategyBase(metaclass=ABCMeta):

    env = Environment

    def __init__(self):
        self._signal_list = []

        self.env.strategies.update({self.__class__.__name__: self})

        # Order Function
        self.buy = SignalGenerator(OrderType.Buy).func_1
        self.sell = SignalGenerator(OrderType.Sell).func_2
        self.short_sell = SignalGenerator(OrderType.Short_sell).func_1
        self.short_cover = SignalGenerator(OrderType.Short_cover).func_2
        self.exit_all = SignalGenerator(
            OrderType.Exit_all).func_1  # TODO：多个信号出现如何处理冲突
        self.cancel_all = SignalGenerator(
            OrderType.Cancel_all).func_1  # TODO：多个信号出现如何处理冲突

    @property
    def gvar(self):
        return self.env.gvar

    def handle_bar(self):
        pass

    # def pre_trading(self):
        # """TODO: 完成逻辑 每天只在开盘前运行一次"""
        # pass

    # def after_trading(self):
        # """TODO: 完成逻辑 每天只在开盘后运行一次"""
        # pass

    def run(self):
        self.handle_bar()
