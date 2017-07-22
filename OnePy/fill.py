#coding=utf8
from event import FillEvent, events

from utils.py3 import with_metaclass
from utils.metabase import MetaParams
import time
from copy import copy
import funcy as fy

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
        self.unre_profit_dict = {}  # {instrument : [{date:xx,unre_profit:xx},..,],..}
        self.re_profit_dict = {}    # {instrument : [{date:xx,re_profit:xx},..,],..}
        self.cash_list = []         # [{date:xx,cash:xx},..,..]
        self.total_list = []        # [{date:xx,total:xx},..,..]


    def run_first(self,feed_list):
        """初始化各项数据"""
        """初始化调整 注意多重feed"""
        date = 'start'
        for f in feed_list:
            instrument = f.instrument
            self.position_dict[instrument]=[{'date':date,'position':0}]
            self.margin_dict[instrument]=[{'date':date,'margin':0}]
            self.avg_price_dict[instrument]=[{'date':date,'avg_price':0}]
            self.unre_profit_dict[instrument]=[{'date':date,'unre_profit':0}]
            self.re_profit_dict[instrument]=[{'date':date,'re_profit':0}]
        self.cash_list = [{'date':date,'cash':self.initial_cash}]
        self.total_list = [{'date':date,'total':self.initial_cash}]


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

        if f.target in ['Forex','Futures','Stock']:
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
                if f.signal_type in ['Buy', 'Sell']:
                    last_value = lpod['position']*lapd['avg_price']
                    cur_value = f.direction*f.size*(f.price + comm)
                    d['avg_price'] = (last_value + cur_value)/cpod['position']  # 总均价 = （上期总市值 + 本期总市值）/ 总仓位
                    self.avg_price_dict[f.instrument].append(d)

        if f.target is 'Stock':
            comm = 1 + f.commission*f.direction           # 交易费为市值的百分比
            if cpod['position'] == 0:
                d['avg_price'] = 0
                self.avg_price_dict[f.instrument].append(d)
            else:
                if f.signal_type in ['Buy', 'Sell']:
                    last_value = lpod['position']*lapd['avg_price']
                    cur_value = f.direction*f.size*f.price*comm
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

        if f.target is 'Stock':     # Buy和 Sell 都一样
            if capd['avg_price'] == 0:
                d['unre_profit'] = 0
                self.unre_profit_dict[f.instrument].append(d)
            else:
                diff = f.price - capd['avg_price']
                d['unre_profit'] = diff*cpod['position']    # 总利润 = （现价 - 现均价）* 现仓位
                self.unre_profit_dict[f.instrument].append(d)


    def _update_total(self,fillevent):
        """用到最新profit数据，所以在update_profit之后"""
        f = fillevent
        d = dict(date = f.date)
        t_re_profit = sum([i[-1].values()[-1] for i in self.re_profit_dict.values()])
        t_profit = t_re_profit + self.unre_profit_dict[f.instrument][-1]['unre_profit']
        if f.target in ['Forex','Futures','Stock']:
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
            self.cash_list.append(d)

        elif f.target is 'Stock':
            cur_mktv = 0
            for f in self.feed_list:
                price = f.cur_bar_list[0][self.pricetype]    # 控制计算的价格，同指令成交价一样
                cur_mktv += price * self.position_dict[f.instrument][-1]['position']
            d['cash'] = cur_total_dict['total'] - cur_mktv
            self.cash_list.append(d)

    def _update_info(self,fillevent):

        ab_list = ['Buyabove','Buybelow','Sellabove','Sellbelow']
        if fillevent.signal_type in ab_list:
            # 什么都不做
            pass
        else:
            if fillevent.target in ['Forex','Futures']:   # 保证金交易
                self._update_margin(fillevent)
                self.margin_dict[fillevent.instrument].pop(-2)

            self._update_position(fillevent)
            self._update_avg_price(fillevent)
            self._update_profit(fillevent)
            self._update_total(fillevent)
            self._update_cash(fillevent)

            # 删除重复

            self.position_dict[fillevent.instrument].pop(-2)
            self.avg_price_dict[fillevent.instrument].pop(-2)
            self.unre_profit_dict[fillevent.instrument].pop(-2)
            self.cash_list.pop(-2)
            self.total_list.pop(-2)


    def update_timeindex(self,feed_list):
        """保持每日数据更新"""

        self.feed_list = feed_list      # 为了传递给stock计算cash

        # 检查若多个feed的话，日期是否相同：
        def _check_date():
            date_dict = {}
            if len(feed_list) > 1:
                for i in range(len(feed_list)):
                    date_dict[str(i)] = feed_list[i].cur_bar_list[0]['date']
                if len(set(date_dict.values()).difference()) > 1:
                    raise SyntaxError('The date of feed is not identical!')
                else:
                    pass

        _check_date()
        date = feed_list[-1].cur_bar_list[0]['date']

        for f in feed_list:
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
        t_re_profit = sum([i['re_profit'] for i in fy.cat(self.re_profit_dict.values())])
        t_profit = t_re_profit + unre_profit

        total = self.initial_cash + t_profit        # 初始资金和总利润
        self.total_list.append({'date':date,'total':total})

        #更新cash
        if f.target in ['Forex','Futures']:
            t_margin = sum(map(abs, [i[-1].values()[-1] for i in self.margin_dict.values()])) # margin需要求绝对值
            cash = total - t_margin
            self.cash_list.append({'date':date,'cash':cash})
        else:
            cur_mktv = 0
            for f in feed_list:
                price = f.cur_bar_list[0][self.pricetype]    # 控制计算的价格，同指令成交价一样
                cur_mktv += price * self.position_dict[f.instrument][-1]['position']
            cash = total - cur_mktv
            self.cash_list.append({'date':date,'cash':cash})

        # 检查是否爆仓
        if self.total_list[-1]['total'] < 0 or self.cash_list[-1]['cash'] < 0:
            for i in feed_list:
                i.continue_backtest = False
            print '爆仓了！！！！'

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
        ls_list = ['TakeProfitOrder','StopLossOrder']
        def get_re_profit(trade_size):
            if f.target is 'Forex':
                d = dict(date = f.date)
                d['re_profit'] = (f.price - (i.price-comm))*trade_size*self._mult * i.direction
                self.re_profit_dict[f.instrument].append(d)
            elif f.target is 'Stock':
                comms = 1.0 + f.commission*f.direction
                d = dict(date = f.date)
                d['re_profit'] = (f.price*comms-i.price)*trade_size * i.direction
                self.re_profit_dict[f.instrument].append(d)

        if f.target in ['Forex','Futures','Stock']:
            # 检查是否来源于触发了止盈止损的单
            if f.executetype in ls_list:
                for i in self.trade_list:
                    if f.dad is i:             # 找到爸爸了
                        self.trade_list.remove(i)       # 删除原空单
                        get_re_profit(f.size)
                        f.size = 0
                        i.size = 0
            else:
                if f.signal_type is 'Buy' and last_position < 0:            # 若为多单!!!!!!!!!!!!!!!!!!
                    for i in self.trade_list:
                        if f.instrument is i.instrument and i.signal_type is 'Sell':                 # 对应只和空单处理
                            if i.size > f.size :                    # 空单大于多单，剩余空单
                                index = self.trade_list.index(i)
                                self.trade_list.pop(index)          # 删除原空单
                                i.size -= f.size                    # 删除原空单
                                get_re_profit(f.size)
                                f.size = 0
                                if i.size != 0:                          # 现事件归零，后面会删除
                                    self.trade_list.insert(index,i)     # 将修改完的单子放回原位

                            elif i.size <= f.size :                 # 空单小于多单，逐个抵消，即将空单删除
                                self.trade_list.remove(i)           # 删除原空单
                                get_re_profit(i.size)
                                f.size -= i.size                    # 修改多单仓位，若为0，后面会删除
                            else:
                                print '回测逻辑出错1!!'               # 无作用。用于检查框架逻辑是否有Bug


                elif f.signal_type is 'Sell' and last_position > 0:                             # 若为空单!!!!!!!!!!!!!!!!!!
                    for i in self.trade_list:
                        if f.instrument is i.instrument and i.signal_type is 'Buy':                  # 对应只和空单处理
                            if i.size > f.size :                    # 多单大于空单，剩余多单
                                index = self.trade_list.index(i)
                                self.trade_list.pop(index)          # 删除原空单
                                i.size -= f.size                    # 修改空单仓位
                                get_re_profit(f.size)
                                f.size = 0
                                if i.size != 0:                           # 现事件归零，后面会删除
                                    self.trade_list.insert(index,i)     # 将修改完的单子放回原位

                            elif i.size <= f.size :                 # 多单小于空单，逐个抵消，即将多单删除
                                self.trade_list.remove(i)           # 删除原多单
                                get_re_profit(i.size)
                                f.size -= i.size                    # 修改空单仓位，若为0，后面会删除
                            else:
                                print '回测逻辑出错2!!'               # 无作用。用于检查框架逻辑是否有Bug



    def _to_list(self,fillevent):
        ab_list = ['Buyabove','Buybelow','Sellabove','Sellbelow']
        if fillevent.signal_type in ab_list:                        # 若是check_trade_list传递过来的，则不append
            self.order_list.append(fillevent)

        else:
            if fillevent.size != 0:
                self.trade_list.append(fillevent)

    def run_fill(self, fillevent):
        """每次指令发过来后，先直接记录下来，然后再去对冲仓位"""
        self._update_info(fillevent)
        self._update_trade_list(fillevent)
        self._to_list(fillevent)



    def check_trade_list(self,feed):
        """ 存在漏洞，先判断的止盈止损，后判断移动止损
            每次触发止盈止损后，发送一个相反的指令，并且自己对冲掉自己
            因为假设有10个多单，5个止损，5个没止损，若止损时对冲5个没止损的单，则会产生错误
            这种情况只会出现在同时多个Buy或者Sell，且有不同的stop或者limit
            所以给多一个dad属性，用于回去寻找自己以便对冲自己                      """

        def put_limit_stop(trade):
            trade.signal_type = 'Sell' if trade.signal_type is 'Buy' else 'Buy'
            trade.type = 'Order'
            trade.date = data1['date']
            trade.limit = None
            trade.stop = None
            trade.direction = 1.0 if trade.signal_type is 'Buy' else -1.0
            events.put(trade)


        data1 = feed.cur_bar_list[0]
        # 检查止盈止损,触发交易
        for t in self.trade_list:
            i = copy(t)                                         # 必须要复制，不然会修改掉原来的订单
            i.dad = t                                           # 等下要回去原来的列表里面找爸爸

            if i.instrument != feed.instrument:
                continue                                        # 不是同个instrument无法比较，所以跳过
            if i.limit is i.stop is i.trailingstop:
                continue                                        # 没有止盈止损，所以跳过

            # 根据指令判断，发送Buy or Sell
            try:
                if i.limit and i.stop:
                    if data1['low'] < i.limit < data1['high'] \
                    and data1['low'] < i.stop < data1['high'] :
                        print '矛盾的止盈止损，这里选择止损'
                        i.executetype = 'StopLossOrder'
                        i.price = i.stop
                        put_limit_stop(i)
                        continue
                if i.limit:
                    if data1['low'] < i.limit < data1['high'] \
                    or (i.limit < data1['low'] if i.signal_type is 'Buy' else False) \
                    or (i.limit > data1['high'] if i.signal_type is 'Sell' else False):
                        i.executetype = 'TakeProfitOrder'
                        i.price = i.limit
                        put_limit_stop(i)
                        continue
                if i.stop:
                    if data1['low'] < i.stop < data1['high'] \
                    or (i.stop > data1['high'] if i.signal_type is 'Buy' else False) \
                    or (i.stop < data1['low'] if i.signal_type is 'Sell' else False):
                        i.executetype = 'StopLossOrder'
                        i.price = i.stop
                        put_limit_stop(i)
                        continue
            except:
                raise SyntaxError('Catch a Bug!')

            # 检查移动止损,触发交易
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
