#coding=utf8

from event import events, SignalEvent
from order import *
from portfolio import *

from utils.py3 import with_metaclass
from utils.metabase import MetaParams


class StrategyBase(with_metaclass(MetaParams, object))
    def __init__(self,portfolio):
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


class MyStrategy(with_metaclass(MetaParams, StrategyBase))
    def __init__(self,portfolio):
        super(MyStrategy,self).__init__(portfolio)
        self.bar = portfolio.cur_bar_dict
        self.instrument = portfolio.instrument

    def BuyStop(self,size,price,
                    limit=None,
                    stop=None,
                    trailamount=None,
                    trailpercent=None,
                    oco=False,    # oco 请传入指令
                    instrument=self.instrument):


        info = dict(signal_type='BuyStop',
                    date=self.bar['date'],
                    size=size,price=price,
                    limit=limit,
                    stop=stop,
                    trailamount=trailamount,
                    trailpercent=trailpercent,
                    oco=oco,
                    instrument=instrument)

        signal = SignalEvent(info)
        put(signal)
        pass


    def BuyLimit(self,size,price,
                    limit=None,
                    stop=None,
                    trailamount=None,
                    trailpercent=None,
                    oco=False,
                    instrument=self.instrument):
        pass


    def Buy(self,size,
                limit=None,
                stop=None,
                trailamount=None,
                trailpercent=None,
                instrument=self.instrument):
        pass


    def Sell(self,size,
                limit=None,
                stop=None,
                trailamount=None,
                trailpercent=None,
                instrument=self.instrument):
        pass


    def SellLimit(self,size,price,
                    limit=None,
                    stop=None,
                    trailamount=None,
                    trailpercent=None,
                    oco=False,
                    instrument=self.instrument):
        pass


    def SellStop(self,size,price,
                    limit=None,
                    stop=None,
                    trailamount=None,
                    trailpercent=None,
                    oco=False,
                    instrument=self.instrument):
        pass


    def EXIT(self,size,instrument=self.instrument):
        pass

    def Cancel(self):
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
