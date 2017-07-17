#coding=utf8

from event import FillEvent,PendEvent
from event import events

from utils.py3 import with_metaclass
from utils.metabase import MetaParams

class ExecutionHandler(object):

    def __init__(self):
        pass

    def execute_order(self,event):
        pass

class SimulatedBroker(with_metaclass(MetaParams,ExecutionHandler)):

    def __init__(self):
        super(SimulatedBroker,self).__init__()
        self.target = None  # will be settled in OnePiece

        self.commission = 0.0
        self.commtype = None  # fixed & percent
        self.margin = 0
        self.muli = 1

        self.fill_or_pend_event = None
        self._notify_onoff = False
    def submit_order(self,orderevent):

        info = dict(instrument = orderevent.instrument,
                    date = orderevent.date,
                    signal_type = orderevent.signal_type,
                    size = orderevent.size,
                    price = orderevent.price,
                    limit = orderevent.limit,
                    stop = orderevent.stop,
                    trailamount = orderevent.trailamount,
                    trailpercent = orderevent.trailpercent,
                    status = 'Submitted',
                    executetype = orderevent.executetype,
                    valid = orderevent.valid,
                    oco = orderevent.oco,
                    parent = orderevent.parent,
                    transmit = orderevent.transmit,
                    target = self.target,
                    commission = self.commission,
                    commtype = self.commtype,
                    margin = self.margin,
                    muli = self.muli)

        if orderevent.signal_type == 'Buy':

            fillevent = FillEvent(info)
            return fillevent

        if orderevent.signal_type == 'Sell':

            fillevent = FillEvent(info)
            return fillevent


    def check_after(self):
        """检查Order发送后是否执行成功"""
        return True

    def check_before(self,orderevent):
        """检查Order是否能够执行，这个函数只有在backtest时才需要，live则不需要
            检查钱是否足够"""
        if self.target == 'Forex':
            if self.fill.cash_list[-1]['cash'] > self.margin * orderevent.size:
                return True
            else:
                return False


    def start(self,orderevent):
        self.notify(orderevent,self._notify_onoff)
        if self.check_before(orderevent):
            self.fill_or_pend_event = self.submit_order(orderevent)

            self.notify(self.fill_or_pend_event,self._notify_onoff)
        else:
            print 'Order Canceled'


    def prenext(self,orderevent):
        if self.check_before(orderevent) and self.check_after():
            self.fill_or_pend_event.status = 'Accepted'
            events.put(self.fill_or_pend_event)
            self.notify(self.fill_or_pend_event,self._notify_onoff)


    def next(self):
        pass


    def notify(self,event,onoff=False):
        if onoff:
            print '{d}, {i}, {s} {st} @ {p}, Size: {si}, Execute: {ot}\
            '.format(d = event.date,
                                i = event.instrument,
                                s = event.signal_type,
                                st = event.status,
                                p = event.price,
                                si = event.size,
                                ot = event.executetype)


    def run_broker(self,orderevent):
        self.start(orderevent)
        self.prenext(orderevent)
        self.next()
