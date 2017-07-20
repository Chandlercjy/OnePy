
#coding=utf8

from event import FillEvent, OrderEvent, events

from utils.py3 import with_metaclass
from utils.metabase import MetaParams
import time

class PortfolioBase(with_metaclass(MetaParams,object)):
    def __init__(self,signalevent):
        self.signalevent = signalevent
        self.Sizer = 1

    def _generate_order(self,signalevent):
        '''
        生成OrderEvent
        '''
        signalevent = self.signalevent

        tradeid = time.time()

        info = dict(instrument = self.signalevent.instrument,
                    date = self.signalevent.date,
                    signal_type = self.signalevent.signal_type,
                    size = self.signalevent.size,
                    price = self.signalevent.price,
                    limit = self.signalevent.limit,
                    stop = self.signalevent.stop,
                    trailingstop = self.signalevent.trailingstop,
                    status = 'Created',
                    executetype = signalevent.executetype,
                    oco = self.signalevent.oco,
                    direction = signalevent.direction)

        order = OrderEvent(info)
        events.put(order)


    def start(self):
        pass

    def prenext(self):
        pass

    def next(self):
        self._generate_order(self.signalevent)

    def run_portfolio(self):
        self.start()
        self.prenext()
        self.next()


    def _general_check(self):
        pass


    def stats(self):
        pass
