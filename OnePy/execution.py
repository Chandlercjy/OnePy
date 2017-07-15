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

class SimulatedBroker(ExecutionHandler):
    def __init__(self):
        super(SimulatedBroker,self).__init__()


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
                    valid = orderevent.valid,
                    oco = orderevent.oco,
                    parent = orderevent.parent,
                    transmit = orderevent.transmit)

        if orderevent.signal_type == 'Buy':

            more_info = dict(executetype = 'MKT')


            info.update(more_info)
            fillevent = FillEvent(info)
            return fillevent

        if orderevent.signal_type == 'Sell':
            pass

        if orderevent.signal_type == 'BuyLimit':

            pendevent = PendEvent(info)
            events.put(pendevent)
            return pendevent

        if orderevent.signal_type == 'BuyStop':
            pass

        if orderevent.signal_type == 'SellLimit':
            pass


        if orderevent.signal_type == 'SellStop':
            pass



    def check_after(self):
        """检查Order发送后是否执行成功"""
        return True

    def check_before(self):
        """检查Order是否能够执行，这个函数只有在backtest时才需要，live则不需要"""
        return True

    def start(self):
        pass


    def prenext(self):
        pass


    def next(self,orderevent):
        if self.check_before():
            fill_or_pend_event = self.submit_order(orderevent)
        if self.check_after():
            events.put(fill_or_pend_event)


    def run_broker(self,orderevent):
        self.start()
        self.prenext()
        self.next(orderevent)
