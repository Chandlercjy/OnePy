from abc import ABCMeta
from enum import Enum

from OnePy.core.base_order import OrderType, SignalGenerator
from OnePy.environment import Environment


class StrategyBase(metaclass=ABCMeta):

    env = None
    gvar = None

    def __init__(self, marketevent):
        self._signal_list = []
        self.g = self.gvar
        # self.context = self.g.context

        self.env.strategy_list.append(self)

        # Order Function
        self.buy = SignalGenerator(OrderType.BUY).order_func
        self.sell = SignalGenerator(OrderType.SELL).order_func
        self.short_sell = SignalGenerator(OrderType.SHORT_SELL).order_func
        self.short_cover = SignalGenerator(OrderType.SHORT_COVER).order_func
        self.exit_all = SignalGenerator(
            OrderType.EXIT_ALL).order_func  # TODO：多个信号出现如何处理冲突
        self.cancel_all = SignalGenerator(
            OrderType.CANCEL_ALL).order_func  # TODO：多个信号出现如何处理冲突

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
