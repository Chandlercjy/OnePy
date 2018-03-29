from OnePy.environment import Environment


class CleanerBase(object):
    env = Environment()

    """Docstring for RiskManagerBase. """

    def __init__(self, name):
        self.env.cleaners.update({name: self})

    def run(self):
        pass
