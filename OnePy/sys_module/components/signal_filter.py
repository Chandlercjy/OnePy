from itertools import count

from OnePy.constants import ActionType
from OnePy.environment import Environment


class SignalFilter(object):
    """
    用来防止同时出现买单和卖单的无效信号。暂时放置
    """
    env = Environment
    counter = count(0)

    def __init__(self):
        pass

    @classmethod
    def filter_confilct_signals(self):
        """
        情况：
        1. buy & sell
        2. short_sell & short_cover
        3. buy & short_sell
        """
        self.filter_buy_and_sell()
        self.filter_short_sell_and_short_cover()
        self.filter_buy_and_short_sell()

    def filter_buy_and_sell(self):
        buy_list = []
        sell_list = []
        short_sell_list = []
        short_cover_list = []

        """
        首先要同个ticker，然后再看order_type，再相减得出最终
        """

        for signal in self.env.signals_normal_cur:
            if self.is_signal_mkt(signal, ActionType.Buy):
                buy_list.append(signal.size)
            elif self.is_signal_mkt(signal, ActionType.Sell):
                sell_list.append(signal.size)
            elif self.is_signal_mkt(signal, ActionType.Short_sell):
                short_sell_list.append(signal.size)
            elif self.is_signal_mkt(signal, ActionType.Short_cover):
                short_cover_list.append(signal.size)

        if sum(buy_list) > sum(sell_list):
            self.delete_all_sell()
        else:
            pass  # TODO

    def filter_short_sell_and_short_cover(self):
        pass

    def filter_buy_and_short_sell(self):
        pass

    def delete_all_buy(self):
        pass

    def is_signal_mkt(self, signal, order_type):
        if signal.order_type == order_type and signal.price == signal.price_pct:
            return True

        return False

    def append_list(self, signal, order_type, order_list):
        if self.is_signal_mkt(signal, order_type):
            order_list.append(signal.size)
