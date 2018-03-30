from OnePy.environment import Environment
from OnePy.sys_mod.base_recorder import RecorderBase
from OnePy.sys_model.record_series import RecordFactory


class StockRecorder(RecorderBase):

    """Docstring for StockRecorder. """

    def __init__(self):
        super().__init__()

        self.initial_cash = 100000

        self.cash = RecordFactory.long_only('cash')
        self.frozen_cash = RecordFactory.long_only('frozen_cash')
        self.position = RecordFactory.long_and_short('position')
        self.avg_price = RecordFactory.long_and_short('avg_price')
        self.holding_pnl = RecordFactory.long_and_short('holding_pnl')
        self.realized_pnl = RecordFactory.long_and_short('realized_pnl')
        self.daily_pnl = RecordFactory.long_and_short('daily_pnl')
        self.transaction_cost = RecordFactory.long_and_short(
            'transaction_cost')
        self.balance = RecordFactory.long_only('balance')

        # self.margin = RecordSeries('margin')
    @property
    def submitted_order(self):
        return self.env.orders_mkt_submitted

    def update_position(self):
        for order in self.submitted_order:
            if for_long(order):
                new = self.position[f'{order.ticker}_long'].latest + order.size
                self.position[f'{order.ticker}_long'].append(
                    {order.mkt_id: new})

    def for_long(self, order):
        if order.order_type in [OrderType.Buy, OrderType.Sell]:
            return True

    def for_short(self, order):
        if order.order_type in [OrderType.Short_sell, OrderType.Short_cover]:
            return True

    def run(self):
        pass

    def update(self):
        """根据最新价格更新信息"""
        pass

    def update_cash(self):
        pass


class StockAccount(object):

    def __init__(self):
        pass

    def cash(self):
        pass

    def frozen_cash(self):
        pass

    def market_value(self):
        pass

    def transaction_cost(self):
        pass

    def positions(self):
        pass

    def get_state(self):
        pass

    def set_state(self):
        pass


class StockPosition(object):
    env = Environment

    def __init__(self):
        self.env.position = RecordSeries('position')

    def market_value(self):
        pass

    def transaction_cost(self):
        pass

    @property
    def latest(self):
        return self.env.position.latest

    def get_state(self):
        pass

    def set_state(self):
        pass


class Portfolio(object):
    def __init__(self):
        self.initial_cash
        self.cash = None
        self.frozen_cash = None
        self.total_returns = None
        self.daily_returns = None
        self.daily_pnl = None
        self.market_value = None
        self.total_value = None
        self.transaction_cost = None
        self.pnl = None
        self.start_date = None
        self.annulized_return = None
        self.positions = None
