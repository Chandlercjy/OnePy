#coding=utf8

from event import events, SignalEvent
from portfolio import *

from utils.py3 import with_metaclass
from utils.metabase import MetaParams


class StrategyBase(with_metaclass(MetaParams, object)):
    def __init__(self,marketevent):
        pass

    def set_indicator(self):
        pass

    def preset_context(self, arg):
        pass


    def Notify_before(self):
        pass

    def prestart(self, arg):
        pass

    def start(self, arg):
        self.set_indicator()
        self.preset_context()

    def prenext(self):
        pass

    def next(self, arg):
        """这里写主要的策略思路"""
        pass

    def stop(self):
        self.Notify_before()
        pass


class MyStrategy(with_metaclass(MetaParams, StrategyBase)):
    def __init__(self,marketevent):
        super(MyStrategy,self).__init__(marketevent)

        self.bar = marketevent.cur_bar_list
        self.data = self.bar[0]
        self.instrument = marketevent.instrument


    def Buy(self,size,
                limit=None,
                stop=None,
                trailamount=None,
                trailpercent=None,
                instrument=None,
                price = 'open'):

        if instrument is None or instrument == self.instrument:
            instrument = self.instrument

        if price == 'open':
            price = self.bar[1]['open']

        if price == 'close':
            price = self.bar[0]['close']

        info = dict(signal_type='Buy',
                    date=self.bar[0]['date'],
                    size=size,price=price,
                    limit=limit,
                    stop=stop,
                    trailamount=trailamount,
                    trailpercent=trailpercent,
                    oco=False,
                    instrument=instrument)

        signalevent = SignalEvent(info)
        events.put(signalevent)

    def Sell(self,size,
                limit=None,
                stop=None,
                trailamount=None,
                trailpercent=None,
                instrument=None,
                price = 'open'):

        if instrument is None or instrument == self.instrument:
            instrument = self.instrument

        if price == 'open':
            price = self.bar[1]['open']

        if price == 'close':
            price = self.bar[0]['close']

        info = dict(signal_type='Sell',
                    date=self.bar[0]['date'],
                    size=size,price=price,
                    limit=limit,
                    stop=stop,
                    trailamount=trailamount,
                    trailpercent=trailpercent,
                    oco=False,
                    instrument=instrument)

        signalevent = SignalEvent(info)
        events.put(signalevent)


    def BuyStop(self,size,price,
                    limit=None,
                    stop=None,
                    trailamount=None,
                    trailpercent=None,
                    oco=False,    # oco 请传入指令
                    instrument=None):
        if instrument is None :
            instrument = self.instrument


        info = dict(signal_type='BuyStop',
                    date=self.bar[0]['date'],
                    size=size,price=price,
                    limit=limit,
                    stop=stop,
                    trailamount=trailamount,
                    trailpercent=trailpercent,
                    oco=oco,
                    instrument=instrument)

        signalevent = SignalEvent(info)
        put(signalevent)


    def BuyLimit(self,size,price,
                    limit=None,
                    stop=None,
                    trailamount=None,
                    trailpercent=None,
                    oco=False,
                    instrument=None):
        if instrument is None :
            instrument = self.instrument


    def SellLimit(self,size,price,
                    limit=None,
                    stop=None,
                    trailamount=None,
                    trailpercent=None,
                    oco=False,
                    instrument=None):

        if instrument is None :
            instrument = self.instrument

    def SellStop(self,size,price,
                    limit=None,
                    stop=None,
                    trailamount=None,
                    trailpercent=None,
                    oco=False,
                    instrument=None):
        if instrument is None :
            instrument = self.instrument



    def Exitall(self,size='all',instrument=None,price = 'open'):

        if instrument is None or instrument == self.instrument:
            instrument = self.instrument

        if price == 'open':
            price = self.bar[1]['open']

        if price == 'close':
            price = self.bar[0]['close']

        info = dict(signal_type='Exit',
                    date=self.bar[0]['date'],
                    size=size,price=price,
                    limit=limit,
                    stop=stop,
                    trailamount=trailamount,
                    trailpercent=trailpercent,
                    oco=False,
                    instrument=instrument)

        signalevent = SignalEvent(info)
        events.put(signalevent)

    def Cancel(self):
        pass


    def set_indicator(self):
        pass

    def preset_context(self):
        pass


    def Notify_before(self):
        pass

    def prestart(self):
        pass

    def start(self):
        self.set_indicator()
        self.preset_context()

    def prenext(self):
        pass

    def next(self):
        """这里写主要的策略思路"""
        if self.data['close'] > self.data['open']:
            self.Buy(0.1)
        if self.data['close'] < self.data['open']:
            self.Sell(0.1)



    def stop(self):
        self.Notify_before()
        pass

    def run_strategy(self):
        self.prestart()
        self.start()
        self.prenext()
        self.next()
        self.stop()
