from OnePy import dataseries


class FillBase(object):
    def __init__(self):
        self.initial_cash = 100000

        self.position = dataseries.PositionSeries()
        self.margin = dataseries.MarginSeries()
        self.avg_price = dataseries.Avg_priceSeries()
        self.unrealizedPL = dataseries.UnrealizedPLSeries()
        self.realizedPL = dataseries.RealizedPLSeries()
        self.commission = dataseries.CommissionSeries()
        self.cash = dataseries.CashSeries()
        self.balance = dataseries.BalanceSeries()

        self._order_list = []
        self._trade_list = []
        self._completed_list = []

    @property
    def completed_list(self):
        return self._completed_list

    def set_cash(self, cash):
        self.initial_cash = cash

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
