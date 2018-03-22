import queue

events = queue.Queue()


class EventBase(object):
    """
    Event的传递实际上是order的传递
    主要将order内相关属性都显示到event中，包括：
        feed, order，date, instrument, units，exectype，price, 
        ordtype, takeprofit, stoploss, trailingstop, direction, 
        status, target, per_comm, commtype, per_margin, mult
    """

    def __init__(self, order):
        self._order = order

    @property
    def order(self):
        return self._order

    @order.setter
    def order(self, value):
        self._order = value

    @property
    def feed(self):
        return self._order.feed

    @feed.setter
    def feed(self, value):
        self._order.set_feed(value)

    @property
    def units(self):
        return self._order.units

    @units.setter
    def units(self, value):
        self._order.set_units(value)

    @property
    def exectype(self):
        return self._order.exectype

    @exectype.setter
    def exectype(self, value):
        self._order.set_exectype(value)

    @property
    def price(self):
        return self._order.price

    @price.setter
    def price(self, value):
        self._order.set_price(value)

    @property
    def ordtype(self):
        return self._order.ordtype

    @ordtype.setter
    def ordtype(self, value):
        self._order.set_ordtype(value)

    @property
    def date(self):
        return self._order.date

    @date.setter
    def date(self, value):
        self._order.set_date(value)

    @property
    def takeprofit(self):
        return self._order.takeprofit

    @takeprofit.setter
    def takeprofit(self, value):
        self._order.set_takeprofit(value)

    @property
    def stoploss(self):
        return self._order.stoploss

    @stoploss.setter
    def stoploss(self, value):
        self._order.set_stoploss(value)

    @property
    def trailingstop(self):
        return self._order.trailingstop

    @trailingstop.setter
    def trailingstop(self, value):
        self._order.set_trailingstop(value)

    @property
    def instrument(self):
        return self._order.instrument

    @instrument.setter
    def instrument(self, value):
        self._order.set_instrument(value)

    @property
    def direction(self):
        return self._order.direction

    @direction.setter
    def direction(self, value):
        self._order.set_direction(value)

    @property
    def status(self):
        return self._order.status

    @status.setter
    def status(self, value):
        self._order.set_status(value)

    @property
    def target(self):
        return self._order.target

    @target.setter
    def target(self, value):
        self._order.set_target(value)

    @property
    def per_comm(self):
        return self._order.per_comm

    @per_comm.setter
    def per_comm(self, value):
        self._order.set_per_comm(value)

    @property
    def commtype(self):
        return self._order.commtype

    @commtype.setter
    def commtype(self, value):
        self._order.set_commtype(value)

    @property
    def per_margin(self):
        return self._order.per_comm

    @per_margin.setter
    def per_margin(self, value):
        self._order.set_per_margin(value)

    @property
    def mult(self):
        return self._order.mult

    @mult.setter
    def mult(self, value):
        self._order.set_mult(value)


class MarketEvent(object):
    def __init__(self, feed):
        self.type = 'Market'
        self.feed = feed
        self.instrument = feed.instrument
        self.cur_bar = feed.cur_bar
        self.bar = feed.bar
        self.per_comm = feed.per_comm
        self.commtype = feed.commtype
        self.per_margin = feed.per_margin
        self.mult = feed.mult
        self.executemode = feed.executemode
        self.target = feed.target


class SignalEvent(EventBase):
    def __init__(self, order):
        super(SignalEvent, self).__init__(order)
        self.type = 'Signal'


class OrderEvent(EventBase):
    def __init__(self, order):
        super(OrderEvent, self).__init__(order)
        self.type = 'Order'


class FillEvent(EventBase):
    def __init__(self, order):
        super(FillEvent, self).__init__(order)
        self.type = 'Fill'

class LiveFillEvent(EventBase):
    def __init__(self,order):
        super(LiveFillEvent, self).__init__(order)
        self.type = "Fill"