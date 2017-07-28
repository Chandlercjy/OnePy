#coding=utf8

import pandas as pd
import talib as tb
import numpy as np

from copy import copy
from datetime import datetime


class indicatorBase(object):
    def __init__(self):
        self.minperiod = None
        self.instrument = None

        self.preload_bar_list = []

    def set_dtformat(self,bar):
        # 目前只设置支持int和str
        date = bar['date']
        dt = "%Y-%m-%d %H:%M:%S"
        if self.timeindex:
            date = datetime.strptime(str(date), self.dtformat).strftime('%Y-%m-%d')
            return date + ' ' + bar[self.timeindex.lower()]
        else:
            return datetime.strptime(str(date), self.dtformat).strftime(dt)

    def _set_feed(self,marketevent):
        m = marketevent
        self.instrument = m.instrument
        self.iteral_data2 = m.info['iteral_data2']
        self.index_list = [i.lower() for i in m.info['index_list']]
        self.id = self._get_index_dict()  # index_dict 索引值
        self.fromdate = m.info['fromdate']
        self.dtformat = m.info['dtformat']
        self.tmformat = m.info['tmformat']
        self.timeindex = m.info['timeindex']

        self.bar_list = copy(m.info['bar_dict'][m.instrument])
        self.bar_list2 = copy(self.bar_list)
        # self.close = [i['close'] for i in m.bar_dict[m.instrument]]
        self.preload_bar_list = m.info['preload_bar_list']

    def _get_index_dict(self):
        # 生成一个字典，key为index名，value为索引
        func = lambda x: self.index_list.index(x)
        dic = {i : func(i) for i in self.index_list}
        return dic

    def _insert_preload_bar(self,minperiod):
        """直接将preload的dict一个一个插到bardict前面，然后开始计算"""
        """若preload_bar_list为空或者不够，则前进"""
        self.preload_limit = self.preload_bar_list[:minperiod]
        self.bar_list = copy(self.bar_list2)
        [self.bar_list.insert(0,i) for i in self.preload_limit]         # load to bar_list


class indicator(indicatorBase):
    def __init__(self):
        super(indicator,self).__init__()

        # shortcut
        self.SMA = self.SimpleMovingAverage

    def SimpleMovingAverage(self,period,index=-1):
        self.minperiod = period
        self._insert_preload_bar(period)

        data = [i['close'] for i in self.bar_list][-period+index:]
        sma = tb.SMA(np.array(data),period)
        if np.isnan(sma[index]):
            raise Warning
        else:
            return sma[index]
