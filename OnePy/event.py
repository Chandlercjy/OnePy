import Queue

events = Queue.Queue()

class Event(object):
    pass

class MarketEvent(Event):
    def __init__(self,info):
        self.type = 'Market'
        self.instrument = info['instrument']
        self.cur_bar_list = info['cur_bar_list']


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


        self.valid = None
        self.oco = None
        self.parent = None
        self.transmit = None

class PendEvent(Event):
    def __init__(self):
        self.type = 'Pend'
        self.tradeid


class FillEvent(Event):
    def __init__(self,info):
        self.type = 'Fill'

        self.signal_type = info['signal_type']
        self.date = info['date']
        self.size = info['size']
        self.trailamount = info['trailamount']
        self.trailpercent = info['trailpercent']
        self.instrument = info['instrument']
        self.price = info['price']
        self.status = info['status']
        self.executetype = info['executetype']
        self.target = info['target']
        self.commission = info['commission']
        self.commtype = info['commtype']
        self.margin = info['margin']
        self.muli = info['muli']

    def _what_target(self,target):
        self.target = target
