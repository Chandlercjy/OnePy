#coding=utf8
from event import FillEvent, events

from utils.py3 import with_metaclass
from utils.metabase import MetaParams
import time


class Fill(with_metaclass(MetaParams,object)):
    """笔记：最后记得要整合数据，因为包含了止损止盈单，导致多了些日期相同的单词，应叠加"""
    def __init__(self):
        self.initial_cash = 100000
        self.pricetype = 'open'
        self._mult = 1

        self.order_list = []
        self.trade_list = []

        self.margin_dict = {}       # {instrument : [{date:xx,margin:xx},..,],..}
        self.position_dict = {}     # {instrument : [{date:xx,position:xx},..,],..}
        self.avg_price_dict = {}    # {instrument : [{date:xx,avg_price:xx},..,],..}
        self.unre_profit_dict = {}       # {instrument : [{date:xx,profit:xx},..,],..}
        self.re_profit_dict = {}       # {instrument : [{date:xx,profit:xx},..,],..}
        self.cash_list = []         # [{date:xx,cash:xx},..,..]
        self.total_list = []        # [{date:xx,total:xx},..,..]
        self.return_list = []      # {instrument : [{date:xx,return:xx},..,}],..}

    def run_first(self,feed_list):
        """初始化各项数据"""
        """初始化调整 注意多重feed"""
        date = 'start'
        for f in feed_list:
            instrument = f.instrument
            self.position_dict.update({instrument:[{'date':date,'position':0}]})     # {instrument : [{date:xx,long:xx,short:xx},..,],..}
            self.margin_dict.update({instrument:[{'date':date,'margin':0}]})               # {instrument : [{date:xx,margin:xx},..,],..}
            self.avg_price_dict.update({instrument:[{'date':date,'avg_price':0}]})    # {instrument : [{date:xx,long:xx,short:xx},..,],..}
            self.unre_profit_dict.update({instrument:[{'date':date,'unre_profit':0}]})       # {instrument : [{date:xx,long:xx,short:xx},..,],..}
            self.re_profit_dict.update({instrument:[{'date':date,'re_profit':0}]})       # {instrument : [{date:xx,long:xx,short:xx},..,],..}
        self.cash_list = [{'date':date,'cash':self.initial_cash}]                        # [{date:xx,cash:xx},..,..]
        self.total_list = [{'date':date,'total':self.initial_cash}]                      # [{date:xx,total:xx},..,..]
        self.return_list = [{'date':date,'return':0}]                      # {instrument : [{date:xx,return:xx},..,}],..}


    def _update_margin(self,fillevent):
        f = fillevent
        d = dict(date = f.date)
        last_margin_dict = self.margin_dict[f.instrument][-1]
        if f.target is 'Forex':
            if f.signal_type is 'Buy':
                margin = f.margin * f.size
                d['margin'] = last_margin_dict['margin'] + margin
                self.margin_dict[f.instrument].append(d)

            elif f.signal_type is 'Sell':
                margin = f.margin * f.size
                d['margin'] = last_margin_dict['margin'] - margin
                self.margin_dict[f.instrument].append(d)

            elif 'above' in f.signal_type or 'below' in f.signal_type:
                pass
            else:
                raise SystemError

    def _update_position(self,fillevent):
        f = fillevent
        d = dict(date = f.date)
        lpod = self.position_dict[f.instrument][-1] # last_position_dict

        if f.target is 'Forex':
            if f.signal_type is 'Buy':
                d['position'] = lpod['position'] + f.size
                self.position_dict[f.instrument].append(d)

            elif f.signal_type is 'Sell':
                d['position'] = lpod['position'] - f.size
                self.position_dict[f.instrument].append(d)

            elif 'above' in f.signal_type or 'below' in f.signal_type:
                pass
            else:
                raise SyntaxError

    def _update_avg_price(self,fillevent):
        """计算profit要用到最新position数据，所以在update_position之后"""
        f = fillevent
        d = dict(date = f.date)
        lapd = self.avg_price_dict[f.instrument][-1]  # last_avg_dict
        lpod = self.position_dict[f.instrument][-2]   # last_position_dict
        cpod = self.position_dict[f.instrument][-1]   # cur_position_dict
        if f.target is 'Forex':
            comm = f.commission*f.direction/self._mult
            if cpod['position'] == 0:
                d['avg_price'] = 0
                self.avg_price_dict[f.instrument].append(d)
            else:
                if f.signal_type is 'Buy':
                    last_value = lpod['position']*lapd['avg_price']
                    cur_value = f.direction*f.size*(f.price + comm)
                    d['avg_price'] = (last_value + cur_value)/cpod['position']  # 总均价 = （上期总市值 + 本期总市值）/ 总仓位
                    self.avg_price_dict[f.instrument].append(d)
                elif f.signal_type is 'Sell':
                    last_value = lpod['position']*lapd['avg_price']
                    cur_value = f.direction*f.size*(f.price + comm)
                    d['avg_price'] = (last_value + cur_value)/cpod['position']  # 总均价 = （上期总市值 + 本期总市值）/ 总仓位
                    self.avg_price_dict[f.instrument].append(d)

    def _update_profit(self,fillevent):
        """用到最新position数据，所以在update_position之后"""
        """运用最新平均价格进行计算, 所以在update_avg_price之后"""
        f = fillevent
        d = dict(date = f.date)
        lpd = self.unre_profit_dict[f.instrument][-1]  # last_profit_dict
        cpod = self.position_dict[f.instrument][-1]  # cur_position_dict
        capd = self.avg_price_dict[f.instrument][-1]  # cur_avg_price_dict
        lapd = self.avg_price_dict[f.instrument][-2]  # last_avg_price_dict
        lpod = self.position_dict[f.instrument][-2]

        if f.target is 'Forex':     # Buy和 Sell 都一样
            if capd['avg_price'] == 0:
                d['unre_profit'] = 0
                self.unre_profit_dict[f.instrument].append(d)
            else:
                diff = f.price - capd['avg_price']
                d['unre_profit'] = diff*cpod['position']*self._mult # 总利润 = （现价 - 现均价）* 现仓位 * 杠杆
                self.unre_profit_dict[f.instrument].append(d)

    def _update_total(self,fillevent):
        """用到最新profit数据，所以在update_profit之后"""
        f = fillevent
        d = dict(date = f.date)
        t_re_profit = sum([i[-1].values()[-1] for i in self.re_profit_dict.values()])
        t_profit = t_re_profit + self.unre_profit_dict[f.instrument][-1]['unre_profit']
        if f.target is 'Forex':
            d['total'] = self.initial_cash + t_profit
            self.total_list.append(d)

    def _update_cash(self,fillevent):
        """用到最新total数据，所以在_update_total之后"""
        f = fillevent
        d = dict(date = f.date)
        cur_total_dict = self.total_list[-1]

        if f.target is 'Forex':
            t_margin = sum(map(abs, [i[-1].values()[-1] for i in self.margin_dict.values()]))  # margin需要求绝对值
            d['cash'] = cur_total_dict['total'] - t_margin
            if d['cash'] < 0: # 应该添加一个检测爆仓的函数，并返回一个清仓指令
                d['cash'] = 0
                print '爆仓了！！！！'
            self.cash_list.append(d)

    def _update_return(self,fillevent):
        """用到最新total数据，所以在_update_total之后"""
        f = fillevent
        d = dict(date = f.date)
        cur_total_dict = self.total_list[-1]
        if f.target is 'Forex':
            d['return'] = cur_total_dict['total']*1.0/self.initial_cash
            self.return_list.append(d)

    def _update_info(self,fillevent):
        if fillevent.target in ['Forex','Futures']:
            self._update_margin(fillevent)

        if fillevent.signal_type in ['Buyabove','Buybelow','Sellabove','Sellbelow']:
            # 什么都不做
            pass
        else:
            self._update_position(fillevent)
            self._update_avg_price(fillevent)
            self._update_profit(fillevent)
            self._update_total(fillevent)
            self._update_cash(fillevent)
            self._update_return(fillevent)

            # 删除重复
            self.margin_dict[fillevent.instrument].pop(-2)
            self.position_dict[fillevent.instrument].pop(-2)
            self.avg_price_dict[fillevent.instrument].pop(-2)
            self.unre_profit_dict[fillevent.instrument].pop(-2)
            self.cash_list.pop(-2)
            self.total_list.pop(-2)
            self.return_list.pop(-2)

    def update_timeindex(self,feed_list):
        """保持每日数据更新"""
        for f in feed_list:
            date = f.cur_bar_list[0]['date']
            price = f.cur_bar_list[0][self.pricetype]    # 控制计算的价格，同指令成交价一样

            #更新保证金
            if f.target in ['Forex','Futures']:
                margin = self.margin_dict[f.instrument][-1]['margin']
                self.margin_dict[f.instrument].append({'date':date,'margin':margin})

            #更新平均价格
            avg_price = self.avg_price_dict[f.instrument][-1]['avg_price']
            self.avg_price_dict[f.instrument].append({'date':date,'avg_price':avg_price})

            #更新仓位
            position = self.position_dict[f.instrument][-1]['position']
            self.position_dict[f.instrument].append({'date':date,'position':position})

            #更新利润
            unre_profit = (price - avg_price) * position * self._mult
            self.unre_profit_dict[f.instrument].append({'date':date,'unre_profit':unre_profit})

        #更新total
        date = feed_list[-1].cur_bar_list[0]['date']
        t_re_profit = sum([i[-1].values()[-1] for i in self.re_profit_dict.values()])
        t_profit = t_re_profit + unre_profit

        total = self.initial_cash + t_profit        # 初始资金和总利润
        self.total_list.append({'date':date,'total':total})

        #更新cash
        t_margin = sum(map(abs, [i[-1].values()[-1] for i in self.margin_dict.values()])) # margin需要求绝对值
        cash = total - t_margin
        self.cash_list.append({'date':date,'cash':cash})

        #更新return
        return_ = total/self.initial_cash
        self.return_list.append({'date':date,'return':return_})


    def _update_trade_list(self,fillevent):
        """
        根据交易更新trade_list
        若平仓掉了之前的单，如何将单从trade_list中删除，因为没有必要考虑止盈止损了
        情况一：做多，若有空单，将空单逐个抵消，
                        若抵消后有剩余多单，则多开个多单
                        若无，修改原空单
                     若无，直接加多单
        情况二：做空，同情况一相反
        情况三：全部平仓，若有单，将所有空单和多单全部抵消
        """

        f = fillevent
        last_position = self.position_dict[f.instrument][-2]['position']
        cur_position = self.position_dict[f.instrument][-1]['position']
        comm = f.commission*f.direction/self._mult
        if f.target is 'Forex':
            if f.signal_type is 'Buy':                              # 若为多单!!!!!!!!!!!!!!!!!!
                if last_position < 0: # and cur_position < 0:          # 多抵空
                    for i in self.trade_list:
                        if f.instrument is i.instrument:
                            if i.signal_type is 'Sell':                 # 对应只和空单处理
                                if i.size > f.size :                    # 空单大于多单，剩余空单
                                    index = self.trade_list.index(i)
                                    self.trade_list.pop(index)          # 删除原空单
                                    i.size -= f.size                    # 删除原空单

                                    d = dict(date = f.date)
                                    d['re_profit'] = (f.price - i.price+comm) * f.size * self._mult * i.direction
                                    self.re_profit_dict[f.instrument].append(d)

                                    f.size = 0
                                    if i.size != 0:                          # 现事件归零，后面会删除
                                        self.trade_list.insert(index,i)     # 将修改完的单子放回原位

                                elif i.size <= f.size :                 # 空单小于多单，逐个抵消，即将空单删除
                                    self.trade_list.remove(i)           # 删除原空单

                                    d = dict(date = f.date)
                                    d['re_profit'] = (f.price - i.price+comm) * i.size * self._mult * i.direction
                                    self.re_profit_dict[f.instrument].append(d)

                                    f.size -= i.size                    # 修改多单仓位，若为0，后面会删除

                                else:
                                    print '回测逻辑出错1!!'               # 无作用。用于检查框架逻辑是否有Bug

                        elif last_position >= 0 and cur_position > 0:       # 无空单，多单叠多单
                            pass                                            # 不需要修改trade_list

            if f.signal_type is 'Sell':                             # 若为空单!!!!!!!!!!!!!!!!!!
                if last_position > 0: # and cur_position > 0:          # 空抵多
                    for i in self.trade_list:
                        if f.instrument is i.instrument:
                            if i.signal_type is 'Buy':                  # 对应只和空单处理
                                if i.size > f.size :                    # 多单大于空单，剩余多单
                                    index = self.trade_list.index(i)
                                    self.trade_list.pop(index)          # 删除原空单
                                    i.size -= f.size                    # 修改空单仓位

                                    d = dict(date = f.date)
                                    d['re_profit'] = (f.price - i.price+comm) * f.size * self._mult * i.direction
                                    self.re_profit_dict[f.instrument].append(d)

                                    f.size = 0
                                    if i.size != 0:                           # 现事件归零，后面会删除
                                        self.trade_list.insert(index,i)     # 将修改完的单子放回原位

                                elif i.size <= f.size :                 # 多单小于空单，逐个抵消，即将多单删除
                                    self.trade_list.remove(i)           # 删除原多单

                                    d = dict(date = f.date)
                                    d['re_profit'] = (f.price - i.price+comm) * i.size * self._mult * i.direction
                                    self.re_profit_dict[f.instrument].append(d)

                                    f.size -= i.size                    # 修改空单仓位，若为0，后面会删除

                                else:
                                    print '回测逻辑出错2!!'               # 无作用。用于检查框架逻辑是否有Bug

                        elif last_position <= 0 and cur_position < 0:       # 无空单，多单叠多单
                            pass                                            # 不需要修改trade_list



    def _to_list(self,fillevent):
        """问题：若平仓掉了之前的单，如何将单从trade_list中删除，因为没有必要考虑止盈止损了"""
        """分两个列表"""
        if fillevent.signal_type in ['Buyabove','Buybelow','Sellabove','Sellbelow']: # 若是check_trade_list传递过来的，则不append
            self.order_list.append(fillevent)

        else:
            if fillevent.size != 0:
                self.trade_list.append(fillevent)

    def run_fill(self, fillevent):
        self._update_trade_list(fillevent)
        self._to_list(fillevent)
        self._update_info(fillevent)


    def check_trade_list(self,feed):
        data1 = feed.cur_bar_list[0]
        """存在漏洞，先判断的止盈止损，后判断移动止损"""

        """检查止盈止损,触发交易"""
        for i in self.trade_list:
            if i.instrument != feed.instrument:
                continue             # 不是同个instrument无法比较，所以跳过

            if i.limit is i.stop is i.trailingstop:
                continue             # 没有止盈止损，所以跳过

            """根据指令判断，发送Buy or Sell"""
            if i.limit and i.stop:
                if data1['low'] < i.limit < data1['high'] \
                and data1['low'] < i.stop < data1['high'] :
                    print '矛盾的止盈止损，这里选择止损'
                    i.executetype = 'StopLossOrder'
                    i.price = i.stop
                    i.signal_type = 'Sell' if i.signal_type is 'Buy' else 'Buy'
                    i.type = 'Order'
                    i.date = data1['date']
                    i.limit = None
                    i.stop = None
                    i.direction = 1.0 if i.signal_type is 'Buy' else -1.0
                    events.put(i)

            elif i.limit:
                if data1['low'] < i.limit < data1['high']:
                    i.executetype = 'TakeProfitOrder'
                    i.price = i.limit
                    i.signal_type = 'Sell' if i.signal_type is 'Buy' else 'Buy'
                    i.type = 'Order'
                    i.date = data1['date']
                    i.limit = None
                    i.direction = 1.0 if i.signal_type is 'Buy' else -1.0
                    events.put(i)
            elif i.stop:
                if data1['low'] < i.stop < data1['high']:
                    i.executetype = 'StopLossOrder'
                    i.price = i.stop
                    i.signal_type = 'Sell' if i.signal_type is 'Buy' else 'Buy'
                    i.type = 'Order'
                    i.date = data1['date']
                    i.stop = None
                    i.direction = 1.0 if i.signal_type is 'Buy' else -1.0
                    events.put(i)

            """检查移动止损,触发交易"""
            if i.trailingstop:
                if ((data1[self.pricetype] < i.price) and (i.signal_type is 'Buy')) \
                or ((data1[self.pricetype] > i.price) and (i.signal_type is 'Sell')):  # 若单子盈利
                    if i.trailingstop.type is 'pips':
                        i.stop = i.price - i.trailingstop.pips * i.direction
                    elif i.trailingstop.type is 'pct':
                        i.stop = i.price * (1-i.trailingstop.pct * i.direction)
                    else:
                        raise SyntaxError('trailingstop should be pips or pct!')


    def check_order_list(self,feed):
        """检查挂单是否触发"""
        data1 = feed.cur_bar_list[0]

        def set_event(signal_type,order,change_price=True):
            self.order_list.remove(order)
            if change_price:
                order.price = data1['open']       # 按跳水价成交
            order.signal_type = signal_type
            order.date = data1['date']
            order.type = 'Order'
            order.executetype = 'MarketTouchedOrder'
            events.put(order)


        for i in self.order_list:
            if i.instrument != feed.instrument:
                continue             # 不是同个instrument无法比较，所以跳过

            # 多单挂单
            if 'Buy' in i.signal_type:
                if i.signal_type is 'Buyabove' and data1['open'] > i.price:
                    set_event('Buy',i)
                elif i.signal_type is 'Buylbelow' and data1['open'] < i.price:
                    set_event('Buy',i)
                elif data1['low'] < i.price < data1['high']:
                    set_event('Buy',i,False)    # 按原价成交

            # 空单挂单
            if 'Sell' in i.signal_type:
                if i.signal_type is 'Sellabove' and data1['open'] > i.price:
                    set_event('Sell',i)
                elif i.signal_type is 'Sellbelow' and data1['open'] < i.price:
                    set_event('Sell',i)
                elif data1['low'] < i.price < data1['high']:
                    set_event('Sell',i,False)   # 按原价成交
