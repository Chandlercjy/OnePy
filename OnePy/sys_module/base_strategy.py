
import abc

from OnePy.constants import ActionType
from OnePy.sys_module.base_recorder import RecorderBase
from OnePy.sys_module.components.signal_generator import SignalGenerator
from OnePy.sys_module.metabase_env import OnePyEnvBase


class StrategyBase(OnePyEnvBase, abc.ABC):

    def __init__(self) -> None:
        self.name = self.__class__.__name__
        self.env.strategies.update({self.name: self})

        self.buy = SignalGenerator(ActionType.Buy, self.name).buy_or_short
        self.sell = SignalGenerator(ActionType.Sell, self.name).sell_or_cover
        self.short = SignalGenerator(ActionType.Short, self.name).buy_or_short
        self.cover = SignalGenerator(ActionType.Cover, self.name).sell_or_cover
        self.cancel_pending = SignalGenerator(
            ActionType.Cancel, self.name).cancel_pending
        self.cancel_tst = SignalGenerator(
            ActionType.Cancel, self.name).cancel_tst
        self.params: dict = None

    @property
    def recorder(self) -> RecorderBase:
        """便于在strategy中调用账户信息数据"""

        return self.env.recorder

    @abc.abstractmethod
    def handle_bar(self):
        """在这里写策略的主要逻辑"""
        raise NotImplementedError

    def run(self):
        self.handle_bar()

    def cur_price(self, ticker: str) -> float:
        return self.env.feeds[ticker].cur_price

    def set_params(self, params: dict):
        """在这里设置参数，以便参数优化"""
        self.params.update(params)
