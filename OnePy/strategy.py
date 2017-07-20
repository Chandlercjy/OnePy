#coding=utf8

from event import events, SignalEvent
from portfolio import *

from utils.py3 import with_metaclass
from utils.metabase import MetaParams


class StrategyBase(with_metaclass(MetaParams, object)):
    def __init__(self,marketevent):

        m = marketevent
        self.bar = m.cur_bar_list
        self.bar_dict = m.bar_dict
        self.data = m.cur_bar_list[0]
        self.close = [i['close'] for i in m.bar_dict[m.instrument]]
        self.instrument = m.instrument
        self.cash = [i['cash'] for i in m.fill.cash_list]
        self.position = [i['position'] for i in m.fill.position_dict[m.instrument]]
        self.margin = [i['margin'] for i in m.fill.margin_dict[m.instrument]]
        self.total = [i['total'] for i in m.fill.total_list]
        self.avg_price = [i['avg_price'] for i in m.fill.avg_price_dict[m.instrument]]

        self.unre_profit = [i['unre_profit'] for i in m.fill.unre_profit_dict[m.instrument]]
        self.re_profit = [i['re_profit'] for i in m.fill.re_profit_dict[m.instrument]]
        self.pricetype = 'open' # 控制计算的价格，可以再OnePy中用 set_pricetype控制

    def pips(self,n):
        n = n*1.0/self._mult
        pips_cls = type('pips',(),dict(pips=n))
        pips_cls.type = 'pips'
        return pips_cls

    def pct(self,n):
        """若输入1，则为原价格的1%"""
        n = n*0.01+1
        pct_cls = type('pct',(),dict(pct=n))
        pct_cls.type = 'pct'
        return pct_cls

    def _check_pips_or_pct(self,signal_type,price,info):
        """控制挂单，控制止盈止损和移动止损"""
        """用于Buy和Sell中，应放到price确定之后"""
        if 'Buy' in signal_type:        # 包含了挂单
            mark = 1
        elif 'Sell' in signal_type:       # 与Buy相反，包含了挂单
            mark = -1
        else:
            raise SyntaxError

        if self.pricetype is 'open': p = self.bar[1]['open']
        elif self.pricetype is 'close': p = self.bar[0]['close']

        #判断开盘价还是收盘价
        if price is 'open':
            price = self.bar[1]['open']
            info['price'] = price
        elif price is 'close':
            price = self.bar[0]['close']
            info['price'] = price

        #控制挂单
        if type(price) is type:
            if price.type is 'pips':
                price = price.pips + p
                info['price'] = price
            elif price.type is 'pct':
                price = p * price.pct
                info['price'] = price
            else:
                raise SyntaxError('price should be pips or pct!')

        #控制止盈止损
        limit = info['limit']
        stop = info['stop']
        if limit:
            if limit.type is 'pips':
                info['limit'] = price + limit.pips * mark
            elif limit.type is 'pct':
                info['limit'] = price * (1+limit.pct * mark)
            else:
                raise SyntaxError('limit should be pips or pct!')
        if stop:
            if stop.type is 'pips':
                info['stop'] = price - stop.pips * mark
            elif stop.type is 'pct':
                info['stop'] = price * (1-stop.pct * mark)
            else:
                raise SyntaxError('stop should be pips or pct!')




    def Buy(self,size,
                limit=None,
                stop=None,
                trailingstop=None,
                instrument=None,
                price = None):

        if price is None:
            price =  self.pricetype
        if instrument is None:
            instrument = self.instrument

        info = dict(signal_type='Buy',
                    date=self.bar[0]['date'],
                    size=size,
                    price=price,
                    limit=limit,
                    stop=stop,
                    trailingstop=trailingstop,
                    oco=False,
                    instrument=instrument,
                    executetype = 'MKT',
                    direction = 1.0)

        self._check_pips_or_pct('Buy',price,info)

        if info['price'] > self.bar[1]['open']:
            info['signal_type'] = 'Buyabove'
        elif info['price'] < self.bar[1]['open']:
            info['signal_type'] = 'Buybelow'

        signalevent = SignalEvent(info)
        events.put(signalevent)

    def Sell(self,size,
                limit=None,
                stop=None,
                trailingstop=None,
                instrument=None,
                price = None):
        if price is None:
            price =  self.pricetype

        if instrument is None or instrument is self.instrument:
            instrument = self.instrument

        info = dict(signal_type='Sell',
                    date=self.bar[0]['date'],
                    size=size,price=price,
                    limit=limit,
                    stop=stop,
                    trailingstop=trailingstop,
                    oco=False,
                    instrument=instrument,
                    executetype = 'MKT',
                    direction = -1.0)

        self._check_pips_or_pct('Sell',price,info)

        if info['price'] > self.bar[1]['open']:
            info['signal_type'] = 'Sellabove'
        elif info['price'] < self.bar[1]['open']:
            info['signal_type'] = 'Sellbelow'


        signalevent = SignalEvent(info)
        events.put(signalevent)



    def Exitall(self,size='all',instrument=None,price=None):

        if price is None:
            price =  self.pricetype

        if instrument is None or instrument is self.instrument:
            instrument = self.instrument

        info = dict(signal_type='Exitall',
                    date=self.bar[0]['date'],
                    size=size,price=price,
                    limit=None,
                    stop=None,
                    trailingstop=None,
                    oco=False,
                    instrument=instrument,
                    executetype = 'MKT')


        if price is 'open':
            price = self.bar[1]['open']
            info['price'] = price
        elif price is 'close':
            price = self.bar[0]['close']
            info['price'] = price


        if self.position[-1] < 0:
            info['signal_type'] = 'Buy'
            info['size'] = self.position[-1] * (-1.0)
            info['direction'] = 1.0
        elif self.position[-1] > 0:
            info['signal_type'] = 'Sell'
            info['size'] = self.position[-1] * 1.0
            info['direction'] = -1.0
        if self.position[-1] == 0:
            pass
        else:
            signalevent = SignalEvent(info)
            events.put(signalevent)


    def Cancel(self):
        pass

    def set_indicator(self):
        pass


    def prestart(self):
        pass

    def start(self):
        self.set_indicator()

    def prenext(self):
        pass

    def next(self):
        """这里写主要的策略思路"""
        pass

    def stop(self):
        pass

    def run_strategy(self):
        self.prestart()
        self.start()
        self.prenext()
        self.next()
        self.stop()



class DIYStrategy(with_metaclass(MetaParams, StrategyBase)):
    def __init__(self,marketevent):
        super(MyStrategy,self).__init__(marketevent)


    def set_indicator(self):
        pass

    def prestart(self):
        pass

    def start(self):
        self.set_indicator()

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
