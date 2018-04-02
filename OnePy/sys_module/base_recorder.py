from OnePy.environment import Environment
from OnePy.sys_model.base_series import BarSeries


class RecorderBase(object):
    env = Environment

    def __init__(self):
        self.env.recorders.update({self.__class__.__name__: self})
        self.env.recorder = self
        self.ohlc = BarSeries()

    def run(self):
        pass

    def update(self):
        """根据最新价格更新账户信息"""
        pass
