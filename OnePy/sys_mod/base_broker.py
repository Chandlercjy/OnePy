from OnePy.components.order_generator import OrderGenerator
from OnePy.environment import Environment
from OnePy.variables import GlobalVariables


class BrokerBase(object):
    env = None  # type:Environment
    gvar = None  # type:GlobalVariables

    """Docstring for RiskManagerBase. """

    def __init__(self):
        self.env.brokers.update({self.__class__.__name__: self})

    def run(self):
        for signal in self.env.signals_current:
            a = OrderGenerator(signal)
            a.generate_order()
            a.submit_order_to_env()
        self.env.signals_current = []

        pass

    def get_portfolio(self):
        pass

    def submit_order(self):
        pass

    def cancle_order(self, order):
        pass

    def get_open_orders(self, order_book_id):
        pass
