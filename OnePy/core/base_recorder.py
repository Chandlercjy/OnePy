
from OnePy.environment import Environment


class RecorderBase(object):
    env = None
    gvar = None

    """Docstring for RiskManagerBase. """

    def __init__(self):
        self.env.recorders.update({self.__class__.__name__: self})

    def run(self):
        pass
