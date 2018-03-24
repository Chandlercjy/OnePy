import queue
from typing import Dict

from OnePy.event import EVENT, EventBus


class Environment(object):

    """全局要素"""

    events = queue.Queue()  # type:queue.Queue

    def __init__(self):
        self.event_bus = EventBus()
        self.mod_dict = None
        self.readers = {}  # type:Dict
        self.feeds = {}  # type:Dict
        self.cleaners = {}  # type:Dict
        self.strategies = {}  # type:Dict
        self.brokers = {}  # type:Dict
        self.risk_managers = {}  # type:Dict
        self.recorders = {}  # type:Dict

        self.signals = {}  # type:Dict
        self.signals_current = {}  # type:Dict
        self.orders = {}  # type:Dict
        self.orders_pending = {}  # type:Dict
        self.orders_current = {}  # type:Dict

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
