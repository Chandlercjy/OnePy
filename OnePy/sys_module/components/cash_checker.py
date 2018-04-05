from OnePy.environment import Environment


class CashChecker(object):
    env = Environment

    @classmethod
    def stock_checker(self, order):  # TODO：还要加上手续费
        return order.size * order.execute_price
