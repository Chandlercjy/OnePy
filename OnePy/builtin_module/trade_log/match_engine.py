from collections import defaultdict, deque

import pandas as pd

from OnePy.constants import ActionType
from OnePy.sys_module.metabase_env import OnePyEnvBase


class MatchEngine(OnePyEnvBase):

    def __init__(self, trade_log):
        self.long_log_pure = defaultdict(deque)
        self.long_log_with_trigger = defaultdict(deque)
        self.short_log_pure = defaultdict(deque)
        self.short_log_with_trigger = defaultdict(deque)
        self.finished_log = []
        self.trade_log = trade_log
        self.left_trade_settled = False

    def _append_finished(self, buy_order, sell_order, size):
        log = self.trade_log(buy_order, sell_order, size).generate()
        self.finished_log.append(log)

    def _search_father(self, order, log_with_trigger):
        for i in log_with_trigger:
            if i.mkt_id == order.father_mkt_id:
                self._append_finished(i, order, order.size)
                log_with_trigger.remove(i)

                break

    def _del_in_mkt_dict(self, mkt_id):
        if mkt_id in self.env.orders_pending_mkt_dict:
            del self.env.orders_pending_mkt_dict[mkt_id]

    def _pair_one_by_one(self, order_list, sell_size, order, counteract=False):
        buy_order = order_list.popleft()
        buy_size = buy_order.track_size
        diff = buy_order.track_size = buy_size - sell_size

        if diff > 0:
            self._append_finished(buy_order, order, sell_size)
            order_list.appendleft(buy_order)

            if counteract:  # 修改dict中订单size
                for order in self.env.orders_pending_mkt_dict[buy_order.mkt_id]:
                    order.size = buy_order.track_size

        elif diff == 0:
            self._append_finished(buy_order, order, sell_size)

            if counteract:
                self._del_in_mkt_dict(buy_order.mkt_id)

        else:
            self._append_finished(buy_order, order, buy_size)
            sell_size -= buy_size

            if counteract:
                self._del_in_mkt_dict(buy_order.mkt_id)
            self._pair_one_by_one(order_list, sell_size, order)

    def _pair_order(self, long_or_short, order):  # order should be sell or short cover
        if long_or_short == 'long':
            log_pure = self.long_log_pure[order.ticker]
            log_with_trigger = self.long_log_with_trigger[order.ticker]
        elif long_or_short == 'short':
            log_pure = self.short_log_pure[order.ticker]
            log_with_trigger = self.short_log_with_trigger[order.ticker]

        sell_size = order.size

        if order.father_mkt_id:
            self._search_father(order, log_with_trigger)

        else:

            try:
                self._pair_one_by_one(log_pure, sell_size, order)
            except IndexError:
                self._pair_one_by_one(log_with_trigger, sell_size, order, True)

    def match_order(self, order):
        if order.action_type == ActionType.Buy:
            order.track_size = order.size

            if order.is_pure():
                self.long_log_pure[order.ticker].append(order)
            else:
                self.long_log_with_trigger[order.ticker].append(order)
        elif order.action_type == ActionType.Short_sell:
            order.track_size = order.size

            if order.is_pure():
                self.short_log_pure[order.ticker].append(order)
            else:
                self.short_log_with_trigger[order.ticker].append(order)

        elif order.action_type == ActionType.Sell:
            self._pair_order('long', order)

        elif order.action_type == ActionType.Short_cover:
            self._pair_order('short', order)

    def append_left_trade_to_log(self):

        def settle_left_trade(unfinished_order):
            log = self.trade_log(
                unfinished_order, None, unfinished_order.track_size).settle_left_trade()
            self.finished_log.append(log)

        for ticker in self.env.tickers:

            for order in self.long_log_pure[ticker]:
                settle_left_trade(order)

            for order in self.long_log_with_trigger[ticker]:
                settle_left_trade(order)

            for order in self.short_log_pure[ticker]:
                settle_left_trade(order)

            for order in self.short_log_with_trigger[ticker]:
                settle_left_trade(order)

    def generate_trade_log(self):
        if self.left_trade_settled is False:
            self.append_left_trade_to_log()
            self.left_trade_settled = True

        log_dict = defaultdict(list)

        for log in self.finished_log:
            log_dict['ticker'].append(log.ticker)
            log_dict['entry_date'].append(log.entry_date)
            log_dict['entry_price'].append(log.entry_price)
            log_dict['entry_type'].append(log.entry_type)
            log_dict['size'].append(log.size)
            log_dict['exit_date'].append(log.exit_date)
            log_dict['exit_price'].append(log.exit_price)
            log_dict['exit_type'].append(log.exit_type)
            log_dict['pl_points'].append(log.pl_points)
            log_dict['re_pnl'].append(log.re_pnl)

        return pd.DataFrame(log_dict)
