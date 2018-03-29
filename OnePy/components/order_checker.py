from OnePy.components.order_generator import OrderGenerator
from OnePy.environment import Environment


class OrderChecker(object):
    env = Environment()

    def check_orders_pending(self):
        for order in self.env.orders_pending:
            self.send_signal(order)

    def check_orders_pending_with_mkt(self):
        for key in list(self.env.orders_pending_mkt_dict):
            for order in self.env.orders_pending_mkt_dict[key]:

                if self.send_signal(order):
                    # TODO: 有Flaw，当多个pending order同时触，只用了第一个
                    del self.env.orders_pending_mkt_dict[key]

                    break

    def send_signal(self, order):
        signal = order.get_triggered_signal()

        if signal:
            executer = OrderGenerator(signal)
            executer.generate_order()
            executer.submit_order_to_env()

            return True

    def run(self):
        self.check_orders_pending_with_mkt()
        self.check_orders_pending()
