from OnePy.builtin_module.recorders.stock_recorder_series import (AvgPriceSeries,
                                                                  CommissionSeries,
                                                                  HoldingPnlSeries,
                                                                  MarginSeries,
                                                                  MarketValueSeries,
                                                                  PositionSeries,
                                                                  RealizedPnlSeries)
from OnePy.builtin_module.trade_log.stock_log import StockTradeLog
from OnePy.constants import ActionType
from OnePy.sys_module.base_recorder import RecorderBase
from OnePy.sys_module.models.base_series import CashSeries


class StockRecorder(RecorderBase):

    def __init__(self):
        super().__init__(StockTradeLog)

    def _for_long_or_short(self, order):
        if order.action_type in [ActionType.Buy, ActionType.Sell]:
            return 'long'
        elif order.action_type in [ActionType.Short_sell, ActionType.Short_cover]:
            return 'short'

    def _record_order(self):
        for order in self.env.orders_mkt_submitted:
            ticker = order.ticker
            long_or_short = self._for_long_or_short(order)

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
                                     last_avg_price,
                                     new_avg_price,
                                     long_or_short)
            self.match_engine.match_order(order)
            self.update(order_executed=True)

    def _update_balance_and_cash(self, trading_date):
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

    def set_setting(self, initial_cash=100000,
                    comm=1, comm_pct=None, margin_rate=0.1):
        self.initial_cash = initial_cash
        self.per_comm = comm
        self.per_comm_pct = comm_pct
        self.margin_rate = margin_rate

    def initialize(self):
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

    def update(self, order_executed=False):
        """根据最新价格更新信息,
        需要更新cash，frozen cash, market_value, holding_pnl, balance"""
        self.market_value.update_barly(order_executed)
        self.holding_pnl.update_barly(order_executed)
        self.margin.update_barly(order_executed)
        self._update_balance_and_cash(self.env.trading_datetime)

    def run(self):
        self._record_order()
