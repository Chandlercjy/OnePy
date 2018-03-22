
import queue


class Environment(object):

    """全局要素"""

    events = queue.Queue()

    def __init__(self):
        self.mod_dict = None
        self.feed_list = []
        self.strategy_list = []
        self.risk_management_list = []
        self.logger = None
        self.trading_date = None
        self.calander_date = None
        self.buffer_days = None
        self.global_var = None
        self.execute_on_close_or_next_open = 'open'
