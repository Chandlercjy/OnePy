#coding=utf8

from event import FillEvent
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
        self.mult = 1

        self.fillevent_checked = None
        self._notify_onoff = False
    def submit_order(self,orderevent):

        info = dict(instrument = orderevent.instrument,
                    date = orderevent.date,
                    signal_type = orderevent.signal_type,
                    size = orderevent.size,
                    price = orderevent.price,
                    limit = orderevent.limit,
                    stop = orderevent.stop,
                    trailingstop = orderevent.trailingstop,
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
                    direction = orderevent.direction)

        fillevent = FillEvent(info)
        return fillevent


    def check_after(self):
        """检查Order发送后是否执行成功"""
        return True

    def check_before(self,orderevent):
        """检查Order是否能够执行，这个函数只有在backtest时才需要，live则不需要
            检查钱是否足够"""

        o = orderevent
        if self.target == 'Forex':
            if self.fill.cash_list[-1]['cash'] > self.margin * o.size + \
            self.fill.margin_dict[o.instrument][-1]['margin'] * o.direction \
            or 'Order' in o.executetype:
                return True
            else:
                return False



    def start(self,orderevent):
        self.notify(orderevent,self._notify_onoff)
        if self.check_before(orderevent):
            self.fillevent_checked = self.submit_order(orderevent)
            self.notify(self.fillevent_checked,self._notify_onoff)
        else:
            print 'Cash is not enough! Order Canceled'


    def prenext(self,orderevent):
        if self.check_before(orderevent) and self.check_after():
            self.fillevent_checked.status = 'Accepted'
            events.put(self.fillevent_checked)
            self.notify(self.fillevent_checked,self._notify_onoff)


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
        if orderevent.signal_type is 'Exitall':
            self._for_Exitall(orderevent)
        else:
            self.start(orderevent)
            self.prenext(orderevent)
            self.next()
