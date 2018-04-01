from OnePy.buildin_mod.recorders.stock_recorder_series import (AvgPriceSeries,
                                                               CashSeries,
                                                               CommissionSeries,
                                                               HoldingPnlSeries,
                                                               MarginSeries,
                                                               MarketValueSeries,
                                                               PositionSeries,
                                                               RealizedPnlSeries)
from OnePy.constants import OrderType
from OnePy.sys_mod.base_recorder import RecorderBase


class StockRecorder(RecorderBase):

    """Docstring for StockRecorder. """

    def __init__(self):
        super().__init__()
        self.initial_cash = 100000
        self.per_comm = None
        self.per_comm_pct = None
        self.margin_rate = None

        self.position = None
        self.avg_price = None
        self.holding_pnl = None
        self.realized_pnl = None
        self.commission = None
        self.market_value = None
        self.margin = None

        self.cash = None
        self.frozen_cash = None
        self.balance = None

    def set_setting(self, initial_cash=100000,
                    comm=1, comm_pct=None, margin_rate=0.1):
        self.initial_cash = initial_cash
        self.per_comm = comm
        self.per_comm_pct = comm_pct
        self.margin_rate = margin_rate

    def initialize(self):
        self.set_setting()
        self.position = PositionSeries()
        self.avg_price = AvgPriceSeries()
        self.holding_pnl = HoldingPnlSeries()
        self.realized_pnl = RealizedPnlSeries()
        self.commission = CommissionSeries()
        self.market_value = MarketValueSeries()
        self.margin = MarginSeries()

        self.cash = CashSeries('cash', self.initial_cash)
        self.frozen_cash = CashSeries('frozen_cash', 0)
        self.balance = CashSeries('balance', self.initial_cash)

    @property
    def submitted_order(self):
        return self.env.orders_mkt_submitted

    def record_order(self):
        for order in self.submitted_order:
            # TODO:这里cur_price有争议，需要考虑成交价
            ticker = order.ticker

            long_or_short = self.for_long_or_short(order)

            last_position = self.position.latest(ticker, long_or_short)
            last_avg_price = self.avg_price.latest(ticker, long_or_short)
            last_commission = self.commission.latest(ticker, long_or_short)
            self.position.append(order, last_position, long_or_short)
            new_position = self.position.latest(ticker, long_or_short)

            self.avg_price.append(order,
                                  last_position,
                                  last_avg_price,
                                  new_position,
                                  long_or_short)
            new_avg_price = self.avg_price.latest(ticker, long_or_short)

            self.commission.append(order,
                                   last_commission,
                                   self.per_comm,
                                   self.per_comm_pct,
                                   long_or_short)

            self.realized_pnl.append(order,
                                     new_avg_price,
                                     last_avg_price,
                                     long_or_short)

    def update_balance_and_cash(self, trading_date):
        total_realized_pnl = self.realized_pnl.total_value()
        total_holding_pnl = self.holding_pnl.total_value()
        total_commission = self.commission.total_value()
        total_margin = self.margin.total_value()
        total_market_value = self.market_value.total_value()
        new_balance = self.initial_cash + total_realized_pnl + \
            total_holding_pnl - total_commission
        new_frozen_cash = total_margin+total_market_value  # 更新frozen_cash

        new_cash = self.initial_cash + total_realized_pnl - \
            total_commission - new_frozen_cash  # 更新cash

        self.balance.append(dict(date=trading_date, value=new_balance))
        self.frozen_cash.append(dict(date=trading_date, value=new_frozen_cash))
        self.cash.append(dict(date=trading_date, value=new_cash))

    def for_long_or_short(self, order):
        if order.order_type in [OrderType.Buy, OrderType.Sell]:
            return 'long'
        elif order.order_type in [OrderType.Short_sell, OrderType.Short_cover]:
            return 'short'

    def run(self):
        self.record_order()

    def update(self):
        """根据最新价格更新信息,
        需要更新cash，frozen cash, market_value, holding_pnl, balance"""
        self.market_value.update_barly()
        self.holding_pnl.update_barly()
        self.margin.update_barly()
        self.update_balance_and_cash(self.env.gvar.trading_date)
