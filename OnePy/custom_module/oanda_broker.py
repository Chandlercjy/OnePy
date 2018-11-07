from oandakey import access_token, accountID
from OnePy.builtin_module.backtest_forex.forex_broker import ForexBroker
from OnePy.constants import ActionType, OrderType
from OnePy.custom_module.api.oanda_api import OandaAPI
from OnePy.sys_module.components.order_checker import SubmitOrderChecker


class OandaBroker(ForexBroker):
    """自动生成挂单，所以要把系统的挂单序列清空"""

    def __init__(self):
        super().__init__()
        self.oanda = OandaAPI(accountID, access_token)

    def _submit_order(self):

        for mkt_order in self.env.orders_mkt_submitted_cur:
            self.send_mkt_order_with_pending(mkt_order)

        # 提交挂单 可以异步提交

        for pending in self.env.orders_pending:
            self.send_pending_order_with_pending(pending)

        self.clear_pending()  # 清除挂单

    def get_order_info(self, pending_list):
        order_info = {}

        for order in pending_list:
            if 'takeprofit' in order.trigger_key:
                order_info['takeprofit'] = order.target_price
            elif 'stoploss' in order.trigger_key:
                order_info['stoploss'] = order.target_price
            elif 'trailingstop' in order.trigger_key:
                cur_price = self.env.feeds[order.ticker].cur_price
                order_info['trailingstop'] = order.difference

        return order_info

    def is_mkt_only(self, order):
        if order.mkt_id in self.env.orders_child_of_mkt_dict:
            return False

        return True

    def send_to_broker(self, mkt, order_info=None):
        if order_info:
            self.oanda.OrderCreate_mkt(**order_info)

            return
        self.oanda.OrderCreate_mkt(mkt.ticker, mkt.size*self.direction(mkt))

    def send_mkt_order_with_pending(self, mkt_order):

        if self.is_mkt_only(mkt_order):
            self.send_to_broker(mkt_order)
        else:
            pending_list = self.env.orders_child_of_mkt_dict[mkt_order.mkt_id]
            order_info = self.get_order_info(pending_list)
            order_info['ticker'] = mkt_order.ticker
            order_info['size'] = mkt_order.size*self.direction(mkt_order)
            self.send_to_broker(mkt_order, order_info)

    def send_pending_order_with_pending(self, order):
        params = self.target_price_for_live(order)
        params.update(dict(
            ticker=order.ticker,
            size=order.size*self.direction(order),
            price=order.target_price))

        if order.order_type == OrderType.Limit:
            params.update(dict(requesttype='LimitOrder'))

        elif order.order_type == OrderType.Stop:
            params.update(dict(requesttype='StopOrder'))
        self.oanda.OrderCreate_pending(**params)

    def direction(self, order):
        if order.action_type in [ActionType.Short, ActionType.Sell]:
            return -1

        return 1

    def clear_pending(self):
        self.env.orders_pending = []
        self.env.orders_child_of_mkt_dict = {}

    def run(self):
        self._clear_submited_order()
        self._generate_order()
        self._check_order()
        self._submit_order()

    def target_price_for_live(self, order):

        def below_price(diff):
            return order.signal.price-diff

        def above_price(diff):
            return order.signal.price+diff

        def target_price():
            return order.signal.price

        params = {}
        division = dollar_per_pips(order.ticker, order.first_cur_price)

        if order.signal.action_type == ActionType.Buy:

            if order.signal.get('stoploss'):
                money = order.signal.get('stoploss')
                diff = money/order.signal.size/division
                result = below_price(diff)
                params.update(dict(stoploss=result))

            if order.signal.get('takeprofit'):
                money = order.signal.get('takeprofit')
                diff = money/order.signal.size/division
                result = above_price(diff)
                params.update(dict(takeprofit=result))

            if order.signal.get('trailingstop'):
                money = order.signal.get('trailingstop')
                diff = money/order.signal.size/division
                params.update(dict(trailingstop=diff))

            if order.signal.get('stoploss_pct'):
                pct = order.signal.get('stoploss_pct')
                diff = pct*target_price()/division
                result = below_price(diff)
                params.update(dict(stoploss=result))

            if order.signal.get('takeprofit_pct'):
                pct = order.signal.get('takeprofit_pct')
                diff = pct*target_price()/division
                result = above_price(diff)
                params.update(dict(takeprofit=result))

            if order.signal.get('trailingstop_pct'):
                pct = order.signal.get('trailingstop_pct')
                diff = pct*target_price()/division
                params.update(dict(trailingstop=diff))

        elif order.signal.action_type == ActionType.Short:

            if order.signal.get('stoploss'):
                money = order.signal.get('stoploss')
                diff = money/order.signal.size/division
                result = above_price(diff)
                params.update(dict(stoploss=result))

            if order.signal.get('takeprofit'):
                money = order.signal.get('takeprofit')
                diff = money/order.signal.size/division
                result = below_price(diff)
                params.update(dict(takeprofit=result))

            if order.signal.get('trailingstop'):
                money = order.signal.get('trailingstop')
                diff = money/order.signal.size/division
                params.update(dict(trailingstop=diff))

            if order.signal.get('stoploss_pct'):
                pct = order.signal.get('stoploss_pct')
                diff = pct*target_price()/division
                result = above_price(diff)
                params.update(dict(stoploss=result))

            if order.signal.get('takeprofit_pct'):
                pct = order.signal.get('takeprofit_pct')
                diff = pct*target_price()/division
                result = below_price(diff)
                params.update(dict(takeprofit=result))

            if order.signal.get('trailingstop_pct'):
                pct = order.signal.get('trailingstop_pct')
                diff = pct*target_price()/division
                params.update(dict(trailingstop=diff))

        return params
