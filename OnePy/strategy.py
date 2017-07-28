#coding=utf8
from .event import events, SignalEvent
from .utils.py3 import with_metaclass
from .utils.metabase import MetaParams
from .indicator import indicator

class StrategyBase(with_metaclass(MetaParams, object)):
    def __init__(self,marketevent):

        m = marketevent
        self.m = marketevent
        self.pricetype = 'open'             # 控制计算的价格，可以再OnePy中用 set_pricetype控制
        self.target = None      # 会在开始的时候从_pass_to_market中传递过来

        self.bar = m.cur_bar_list
        self.bar_dict = m.bar_dict
        self.data = m.bar_dict[m.instrument]
        self.close = [i['close'] for i in m.bar_dict[m.instrument]]
        self.instrument = m.instrument
        self.cash = [i['cash'] for i in m.fill.cash_list]
        self.position = [i['position'] for i in m.fill.position_dict[m.instrument]]
        self.margin = [i['margin'] for i in m.fill.margin_dict[m.instrument]]
        self.total = [i['total'] for i in m.fill.total_list]
        self.avg_price = [i['avg_price'] for i in m.fill.avg_price_dict[m.instrument]]
        self.unre_profit = [i['unre_profit'] for i in m.fill.unre_profit_dict[m.instrument]]
        self.re_profit = sum([i['re_profit'] for i in m.fill.re_profit_dict[m.instrument]])

        self._signal_list = []

    def set_indicator(self):
        self.indicator = indicator()
        self.indicator._set_feed(self.m)
        self.i = self.indicator     # shortcut


    def pips(self,n):

        if self.m.target is 'Forex':
            n = n*1.0/self._mult
        elif self.m.target in ['Stock','Futures']:
            pass
        pips_cls = type('pips',(),dict(pips=n))
        pips_cls.type = 'pips'
        return pips_cls

    def pct(self,n):
        """若输入1，则为原价格的1%"""
        n = n*0.01
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


    def _set_info(self,signal,direction,size,limit,stop,
                            trailingstop,instrument,price):
        info = dict(signal_type=signal,
                    date=self.bar[0]['date'],
                    size=size,price=price,
                    limit=limit,
                    stop=stop,
                    trailingstop=trailingstop,
                    oco=False,
                    instrument=instrument,
                    executetype = 'MKT',
                    direction = direction)
        return info

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

        info = self._set_info('Buy',1.0,size,limit,stop,
                                trailingstop,instrument,price)
        self._check_pips_or_pct('Buy',price,info)

        if info['price'] > self.bar[1]['open']:         #判断挂单方向
            info['signal_type'] = 'Buyabove'
        elif info['price'] < self.bar[1]['open']:
            info['signal_type'] = 'Buybelow'

        self._signal_list.append(SignalEvent(info))

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

        info = self._set_info('Sell',-1.0,size,limit,stop,
                                trailingstop,instrument,price)
        self._check_pips_or_pct('Sell',price,info)

        if info['price'] > self.bar[1]['open']:         #判断挂单方向
            info['signal_type'] = 'Sellabove'
        elif info['price'] < self.bar[1]['open']:
            info['signal_type'] = 'Sellbelow'

        self._signal_list.append(SignalEvent(info))

    def Exitall(self,size='all',instrument=None,price=None):

        if price is None:
            price =  self.pricetype

        if instrument is None or instrument is self.instrument:
            instrument = self.instrument

        info = self._set_info('Exitall',None,size,None,None,
                                None,instrument,price)

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
            self._signal_list.append(SignalEvent(info))


    def Cancel(self):
        pass


    # def prestart(self):
    #     pass

    def _start(self):
        self.set_indicator()

    def prenext(self):
        pass

    def next(self):
        """这里写主要的策略思路"""
        pass

    def stop(self):
        for i in self._signal_list:
            events.put(i)

    def run_strategy(self):
        # self.prestart()
        self._start()
        self.prenext()
        try:
            self.next()
            self.stop()
        except Warning:
            date = str(self.m.cur_bar_list[0]['date'])
            print('No trade on '+ date + 'for Loading Indicator')
            # print('Name specific')
        except IndexError:
            date = str(self.m.cur_bar_list[0]['date'])
            print('No trade on '+ date + 'for Loading other Variables')




class DIYStrategy(with_metaclass(MetaParams, StrategyBase)):
    def __init__(self,marketevent):
        super(MyStrategy,self).__init__(marketevent)

    def prenext(self):
        pass

    def next(self):
        """这里写主要的策略思路"""
        if self.data['close'] > self.data['open']:
            self.Buy(0.1)
        if self.data['close'] < self.data['open']:
            self.Sell(0.1)

    def stop(self):
        pass
