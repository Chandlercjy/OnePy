import queue

from OnePy.constants import EVENT
from OnePy.event import EventBus
from OnePy.model.containers import UsefulDict


class Environment(object):

    """全局要素"""

    events = queue.Queue()  # type:queue.Queue

    def __init__(self):
        self.event_bus = EventBus()
        self.mod_dict = None
        self.readers = UsefulDict('Readers')
        self.feeds = UsefulDict('Feeds')
        self.cleaners = UsefulDict('Cleaners')
        self.strategies = UsefulDict('Strategies')
        self.brokers = UsefulDict('Brokers')
        self.risk_managers = UsefulDict('Risk_Managers')
        self.recorders = UsefulDict('Recorders')

        self.signals = []
        self.signals_current = []
        self.signals_trigger = []

        self.orders_mkt_original = []  # 保存最原始的所有market order
        self.orders_mkt_normal = []  # 动态的临时order
        self.orders_mkt_absolute = []

        self.orders_pending = []   # 保存动态挂单的pending
        self.orders_pending_mkt_dict = {}  # 保存都动态的跟随已有market order 的pending

        self.logger = None
        self.buffer_days = None
        self.execute_on_close_or_next_open = 'open'

        self.hedge_mode = False
        self.live_mode = False

        self._config = None

        self.event_loop = [dict(if_event=EVENT.MARKET_UPDATED,
                                then_event=EVENT.DATA_CLEANED,
                                module_dict=self.cleaners),

                           dict(if_event=EVENT.DATA_CLEANED,
                                then_event=EVENT.SIGNAL_GENERATED,
                                module_dict=self.strategies),

                           dict(if_event=EVENT.SIGNAL_GENERATED,
                                then_event=EVENT.SUBMIT_ORDER,
                                module_dict=self.risk_managers),

                           dict(if_event=EVENT.SUBMIT_ORDER,
                                then_event=EVENT.RECORD_RESULT,
                                module_dict=self.brokers),

                           dict(if_event=EVENT.RECORD_RESULT,
                                then_event=None,
                                module_dict=self.recorders)
                           ]
