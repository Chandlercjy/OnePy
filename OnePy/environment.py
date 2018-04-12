from OnePy.event import EventBus
from OnePy.sys_module.components.logger import BacktestLogger


class Environment(object):

    """全局要素"""
    tickers = []
    fromdate = None
    todate = None

    event_bus = EventBus()
    mod_dict = None
    readers = {}
    feeds = {}
    cleaners = {}
    strategies = {}
    brokers = {}
    risk_managers = {}
    recorders = {}
    recorder = None

    signals_normal: list = []
    signals_trigger: list = []
    signals_normal_cur: list = []
    signals_trigger_cur: list = []

    orders_mkt_original: list = []  # 保存最原始的所有market order
    orders_mkt_normal: list = []  # 动态的临时order
    orders_mkt_absolute: list = []
    orders_mkt_submitted: list = []

    orders_pending: list = []   # 保存动态挂单的pending
    orders_pending_mkt_dict: dict = {}  # 保存都动态的跟随已有market order 的pending

    event_loop = None
    gvar = None

    _config = None
    logger = None
    buffer_days = None
    execute_on_close_or_next_open = 'open'

    hedge_mode = False
    live_mode = False

    def refresh(self):

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
