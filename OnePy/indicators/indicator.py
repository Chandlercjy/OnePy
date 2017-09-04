import talib as tb
import numpy as np
from OnePy.indicators.indicatorbase import IndicatorBase


class Indicator(IndicatorBase):
    def __init__(self, marketevent):
        super(Indicator, self).__init__(marketevent)
        self.SMA = self.SimpleMovingAverage  # shortcut

    def SimpleMovingAverage(self, period, index=-1):
        data = self.get_preload(period, index, 'close')  # 返回period个周期的数据列表
        sma = tb.SMA(data, period)
        return return_NaN(sma, index)


def return_NaN(indicator, index):
    if np.isnan(indicator[index]):
        raise Warning
    else:
        return indicator[index]
