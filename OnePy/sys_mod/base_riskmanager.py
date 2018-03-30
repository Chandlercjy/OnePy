from OnePy.environment import Environment


class RiskManagerBase(object):

    env = Environment

    def __init__(self):
        self.env.risk_managers.update({self.__class__.__name__: self})

    def run(self):
        pass
