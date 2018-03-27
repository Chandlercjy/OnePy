import queue

from OnePy.constants import EVENT
from OnePy.event import EventBus
from OnePy.model.containers import UsefulDict


class Environment(object):

    """全局要素"""

    event_bus = EventBus()
    mod_dict = None
    readers = UsefulDict('Readers')
    feeds = UsefulDict('Feeds')
    cleaners = UsefulDict('Cleaners')
    strategies = UsefulDict('Strategies')
    brokers = UsefulDict('Brokers')
    risk_managers = UsefulDict('Risk_Managers')
    recorders = UsefulDict('Recorders')

    signals = []
    signals_current = []
    signals_trigger = []

    orders_mkt_original = []  # 保存最原始的所有market order
    orders_mkt_normal = []  # 动态的临时order
    orders_mkt_absolute = []

    orders_pending = []   # 保存动态挂单的pending
    orders_pending_mkt_dict = {}  # 保存都动态的跟随已有market order 的pending

    logger = None
    buffer_days = None
    execute_on_close_or_next_open = 'open'

    hedge_mode = False
    live_mode = False

    _config = None

    event_loop = None
