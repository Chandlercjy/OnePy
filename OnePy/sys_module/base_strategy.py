
from OnePy.constants import ActionType
from OnePy.sys_module.components.signal_generator import SignalGenerator
from OnePy.sys_module.metabase_env import OnePyEnvBase


class StrategyBase(OnePyEnvBase):

    def __init__(self):
        self._signal_list = []
        self.env.strategies.update({self.__class__.__name__: self})

        self.buy = SignalGenerator(ActionType.Buy).func_1
        self.sell = SignalGenerator(ActionType.Sell).func_2
        self.short_sell = SignalGenerator(ActionType.Short_sell).func_1
        self.short_cover = SignalGenerator(ActionType.Short_cover).func_2

    @property
    def recorder(self):
        """便于在strategy中调用账户信息数据"""

        return self.env.recorder

    def handle_bar(self):
        """在这里写策略的主要逻辑"""
        raise NotImplementedError

    def run(self):
        self.handle_bar()
