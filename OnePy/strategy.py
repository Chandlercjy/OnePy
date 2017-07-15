#coding=utf8

from event import events, SignalEvent
from portfolio import *

from utils.py3 import with_metaclass
from utils.metabase import MetaParams


class StrategyBase(with_metaclass(MetaParams, object)):
    def __init__(self,marketevent):
        pass

    def check_order_list(self):
        pass

    def set_indicator(self):
        pass

    def preset_context(self, arg):
        pass


    def Notify_before(self):
        pass

    def prestart(self, arg):
        self.check_order_list()  # 注意！！要重新考虑 放到strategy之前！！

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
        self.instrument = marketevent.instrument

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
                    date=self.bar[1]['date'],
                    size=size,price=price,
                    limit=limit,
                    stop=stop,
                    trailamount=trailamount,
                    trailpercent=trailpercent,
                    oco=oco,
                    instrument=instrument)

        signal = SignalEvent(info)
        put(signal)


    def BuyLimit(self,size,price,
                    limit=None,
                    stop=None,
                    trailamount=None,
                    trailpercent=None,
                    oco=False,
                    instrument=None):
        if instrument is None :
            instrument = self.instrument



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
            print self.bar
            price = self.bar[0]['close']

            info = dict(signal_type='Buy',
                        date=self.bar[0]['date'],
                        size=size,price=self.bar['close'],
                        limit=limit,
                        stop=stop,
                        trailamount=trailamount,
                        trailpercent=trailpercent,
                        oco=False,
                        instrument=instrument)


            signal = SignalEvent(info)
            events.put(signal)

    def Sell(self,size,
                limit=None,
                stop=None,
                trailamount=None,
                trailpercent=None,
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



    def EXIT(self,size,instrument=None):

        if instrument is None :
            instrument = self.instrument



    def Cancel(self):
        pass



    def check_order_list(self):
        pass

    def set_indicator(self):
        pass

    def preset_context(self):
        pass


    def Notify_before(self):
        pass

    def prestart(self):
        self.check_order_list()  # 注意！！要重新考虑 放到strategy之前！！

    def start(self):
        self.set_indicator()
        self.preset_context()

    def prenext(self):
        pass

    def next(self):
        """这里写主要的策略思路"""
        self.Buy(1, price='close')

    def stop(self):
        self.Notify_before()
        pass

    def run_strategy(self):
        self.prestart()
        self.start()
        self.prenext()
        self.next()
        self.stop()
