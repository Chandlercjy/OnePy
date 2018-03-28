from OnePy.environment import Environment
from OnePy.variables import GlobalVariables

class RecorderBase(object):
    env = Environment()
    gvar = GlobalVariables()

    def __init__(self):
        self.env.recorders.update({self.__class__.__name__: self})

    def run(self):
        pass


class StockRecorder(RecorderBase):

    """Docstring for StockRecorder. """

    def __init__(self):
        super().__init__(self)


class AbstractAccount(object):

    def __init__(self):
        pass

    def cash(self):
        pass

    def frozen_cash(self):
        pass

    def market_value(self):
        pass

    def transaction_cost(self):
        pass

    def positions(self):
        pass

    def get_state(self):
        pass

    def set_state(self):
        pass


class AbstractPosition(object):

    def __init__(self):
        pass

    def market_value(self):
        pass

    def transaction_cost(self):
        pass

    def positions(self):
        pass

    def get_state(self):
        pass

    def set_state(self):
        pass
