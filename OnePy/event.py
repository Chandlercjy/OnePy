import Queue

events = Queue.Queue()

class Event(object):
    pass

class MarketEvent(Event):
    def __init__(self,info):
        self.type = 'Market'
        self.instrument = info['instrument']
        self.cur_bar_list = info['cur_bar_list']
        self.bar_dict = info['bar_dict']

        self.info = info
        # self.indicator = None
        # self.fill = None

class SignalEvent(Event):
    def __init__(self,info):
        self.type = 'Signal'

        self.signal_type = info['signal_type']

        self.date = info['date']
        self.size = info['size']
        self.price = info['price']
        self.limit = info['limit']
        self.stop = info['stop']
        self.trailingstop = info['trailingstop']
        self.oco = info['oco']
        self.instrument = info['instrument']
        self.executetype = info['executetype']
        self.direction = info['direction']


class OrderEvent(Event):
    def __init__(self,info):
        self.type = 'Order'
        self.signal_type = info['signal_type']

        self.date = info['date']
        self.size = info['size']
        self.limit = info['limit']
        self.stop = info['stop']
        self.trailingstop = info['trailingstop']
        self.oco = info['oco']
        self.instrument = info['instrument']
        self.price = info['price']
        self.status = info['status']
        self.executetype = info['executetype']
        self.valid = None
        self.oco = None
        self.parent = None
        self.transmit = None
        self.direction = info['direction']

class FillEvent(Event):
    def __init__(self,info):
        self.type = 'Fill'

        self.signal_type = info['signal_type']
        self.instrument = info['instrument']
        self.date = info['date']
        self.size = info['size']
        self.price = info['price']
        self.limit = info['limit']
        self.stop = info['stop']
        self.trailingstop = info['trailingstop']

        self.valid = info['valid']
        self.oco = info['oco']
        self.parent = info['parent']
        self.transmit = info['transmit']

        self.status = info['status']
        self.executetype = info['executetype']
        self.target = info['target']
        self.commission = info['commission']
        self.commtype = info['commtype']
        self.margin = info['margin']

        self.direction = info['direction']
