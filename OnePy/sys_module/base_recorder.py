from OnePy.environment import Environment


class RecorderBase(object):
    env = Environment

    def __init__(self):
        self.env.recorders.update({self.__class__.__name__: self})
        self.env.recorder = self

    def run(self):
        pass

    def update(self):
        """根据最新价格更新账户信息"""
        pass
