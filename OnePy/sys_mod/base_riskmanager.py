from OnePy.environment import Environment
from OnePy.variables import GlobalVariables


class RiskManagerBase(object):

    env = Environment()
    gvar = GlobalVariables()

    def __init__(self):
        self.env.risk_managers.update({self.__class__.__name__: self})

    def run(self):
        pass
