

class GlobalVariables(object):

    env = None
    """全局变量"""

    def __init__(self):
        self.context = None
        self.tickers = None  # type:list

        self.trading_date = None
        self.calander_date = None

    @property
    def feed(self):
        return self.env.feed_dict


class Context(object):

    def __init__(self):
        self.fromdate = None
        self.todate = None


class TickerSetting(object):

    """表示跟随每一个Ticker的配置信息,只有在recorder中才用用到"""

    def __init__(self):

        # 以下变量会被初始化
        self._per_comm = None
        self._commtype = None
        self._mult = None
        self._per_margin = None
        self._executemode = None
        self._trailingstop_executemode = None


class DataBuffer(object):

    """用于与读取数据，便与恢复状态或计算指标"""

    def __init__(self):
        pass
