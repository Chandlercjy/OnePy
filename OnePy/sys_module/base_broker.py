from OnePy.environment import Environment
from OnePy.sys_module.components.cash_checker import CashChecker
from OnePy.sys_module.components.order_checker import SubmitOrderChecker
from OnePy.sys_module.components.order_generator import OrderGenerator


class BrokerBase(object):
    env = Environment

    """Docstring for RiskManagerBase. """

    def __init__(self):
        self.env.brokers.update({self.__class__.__name__: self})
        self.checker = SubmitOrderChecker(CashChecker.stock_checker)
        self.order_generator = OrderGenerator()

    def clear_submited_order(self):
        self.env.orders_mkt_submitted = []

    def submit_order(self):
        self.checker.run()

    def generate_order(self):
        self.order_generator.run()

    def cancel_order(self, order):
        pass

    def get_open_orders(self, order_book_id):
        pass

    def get_portfolio(self):
        pass

    def run(self):
        self.clear_submited_order()
        self.generate_order()
        self.submit_order()
