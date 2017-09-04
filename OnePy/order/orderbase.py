import itertools

from OnePy.order.orderdata import Orderdata


class OrderBase(object):
    """
    ExecTypes = ["Market", "Limit", "Stop", "StopLossOrder", "TakeProfitOrder",
                 "TralingStopLossOrder","CloseAll"]

    OrdTypes = ["Buy", "Sell"]

    Status = [
        "Created", "Submitted", "Filled", "Partial", "Completed",
        "Expired", "Margin", "Rejected",
        "Pending","Triggered","Cancelled"
    ]
    """

    refbasis = itertools.count(1)  # for a unique identifier per order

    def __init__(self, marketevent):
        self.orderID = next(self.refbasis)
        self._drop = False
        self.set_status("Created")
        self._parent = None

        self._instrument = marketevent.instrument
        self._cur_bar = marketevent.cur_bar
        self._executemode = marketevent.executemode
        self._per_comm = marketevent.per_comm
        self._commtype = marketevent.commtype
        self._per_margin = marketevent.per_margin
        self._mult = marketevent.mult
        self._target = marketevent.target
        self._feed = marketevent.feed

        self.Orderdata = None
        self._date = None
        self._units = None
        self._price = None
        self._takeprofit = None
        self._stoploss = None
        self._exectype = None
        self._direction = None
        self._trailingstop_pip_pct = None
        self._trailingstop = None

    @property
    def per_comm(self):
        return self._per_comm

    @property
    def commtype(self):
        return self._commtype

    @property
    def status(self):
        return self._status

    @property
    def orderid(self):
        return self.orderID

    @property
    def per_margin(self):
        return self._per_margin

    @property
    def target(self):
        return self._target

    @property
    def mult(self):
        return self._mult

    @property
    def parent(self):
        return self._parent

    @property
    def ordtype(self):
        return self._ordtype

    @property
    def exectyoe(self):
        return self._exectype

    @property
    def date(self):
        return self._date

    @property
    def direction(self):
        return self._direction

    @property
    def instrument(self):
        return self._instrument

    @property
    def price(self):
        return self._price

    @property
    def units(self):
        return self._units

    @property
    def takeprofit(self):
        return self._takeprofit

    @property
    def stoploss(self):
        return self._stoploss

    @property
    def trailingstop(self):
        return self._trailingstop

    @property
    def feed(self):
        return self._feed

    def set_status(self, status):
        self._status = status

    def set_parent(self, parent):
        self._parent = parent

    def set_trailingstop(self, price):
        self._trailingstop = price

    def set_per_comm(self, per_comm):
        self._per_comm = per_comm

    def set_commtype(self, commtype):
        self._commtype = commtype

    def set_date(self, date):
        self._date = date

    def set_price(self, price):
        self._price = price

    def set_takeprofit(self, price):
        self._takeprofit = price

    def set_stoploss(self, price):
        self._stoploss = price

    def set_exectype(self, exectype):
        self._exectype = exectype

    def set_ordtype(self, ordtype):  # 先set type之后再execute
        self._ordtype = ordtype
        self._direction = 1.0 if ordtype == "Buy" else -1.0

    def set_units(self, units):
        self._units = units


class Order(OrderBase):
    def execute(self, units, price, takeprofit, stoploss, trailingstop, instrument):
        if instrument is None:
            instrument = self._instrument

        self.Orderdata = Orderdata(units=units,
                                   price=price,
                                   takeprofit=takeprofit,
                                   stoploss=stoploss,
                                   trailingstop=trailingstop,
                                   instrument=instrument,
                                   cur_bar=self._cur_bar,
                                   executemode=self._executemode,
                                   ordtype=self._ordtype)
        self._set_Orderdata()

    def _set_Orderdata(self):
        self._instrument = self.Orderdata.instrument
        self._direction = self.Orderdata.direction
        self._date = self.Orderdata.date
        self._units = self.Orderdata.units
        self._price = self.Orderdata.price
        self._takeprofit = self.Orderdata.takeprofit
        self._stoploss = self.Orderdata.stoploss
        self._trailingstop = self.Orderdata.trailingstop
        self._trailingstop_pip_pct = self.Orderdata.trailingstop_pip_pct

        executemode = self.Orderdata.executemode
        if self._exectype == "CloseAll":
            return
        elif self._price > executemode:
            self._exectype = "Stop" if self._ordtype == "Buy" else "Limit"
        elif self._price < executemode:
            self._exectype = "Limit" if self._ordtype == "Buy" else "Stop"
        elif self._price == executemode:
            self._exectype = "Market"

    def _get_trailingprice(self, new, old):
        if self._ordtype == "Buy":
            return max(new, old)
        elif self._ordtype == "Sell":
            return min(new, old)

    def update_trailingstop(self, cur_price):

        if self._trailingstop_pip_pct:
            if self._trailingstop_pip_pct.type == "pips":
                pips = self._trailingstop_pip_pct.pips * self._direction
                new = cur_price - pips
                old = self._trailingstop

                self._trailingstop = self._get_trailingprice(new, old)
            elif self._trailingstop_pip_pct.type == "pct":
                pct = 1 - self._trailingstop_pip_pct.pct * self._direction
                new = cur_price * pct
                old = self._trailingstop
                self._trailingstop = self._get_trailingprice(new, old)
            else:
                raise SyntaxError("trailingstop should be pips or pct!")
