#coding=utf8
from event import FillEvent, OrderEvent, events

from utils.py3 import with_metaclass
from utils.metabase import MetaParams
import time


class Fill(with_metaclass(MetaParams,object)):
    def __init__(self):


        self.initial_cash = 100000

        self.position_dict = {}     # {instrument : [{date:xx,position:xx},..,],..}
        self.margin_dict = {}       # {instrument : [{date:xx,margin:xx},..,],..}
        self.profit_dict = {}       # {instrument : [{date:xx,profit:xx},..,],..}
        self.return_dict = {}       # {instrument : [{date:xx,return:xx},..,}],..}
        self.cash_list = []         # [{date:xx,cash:xx},..,..]
        self.total_list = []        # [{date:xx,total:xx},..,..]
        self.avg_price_dict = {}    # {instrument : [{date:xx,avg_price:xx},..,],..}

    def _update_margin(self,fillevent):
        f = fillevent
        d = dict(date = f.date)
        last_margin_dict = self.margin_dict[f.instrument][-1]
        if f.target == 'Forex':
            if f.signal_type == 'Buy':
                margin = f.margin * f.size
                d['margin'] = last_margin_dict['margin'] + margin
                self.margin_dict[f.instrument].append(d)

            if f.signal_type == 'Sell':
                margin = f.margin * f.size
                d['margin'] = last_margin_dict['margin'] - margin
                self.margin_dict[f.instrument].append(d)

    def _update_position(self,fillevent):
        f = fillevent
        d = dict(date = f.date)
        last_position_dict = self.position_dict[f.instrument][-1]

        if f.target == 'Forex':
            if f.signal_type == 'Buy':
                d['position'] = last_position_dict['position'] + f.size
                self.position_dict[f.instrument].append(d)
            if f.signal_type == 'Sell':
                d['position'] = last_position_dict['position'] - f.size
                self.position_dict[f.instrument].append(d)




    def _update_avg_price(self,fillevent):
        """计算profit要用到最新position数据，所以在update_position之后"""
        f = fillevent
        d = dict(date = f.date)
        lapd = self.avg_price_dict[f.instrument][-1]  # last_avg_dict
        lpod = self.position_dict[f.instrument][-2]   # last_position_dict
        cpod = self.position_dict[f.instrument][-1]   # cur_position_dict

        if f.target == 'Forex':
            if cpod['position'] == 0:
                d['avg_price'] = 0
                self.avg_price_dict[f.instrument].append(d)
            else:
                if f.signal_type == 'Buy':
                    last_value = lpod['position']*lapd['avg_price']
                    cur_value = f.size*f.price
                    d['avg_price'] = (last_value + cur_value)/cpod['position']  # 总均价 = （上期总市值 + 本期总市值）/ 总仓位
                    self.avg_price_dict[f.instrument].append(d)
                if f.signal_type == 'Sell':
                    last_value = lpod['position']*lapd['avg_price']
                    cur_value = -f.size*f.price
                    d['avg_price'] = (last_value + cur_value)/cpod['position']  # 总均价 = （上期总市值 + 本期总市值）/ 总仓位
                    self.avg_price_dict[f.instrument].append(d)




    def _update_profit(self,fillevent):
        """用到最新position数据，所以在update_position之后"""
        """运用最新平均价格进行计算, 所以在update_avg_price之后"""
        f = fillevent
        d = dict(date = f.date)
        lpd = self.profit_dict[f.instrument][-1]  # last_profit_dict
        cpod = self.position_dict[f.instrument][-1]  # cur_position_dict
        capd = self.avg_price_dict[f.instrument][-1]  # cur_avg_price_dict
        lapd = self.avg_price_dict[f.instrument][-2]  # last_avg_price_dict
        lpod = self.position_dict[f.instrument][-2]

        if f.target == 'Forex':     # Buy和 Sell 都一样
            if capd['avg_price'] == 0:
                d['profit'] = (f.price*f.size - lapd['avg_price']*lpod['position'])*f.muli
                self.profit_dict[f.instrument].append(d)
            else:
                d['profit'] = (f.price - capd['avg_price'])*cpod['position']*f.muli  # 总利润 = （现价 - 现均价）* 现仓位 * 杠杆
                self.profit_dict[f.instrument].append(d)


    def _update_total(self,fillevent):
        """用到最新profit数据，所以在update_profit之后"""
        f = fillevent
        d = dict(date = f.date)
        cpd = self.profit_dict[f.instrument][-1]  # cur_profit_dict

        if f.target == 'Forex':
            d['total'] = self.initial_cash + cpd['profit']
            self.total_list.append(d)


    def _update_cash(self,fillevent):
        """计算cash要用到最新数据，所以最后一个算"""
        f = fillevent
        d = dict(date = f.date)
        cur_total_dict = self.total_list[-1]

        if f.target == 'Forex':
            cur_margin_dict = self.margin_dict[f.instrument][-1]
            d['cash'] = cur_total_dict['total'] - abs(cur_margin_dict['margin'])
            if d['cash'] < 0: # 应该添加一个检测爆仓的函数，并返回一个清仓指令
                d['cash'] = 0
            self.cash_list.append(d)



    def _update_return(self,fillevent):
        pass



    def _update_info(self,fillevent):
        if fillevent.target in ['Forex','Futures']:
            self._update_margin(fillevent)
        self._update_position(fillevent)
        self._update_avg_price(fillevent)
        self._update_profit(fillevent)
        self._update_total(fillevent)
        self._update_cash(fillevent)
        self._update_return(fillevent)

    def run_first(self,feed_list):
        """初始化各项数据"""
        for f in feed_list:
            date = 'start'
            instrument = f.instrument
            self.position_dict = {instrument:[{'date':date,'position':0}]}     # {instrument : [{date:xx,long:xx,short:xx},..,],..}
            self.margin_dict = {instrument:[{'date':date,'margin':0}]}               # {instrument : [{date:xx,margin:xx},..,],..}
            self.profit_dict = {instrument:[{'date':date,'profit':0}]}       # {instrument : [{date:xx,long:xx,short:xx},..,],..}
            self.return_dict = {instrument:[{'date':date,'return':0}]}               # {instrument : [{date:xx,return:xx},..,}],..}
            self.avg_price_dict = {instrument:[{'date':date,'avg_price':0}]}    # {instrument : [{date:xx,long:xx,short:xx},..,],..}
            self.cash_list = [{'date':date,'cash':self.initial_cash}]                        # [{date:xx,cash:xx},..,..]
            self.total_list = [{'date':date,'total':self.initial_cash}]                      # [{date:xx,total:xx},..,..]
