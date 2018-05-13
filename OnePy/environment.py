from OnePy.event import EventBus


class Environment(object):

    """作为全局共享变量为各模块提供支持"""

    fromdate = None
    todate = None
    event_bus = EventBus()

    mod_dict = {}
    readers = {}
    feeds = {}
    cleaners = {}
    strategies = {}
    brokers = {}
    risk_managers = {}
    recorders = {}
    recorder = None
    logger = None

    signals_normal: list = []  # 保存最原始的所有信号
    signals_trigger: list = []  # 保存最原始的所有挂单信号
    signals_normal_cur: list = []  # 动态地临时信号，会不断刷新
    signals_trigger_cur: list = []  # 动态地临时信号，会不断刷新

    orders_mkt_original: list = []  # 保存最原始的所有订单信号
    orders_mkt_normal: list = []  # 动态地保存当前订单, 会不断刷新
    orders_mkt_absolute: list = []  # 动态地保存触发的挂单并成交信息，会不断刷新
    orders_mkt_submitted: list = []  # 动态地保存成交单，会不断刷新

    orders_pending: list = []   # 动态地保存挂单
    orders_pending_mkt_dict: dict = {}  # 动态地保存跟随市价单的挂单

    event_loop = None
    execute_on_close_or_next_open = 'open'

    def refresh(self):
        """刷新environment防止缓存累积"""
        self.signals_normal: list = []
        self.signals_trigger: list = []
        self.signals_normal_cur: list = []
        self.signals_trigger_cur: list = []
        self.orders_mkt_original: list = []
        self.orders_mkt_normal: list = []
        self.orders_mkt_absolute: list = []
        self.orders_mkt_submitted: list = []
        self.orders_pending: list = []
        self.orders_pending_mkt_dict: dict = {}

    @property
    def trading_datetime(self):
        return self.feeds[self.tickers[0]].date

    @property
    def tickers(self):
        return list(self.readers.keys())
