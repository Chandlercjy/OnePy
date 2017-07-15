
#coding=utf8

from event import FillEvent, OrderEvent, events

from utils.py3 import with_metaclass
from utils.metabase import MetaParams
import time

class PortfolioBase(with_metaclass(MetaParams,object)):
    def __init__(self,feed_list):
        self.hedge_mode = False

        # 注意多个feed
        self.cur_bar_list = {f.instrument:f.cur_bar_list for f in feed_list}
        self.bar_dict = {f.instrument:f.bar_dict for f in feed_list}
        self.instrument = [f.instrument for f in feed_list]

        self.initial_cash = 100000
        self.Sizer = 1
        self.instrument_list = [f.instrument for f in feed_list]


    def _generate_order(self,signalevent):
        '''
        生成OrderEvent
        '''
        tradeid = time.time()

        info = dict(instrument = signalevent.instrument,
                    date = signalevent.date,
                    signal_type = signalevent.signal_type,
                    size = signalevent.size,
                    price = signalevent.price,
                    limit = signalevent.limit,
                    stop = signalevent.stop,
                    trailamount = signalevent.trailamount,
                    trailpercent = signalevent.trailpercent,
                    status = 'Created',
                    oco = signalevent.oco)

        order = OrderEvent(info)
        events.put(order)


    def start(self):
        pass

    def prenext(self):
        pass

    def next(self,signalevent):
        self._generate_order(signalevent)

    def run_portfolio(self,signalevent):
        self.start()
        self.prenext()
        self.next(signalevent)





    def _general_check(self):
        pass


    def stats(self):
        pass
