
from OnePy.environment import Environment
from OnePy.variables import GlobalVariables


class BrokerBase(object):
    env = None  # type:Environment
    gvar = None  # type:GlobalVariables

    """Docstring for RiskManagerBase. """

    def __init__(self):
        self.env.brokers.update({self.__class__.__name__: self})

    def run(self):
        pass
