from itertools import count

from OnePy.constants import ActionType
from OnePy.sys_module.metabase_env import OnePyEnvBase
from OnePy.sys_module.models.orders.general_order import (CancelPendingOrder,
                                                          CancelTSTOrder,
                                                          LimitBuyOrder,
                                                          LimitCoverOrder,
                                                          LimitSellOrder,
                                                          LimitShortOrder,
                                                          MarketOrder,
                                                          StopBuyOrder,
                                                          StopCoverOrder,
                                                          StopSellOrder,
                                                          StopShortOrder,
                                                          TrailingStopCoverOrder,
                                                          TrailingStopSellOrder)
from OnePy.sys_module.models.signals import (Signal, SignalByTrigger,
                                             SignalCancelPending,
                                             SignalCancelTST)


class OrderGenerator(OnePyEnvBase):
    counter = count(1)
    buy_child_pair = [('stoploss', StopSellOrder),
                      ('trailingstop', TrailingStopSellOrder),
                      ('takeprofit', LimitSellOrder)]
    short_child_pair = [('stoploss', StopCoverOrder),
                        ('trailingstop', TrailingStopCoverOrder),
                        ('takeprofit', LimitCoverOrder)]

    def cur_price(self, ticker: str) -> float:
        return self.env.feeds[ticker].cur_price

    @staticmethod
    def is_buy(signal) -> bool:
        return True if signal.action_type == ActionType.Buy else False

    @staticmethod
    def is_sell(signal) -> bool:
        return True if signal.action_type == ActionType.Sell else False

    @staticmethod
    def is_short(signal) -> bool:
        return True if signal.action_type == ActionType.Short else False

    @staticmethod
    def is_shortcover(signal) -> bool:
        return True if signal.action_type == ActionType.Cover else False

    @staticmethod
    def is_absolute_mkt(signal) -> bool:
        return True if isinstance(signal, SignalByTrigger) else False

    @staticmethod
    def is_normal_mkt(signal) -> bool:
        return False if signal.price or signal.price_pct else True

    @staticmethod
    def _child_of_mkt(mkt_id, signal, order_class, key, orders_basket):
        if getattr(signal, key):
            orders_basket.append(order_class(signal, mkt_id, key))
        elif getattr(signal, f'{key}_pct'):
            orders_basket.append(order_class(signal, mkt_id, f'{key}_pct'))

    def _generate_mkt_order(self, signal: Signal):
        mkt_id = next(self.counter)
        mkt_order = MarketOrder(signal, mkt_id)

        return mkt_id, mkt_order

    def _generate_child_of_mkt(self, mkt_id: int, signal: Signal):
        orders_basket = []

        if self.is_buy(signal):
            for key, order in self.buy_child_pair:
                self._child_of_mkt(mkt_id, signal, order, key, orders_basket)

        elif self.is_short(signal):
            for key, order in self.short_child_pair:
                self._child_of_mkt(mkt_id, signal, order, key, orders_basket)

        return orders_basket

    def _generate_pending_order(self, signal):
        if signal.price > self.cur_price(signal.ticker):
            if self.is_buy(signal):
                order = StopBuyOrder(signal, None, 'price')
            elif self.is_shortcover(signal):
                order = StopCoverOrder(signal, None, 'price')
            elif self.is_sell(signal):
                order = LimitSellOrder(signal, None, 'price')
            elif self.is_short(signal):
                order = LimitShortOrder(signal, None, 'price')
        elif signal.price < self.cur_price(signal.ticker):
            if self.is_buy(signal):
                order = LimitBuyOrder(signal, None, 'price')
            elif self.is_shortcover(signal):
                order = LimitCoverOrder(signal, None, 'price')
            elif self.is_sell(signal):
                order = StopSellOrder(signal, None, 'price')
            elif self.is_short(signal):
                order = StopShortOrder(signal, None, 'price')
        else:
            raise Exception("Here shouldn't be raised")

        return order

    def submit_mkt_order_with_child(self, mkt_order: MarketOrder,
                                    orders_basket: list,
                                    orders_cur: list):
        orders_cur.append(mkt_order)

        if orders_basket != []:
            mkt_id = mkt_order.mkt_id
            self.env.orders_child_of_mkt_dict.update({mkt_id: orders_basket})

    def _process_mkt_signals(self, signals_list: list):
        for signal in signals_list:
            mkt_id, mkt_order = self._generate_mkt_order(signal)
            child_of_mkt = self._generate_child_of_mkt(mkt_id, signal)
            self.submit_mkt_order_with_child(
                mkt_order, child_of_mkt, self.env.orders_mkt_normal_cur)

    def _process_triggered_signals(self, signals_list: list):
        for signal in signals_list:
            mkt_id, mkt_order = self._generate_mkt_order(signal)
            child_of_mkt = self._generate_child_of_mkt(mkt_id, signal)
            self.submit_mkt_order_with_child(
                mkt_order, child_of_mkt, self.env.orders_mkt_absolute_cur)

    def _process_pending_signals(self, signals_list: list):
        for signal in signals_list:
            pending_order = self._generate_pending_order(signal)
            self.env.orders_pending.append(pending_order)

    def _process_cancel_signals(self):
        for signal in self.env.signals_cancel_cur:
            if isinstance(signal, SignalCancelTST):
                order = CancelTSTOrder(signal)
            elif isinstance(signal, SignalCancelPending):
                order = CancelPendingOrder(signal)
            self.env.orders_cancel_cur.append(order)

    def _clear_current_signals_memory(self):
        self.env.signals_normal_cur.clear()
        self.env.signals_pending_cur.clear()
        self.env.signals_trigger_cur.clear()
        self.env.signals_cancel_cur.clear()

    def run(self):
        self._process_mkt_signals(self.env.signals_normal_cur)
        self._process_triggered_signals(self.env.signals_trigger_cur)
        self._process_pending_signals(self.env.signals_pending_cur)
        self._process_cancel_signals()
        self._clear_current_signals_memory()
