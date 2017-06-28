import datetime
import Queue

from abc import ABCMeta, abstractmethod

from event import FillEvent, OrderEvent
from event import events

class ExecutionHandler(object):

    __metaclass__ = ABCMeta

    def __init__(self,events,commission):
        self.events = events
        self.commission = commission

    @abstractmethod
    def execute_order(self,event):
        raise NotImplemented('Should implement execute_order()')

class SimulatedExecutionHandler(ExecutionHandler):
    def __init__(self,commission):
        super(SimulatedExecutionHandler,self).__init__(events,commission)


    def execute_order(self,orderevent):
        if orderevent.live:
            time = datetime.datetime.utcnow()
        else:
            time = orderevent.dt

        fill_event = FillEvent(timeindex = time,
                               symbol = orderevent.symbol,
                               exchange = 'BLUE SEA',
                               quantity_l = orderevent.quantity_l,
                               quantity_s = orderevent.quantity_s,
                               signal_type = orderevent.signal_type,
                               direction = orderevent.direction,
                               price = orderevent.price,
                               commission = self.commission)
        self.events.put(fill_event)
