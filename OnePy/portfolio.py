
#coding=utf8
import time

from .event import FillEvent, OrderEvent, events


class PortfolioBase(object):
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
                    takeprofit = self.signalevent.takeprofit,
                    stoploss = self.signalevent.stoploss,
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
