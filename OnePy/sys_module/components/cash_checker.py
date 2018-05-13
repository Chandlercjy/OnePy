from OnePy.sys_module.metabase_env import OnePyEnvBase


class CashChecker(OnePyEnvBase):

    @classmethod
    def stock_checker(self, order):  # TODO：还要加上手续费,和保证金
        return order.size * order.execute_price
