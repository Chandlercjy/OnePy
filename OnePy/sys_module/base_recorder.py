import abc

from OnePy.sys_module.components.match_engine import MatchEngine
from OnePy.sys_module.metabase_env import OnePyEnvBase
from OnePy.sys_module.models.base_log import TradeLogBase
from OnePy.sys_module.models.base_series import (AvgPriceSeries,
                                                 CommissionSeriesBase,
                                                 HoldingPnlSeriesBase,
                                                 MarginSeriesBase,
                                                 MarketValueSeriesBase,
                                                 MoneySeries, PositionSeries,
                                                 RealizedPnlSeriesBase)


class RecorderBase(OnePyEnvBase, abc.ABC):

    def __init__(self):
        self.env.recorders.update({self.__class__.__name__: self})
        self.env.recorder = self

        self.initial_cash: int = 100000
        self.per_comm: int = 1
        self.per_comm_pct: float = None
        self.margin_rate: float = 0.1

        self.holding_pnl: HoldingPnlSeriesBase = None
        self.realized_pnl: RealizedPnlSeriesBase = None
        self.commission: CommissionSeriesBase = None
        self.market_value: MarketValueSeriesBase = None
        self.margin: MarginSeriesBase = None

        self.position: PositionSeries = None
        self.avg_price: AvgPriceSeries = None
        self.cash: MoneySeries = None
        self.frozen_cash: MoneySeries = None
        self.balance: MoneySeries = None

        self.match_engine: TradeLogBase = None
        self.series = None  # 含有series的包

    def initialize(self):
        """根据最新价格更新账户信息"""

        self.settle_match_engine_and_series()
        self.holding_pnl = self.series.HoldingPnlSeries()
        self.realized_pnl = self.series.RealizedPnlSeries()
        self.commission = self.series.CommissionSeries()
        self.market_value = self.series.MarketValueSeries()
        self.margin = self.series.MarginSeries()

        self.position = PositionSeries()
        self.avg_price = AvgPriceSeries()
        self.cash = MoneySeries('cash', self.initial_cash)
        self.frozen_cash = MoneySeries('frozen_cash', 0)
        self.balance = MoneySeries('balance', self.initial_cash)

    def update(self, order_executed: bool = False):
        """根据最新价格更新信息"""
        self.market_value.update_barly(order_executed)
        self.holding_pnl.update_barly(order_executed)
        self.margin.update_barly()
        self._update_balance(self.env.sys_date)
        self._update_cash(self.env.sys_date)

    def _update_balance(self, trading_date):
        total_realized_pnl = self.realized_pnl.total_value()
        total_holding_pnl = self.holding_pnl.total_value()
        total_commission = self.commission.total_value()
        new_balance = self.initial_cash + total_realized_pnl + \
            total_holding_pnl - total_commission

        self.balance.append({'date': trading_date, 'value': new_balance})

    def _record_order(self):
        """记录成交的账单信息，更新账户信息"""

        for order in self.env.orders_mkt_submitted_cur:
            ticker = order.ticker
            long_or_short = order.long_or_short
            size = order.size
            execute_price = order.execute_price
            action_type = order.action_type

            last_position = self.position.latest(ticker, long_or_short)
            last_avg_price = self.avg_price.latest(ticker, long_or_short)
            last_commission = self.commission.latest(ticker, long_or_short)
            self.position.update_order(ticker, size, action_type,
                                       last_position, long_or_short)
            new_position = self.position.latest(ticker, long_or_short)

            self.avg_price.update_order(ticker,
                                        size,
                                        execute_price,
                                        last_position,
                                        last_avg_price,
                                        new_position,
                                        long_or_short)

            self.commission.update_order(ticker,
                                         size,
                                         execute_price,
                                         action_type,
                                         last_commission,
                                         long_or_short)
            self.realized_pnl.update_order(ticker,
                                           size,
                                           execute_price,
                                           action_type,
                                           last_avg_price,
                                           long_or_short)
            self.margin.update_order(ticker, long_or_short)
            self.match_engine.match_order(order)

            self.update(order_executed=True)

    def run(self):
        self._record_order()

    @abc.abstractmethod
    def _update_cash(self, trading_date: str):
        raise NotImplementedError

    @abc.abstractmethod
    def settle_match_engine_and_series(self):
        self.match_engine = MatchEngine(TradeLogBase)  # 对应传入Log模块
        self.series = None  # 含有series的包
        raise NotImplementedError

    @abc.abstractmethod
    def set_setting(self):
        raise NotImplementedError

    @abc.abstractproperty
    def bar_class(self):
        raise NotImplementedError
