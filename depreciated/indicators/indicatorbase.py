from copy import copy

import numpy as np


class IndicatorBase(object):
    def __init__(self, marketevent):
        self.instrument = None
        self.preload_bar_list = []

        self.instrument = marketevent.instrument
        self.iteral_buffer = marketevent.feed.iteral_buffer
        self.bar_list = copy(marketevent.bar.data)
        self.bar_list2 = copy(self.bar_list)
        self.preload_bar_list = marketevent.feed.preload_bar_list

    def get_preload(self, minperiod, index, ohlc='close'):
        """将preload插入到bar_dict前，然后根据当前时间点动态获取固定长度的数据"""
        preload_limit = self.preload_bar_list[:minperiod]
        self.bar_list = copy(self.bar_list2)
        for i in preload_limit:
            self.bar_list.insert(0, i)  # load to bar_list

        data = [i[ohlc] for i in self.bar_list][-minperiod + index:]
        return np.array(data)

