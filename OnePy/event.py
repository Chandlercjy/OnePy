import Queue

events = Queue.Queue()

class Event(object):
    pass

class MarketEvent(Event):
    def __init__(self):
        self.type = 'Market'
        # print 'here is a marketevent'

class SignalEvent(Event):
    def __init__(self,info):
        self.type = 'Signal'

        self.signal_type = info['signal_type']

        self.date = info['date']
        self.size = info['size']
        self.price = info['price']
        self.limit = info['limit']
        self.stop = info['stop']
        self.trailamount = info['trailamount']
        self.trailpercent = info['trailpercent']
        self.oco = info['oco']
        self.instrument = info['instrument']

class OrderEvent(Event):
    def __init__(self,info):
        self.type = 'Order'
        self.signal_type = info['signal_type']

        self.date = info['date']
        self.size = info['size']
        self.limit = info['limit']
        self.stop = info['stop']
        self.trailamount = info['trailamount']
        self.trailpercent = info['trailpercent']
        self.oco = info['oco']
        self.instrument = info['instrument']
        self.price = info['price']

        self.status = info['status']

        self.ordertype = None

        self.valid = None
        self.oco = None
        self.parent = None
        self.transmit = None

class PendEvent(Event):
    def __init__(self):
        self.tradeid


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
