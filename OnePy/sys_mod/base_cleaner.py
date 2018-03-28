from OnePy.environment import Environment
from OnePy.variables import GlobalVariables


class CleanerBase(object):
    env = Environment()
    gvar = GlobalVariables()

    """Docstring for RiskManagerBase. """

    def __init__(self, name):
        self.env.cleaners.update({name: self})

    def run(self):
        pass
