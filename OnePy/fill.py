#coding=utf8
from event import FillEvent, OrderEvent, events

from utils.py3 import with_metaclass
from utils.metabase import MetaParams
import time


class Fill(with_metaclass(MetaParams,object)):
    """笔记：最后记得要整合数据，因为包含了止损止盈单，导致多了些日期相同的单词，应叠加"""
    def __init__(self):
        self.initial_cash = 100000
        self.order_list = []
        self.trade_list = []

        self.position_dict = {}     # {instrument : [{date:xx,position:xx},..,],..}
        self.margin_dict = {}       # {instrument : [{date:xx,margin:xx},..,],..}
        self.profit_dict = {}       # {instrument : [{date:xx,profit:xx},..,],..}
        self.return_dict = {}       # {instrument : [{date:xx,return:xx},..,}],..}
        self.cash_list = []         # [{date:xx,cash:xx},..,..]
        self.total_list = []        # [{date:xx,total:xx},..,..]
        self.avg_price_dict = {}    # {instrument : [{date:xx,avg_price:xx},..,],..}

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

            if f.signal_type == 'Exitall':
                d['margin'] = 0
                self.margin_dict[f.instrument].append(d)

    def _update_position(self,fillevent):
        f = fillevent
        d = dict(date = f.date)
        lpod = self.position_dict[f.instrument][-1] # last_position_dict

        if f.target == 'Forex':
            if f.signal_type == 'Buy':
                d['position'] = lpod['position'] + f.size
                self.position_dict[f.instrument].append(d)

            if f.signal_type == 'Sell':
                d['position'] = lpod['position'] - f.size
                self.position_dict[f.instrument].append(d)

            if f.signal_type == 'Exitall':
                f.size = lpod['position']
                f.signal_type = 'Buy' if lpod['position'] <= 0 else 'Sell'
                d['position'] = 0
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
                # d['profit'] = (f.price*f.size - lapd['avg_price']*lpod['position'])*f.mult
                d['profit'] = (f.price - lapd['avg_price'])*lpod['position']*f.mult
                self.profit_dict[f.instrument].append(d)
            else:
                d['profit'] = (f.price - capd['avg_price'])*cpod['position']*f.mult  # 总利润 = （现价 - 现均价）* 现仓位 * 杠杆
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

        if fillevent.signal_type in ['Buyabove','Buybelow','Sellabove','Sellbelow']:
            # 这里空白，使数据直接继承上一个
            instrument = fillevent.instrument
            [i[j].append(i[j][-1]) for i in [self.position_dict] for j in [instrument]]
            [i[j].append(i[j][-1]) for i in [self.margin_dict] for j in [instrument]]
            [i[j].append(i[j][-1]) for i in [self.profit_dict] for j in [instrument]]
            # [i[j].append(i[j][-1]) for i in [self.return_dict] for j in [instrument]]
            [i[j].append(i[j][-1]) for i in [self.avg_price_dict] for j in [instrument]]
            [i.append(i[-1]) for i in [self.cash_list]]
            [i.append(i[-1]) for i in [self.total_list]]

        else:
            self._update_position(fillevent)
            self._update_avg_price(fillevent)
            self._update_profit(fillevent)
            self._update_total(fillevent)
            self._update_cash(fillevent)
            self._update_return(fillevent)


    def _update_trade_list(self,fillevent):
        """
        根据交易更新trade_list

        注意：分列表，放一起，后删除

        若平仓掉了之前的单，如何将单从trade_list中删除，因为没有必要考虑止盈止损了
        情况一：做多，若有空单，将空单逐个抵消，
                        若抵消后有剩余多单，则多开个多单
                        若无，修改原空单
                     若无，直接加多单
        情况二：做空，若有多单，将多单逐个抵消，若抵消后有剩余，则多开个空单
        情况三：全部平仓，若有单，将所有空单和多单全部抵消
        """

        f = fillevent
        last_position = self.position_dict[f.instrument][-2]['position']
        cur_position = self.position_dict[f.instrument][-1]['position']
        if f.target == 'Forex':
            if f.signal_type == 'Buy':                              # 若为多单!!!!!!!!!!!!!!!!!!
                if last_position < 0: # and cur_position < 0:          # 多抵空
                    for i in self.trade_list:
                        if i.signal_type == 'Sell':                 # 对应只和空单处理
                            if i.size > f.size :                    # 空单大于多单，剩余空单
                                """将trade_list中的单子按顺序替换"""
                                index = self.trade_list.index(i)
                                self.trade_list.pop(index)          # 删除原空单
                                i.size -= f.size                    # 删除原空单
                                f.size = 0
                                if i.size != 0:                          # 现事件归零，后面会删除
                                    self.trade_list.insert(index,i)     # 将修改完的单子放回原位

                            elif i.size <= f.size :                 # 空单小于多单，逐个抵消，即将空单删除
                                """将trade_list中的单子按顺序替换"""
                                self.trade_list.remove(i)           # 删除原空单
                                f.size -= i.size                    # 修改多单仓位，若为0，后面会删除

                            else:
                                print '回测逻辑出错1!!'               # 无作用。用于检查框架逻辑是否有Bug

                elif last_position >= 0 and cur_position > 0:       # 无空单，多单叠多单
                    pass                                            # 不需要修改trade_list

            if f.signal_type == 'Sell':                             # 若为空单!!!!!!!!!!!!!!!!!!
                if last_position > 0: # and cur_position > 0:          # 空抵多
                    for i in self.trade_list:
                        if i.signal_type == 'Buy':                  # 对应只和空单处理
                            if i.size > f.size :                    # 多单大于空单，剩余多单
                                """将trade_list中的单子按顺序替换"""
                                index = self.trade_list.index(i)
                                self.trade_list.pop(index)          # 删除原空单
                                i.size -= f.size                    # 修改空单仓位
                                f.size = 0
                                if i.size != 0:                           # 现事件归零，后面会删除
                                    self.trade_list.insert(index,i)     # 将修改完的单子放回原位

                            elif i.size <= f.size :                 # 多单小于空单，逐个抵消，即将多单删除
                                """将trade_list中的单子按顺序替换"""
                                self.trade_list.remove(i)           # 删除原多单
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
        self._update_info(fillevent)
        self._update_trade_list(fillevent)
        self._to_list(fillevent)

    def check_trade_list(self,feed):
        data1 = feed.cur_bar_list[0]
        """存在漏洞，先判断的止盈止损，后判断移动止损"""

        """检查止盈止损,触发交易"""
        for i in self.trade_list:
            if i.instrument != feed.instrument:
                continue             # 不是同个instrument无法比较，所以跳过

            if i.limit == i.stop == i.trailamount == i.trailpercent:
                continue             # 没有止盈止损，所以跳过

            """根据指令判断，发送Buy or Sell"""
            if i.limit and i.stop:
                if data1['low'] < i.limit < data1['high'] \
                and data1['low'] < i.stop < data1['high'] :
                    print '矛盾的止盈止损，这里选择止损'
                    i.executetype = 'StopLossOrder'
                    i.price = i.stop
                    i.signal_type = 'Sell' if i.signal_type == 'Buy' else 'Buy'
                    i.type = 'Order'
                    i.date = data1['date']
                    i.limit = None
                    i.stop = None
                    events.put(i)

            elif i.limit:
                if data1['low'] < i.limit < data1['high']:
                    i.executetype = 'TakeProfitOrder'
                    i.price = i.limit
                    i.signal_type = 'Sell' if i.signal_type == 'Buy' else 'Buy'
                    i.type = 'Order'
                    i.date = data1['date']
                    i.limit = None
                    events.put(i)
            elif i.stop:
                if data1['low'] < i.stop < data1['high']:
                    i.executetype = 'StopLossOrder'
                    i.price = i.stop
                    i.signal_type = 'Sell' if i.signal_type == 'Buy' else 'Buy'
                    i.type = 'Order'
                    i.date = data1['date']
                    i.stop = None
                    events.put(i)

        """检查移动止损,触发交易"""



    def check_order_list(self,feed):
        """检查挂单是否触发"""
        data1 = feed.cur_bar_list[0]
        for i in self.order_list:
            if i.instrument != feed.instrument:
                continue             # 不是同个instrument无法比较，所以跳过
            if 'Buy' in i.signal_type:
                if i.signal_type == 'Buyabove' and data1['open'] > i.price:
                    i.price = data1['open']
                    i.signal_type = 'Buy'
                    i.date = data1['date']
                    i.type = 'Order'
                    i.executetype = 'MarketTouchedOrder'
                    events.put(i)

                elif i.signal_type == 'Buylbelow' and data1['open'] < i.price:
                    i.price = data1['open']
                    i.signal_type = 'Buy'
                    i.date = data1['date']
                    i.type = 'Order'
                    events.put(i)

                elif data1['low'] < i.price < data1['high']:
                    i.signal_type = 'Buy'
                    i.date = data1['date']
                    i.type = 'Order'
                    i.executetype = 'MarketTouchedOrder'
                    events.put(i)

            if 'Sell' in i.signal_type:
                if i.signal_type == 'Sellabove' and data1['open'] > i.price:
                    i.price = data1['open']
                    i.signal_type = 'Sell'
                    i.date = data1['date']
                    i.type = 'Order'
                    i.executetype = 'MarketTouchedOrder'
                    events.put(i)

                elif i.signal_type == 'Sellbelow' and data1['open'] < i.price:
                    i.price = data1['open']
                    i.signal_type = 'Sell'
                    i.date = data1['date']
                    i.type = 'Order'
                    i.executetype = 'MarketTouchedOrder'
                    events.put(i)

                elif data1['low'] < i.price < data1['high']:
                    i.signal_type = 'Sell'
                    i.date = data1['date']
                    i.type = 'Order'
                    i.executetype = 'MarketTouchedOrder'
                    events.put(i)
