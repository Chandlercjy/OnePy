from OnePy import dataseries


class FillBase(object):
    def __init__(self):
        self.initial_cash = 100000
        self.trailingstopprice = "open"

        self.position = dataseries.PositionSeries()
        self.margin = dataseries.MarginSeries()
        self.avg_price = dataseries.Avg_priceSeries()
        self.unrealizedPL = dataseries.UnrealizedPLSeries()
        self.realizedPL = dataseries.RealizedPLSeries()
        self.commission = dataseries.CommissionSeries()
        self.cash = dataseries.CashSeries()
        self.balance = dataseries.BalanceSeries()

        self.order_list = []
        self.trade_list = []
        self.completed_list = []

    def set_cash(self, cash):
        self.initial_cash = cash

    def run_first(self, feed_list):
        """初始化各项数据, 注意多重feed"""

        for f in feed_list:
            instrument = f.instrument
            self.position.initialize(instrument, 0)
            self.margin.initialize(instrument, 0)
            self.avg_price.initialize(instrument, 0)
            self.unrealizedPL.initialize(instrument, 0)
            self.realizedPL.initialize(instrument, 0)
            self.commission.initialize(instrument, 0)
        self.cash.initialize("all", self.initial_cash)
        self.balance.initialize("all", self.initial_cash)

    def set_dataseries_instrument(self, instrument):
        self.position.set_instrument(instrument)
        self.margin.set_instrument(instrument)
        self.avg_price.set_instrument(instrument)
        self.unrealizedPL.set_instrument(instrument)
        self.realizedPL.set_instrument(instrument)
        self.commission.set_instrument(instrument)

    def update_timeindex(self, feed_list):
        pass

    def check_trade_list(self, feed):
        pass

    def check_order_list(self, feed):
        pass

    def run_fill(self, fillevent):
        pass
