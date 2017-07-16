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
                    transmit = orderevent.transmit,
                    target = self.target,
                    commission = self.commission,
                    commtype = self.commtype,
                    margin = self.margin,
                    muli = self.muli)

        if orderevent.signal_type == 'Buy':
            more_info = dict(executetype = 'MKT')
            info.update(more_info)
            fillevent = FillEvent(info)
            return fillevent

        if orderevent.signal_type == 'Sell':
            more_info = dict(executetype = 'MKT')
            info.update(more_info)
            fillevent = FillEvent(info)
            return fillevent



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

    def check_before(self,orderevent):
        """检查Order是否能够执行，这个函数只有在backtest时才需要，live则不需要
            检查钱是否足够"""

        if self.target == 'Forex':
            if self.fill.cash_list[-1]['cash'] > self.margin * orderevent.size:
                return True
            else:
                return False


    def start(self):
        pass


    def prenext(self):
        pass


    def next(self,orderevent):
        if self.check_before(orderevent) and self.check_after():
            fill_or_pend_event = self.submit_order(orderevent)
            events.put(fill_or_pend_event)



    def run_broker(self,orderevent):
        self.start()
        self.prenext()
        self.next(orderevent)
