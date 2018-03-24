import queue

from OnePy.core.base_order import SignalGenerator
from OnePy.event import EventBus


class Environment(object):

    """全局要素"""

    events = queue.Queue()

    def __init__(self):
        self.event_bus = EventBus()
        self.mod_dict = None
        self.reader_dict = {}
        self.feed_dict = {}
        self.cleaner_dict = {}
        self.strategy_list = []
        self.broker_list = []
        self.risk_manager_list = []
        self.recorder_list = []
        self.order_list = SignalGenerator.order_list

        self.logger = None
        self.buffer_days = None
        self.execute_on_close_or_next_open = 'open'

        self.hedge_mode = False
        self.live_mode = False

        self._config = None
