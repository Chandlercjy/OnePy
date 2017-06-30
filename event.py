import Queue

events = Queue.Queue()

class Event(object):
    pass

class MarketEvent(Event):
    def __init__(self):
        self.type = 'Market'
        # print 'here is a marketevent'

class SignalEvent(Event):
    def __init__(self, symbol, datetime,price,signal_type,
                lots,percent_sizer=False):
        self.type = 'Signal'
        self.symbol = symbol
        self.datetime = datetime
        self.price = price
        self.signal_type = signal_type
        self.lots = lots  # control the amount of positions
        self.percent = percent_sizer

class OrderEvent(Event):
    def __init__(self, dt, signal_type ,symbol,price,
                 order_type, quantity_l, quantity_s, direction):
        self.type = 'Order'
        self.dt = dt
        self.signal_type = signal_type
        self.symbol = symbol
        self.price = price
        self.order_type = order_type
        self.quantity_l = quantity_l
        self.quantity_s = quantity_s
        self.direction = direction

        self.live = False

    def print_order(self):
        print "%s, %s, %s CREATE @ %s, Type=%s, %s" % \
            (self.dt, self.symbol, self.direction,self.price,
            self.order_type,self.signal_type)

    def cancle_order(self):
        print "%s, %s, %s Cancled! @ %s, Type=%s, %s" % \
            (self.dt, self.symbol, self.direction,self.price,
            self.order_type,self.signal_type)

class FillEvent(Event):
    def __init__(self, timeindex, symbol, exchange, quantity_l, quantity_s,
                signal_type, direction, price, commission=0):
        self.type = 'Fill'
        self.timeindex = timeindex
        self.symbol = symbol
        self.exchange = exchange
        self.quantity_l = quantity_l
        self.quantity_s = quantity_s
        self.signal_type = signal_type
        self.direction = direction
        self.price = price

        # Calculate commission
        self.commission = commission


    def print_executed(self):
        lots = self.quantity_l + self.quantity_s
        print "%s, %s, %s EXECUTED @ %s, lots:%s, Comm:%s" % \
            (self.timeindex, self.symbol, self.direction, self.price,
            lots, self.commission*lots)


    def get_symbol(self):
        return self.symbol

    def get_entry_date(self):
        return self.timeindex


    def get_entry_price(self):
        return self.price

    def get_long_short(self):
        if self.signal_type == 'LONG':
            return 'long'
        if self.signal_type == 'SHORT':
            return 'short'

    def get_qty(self):
        if self.signal_type == 'LONG':
            return self.quantity_l
        if self.signal_type == 'SHORT':
            return self.quantity_s
