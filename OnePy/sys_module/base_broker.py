from OnePy.sys_module.components.cash_checker import CashChecker
from OnePy.sys_module.components.order_checker import SubmitOrderChecker
from OnePy.sys_module.components.order_generator import OrderGenerator
from OnePy.sys_module.metabase_env import OnePyEnvBase


class BrokerBase(OnePyEnvBase):

    def __init__(self):
        self.env.brokers.update({self.__class__.__name__: self})
        self._checker = None
        self._order_generator = OrderGenerator()

    def _clear_submited_order(self):
        self.env.orders_mkt_submitted = []

    def submit_order(self):
        pass

    def generate_order(self):
        self._order_generator.run()

    def run(self):
        self._clear_submited_order()
        self.generate_order()
        self.check_order()
        self.submit_order()

    def check_order(self):
        self._checker.run()


class StockBroker(BrokerBase):

    def __init__(self):
        super().__init__()
        self._checker = SubmitOrderChecker(CashChecker.stock_checker)
