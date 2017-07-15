

from event import FillEvent, OrderEvent, events

from utils.py3 import with_metaclass
from utils.metabase import MetaParams
import time

class PortfolioBase(with_metaclass(MetaParams,object)):
    def __init__(self,feed_list):
        self.hedge_mode = False

        # 注意多个feed
        self.cur_bar_dict = {f.instrument:f.cur_bar_dict for f in feed_list}
        self.bar_dict = {f.instrument:f.bar_dict for f in feed_list}
        self.instrument = [f.instrument for f in feed_list]

        self.initial_cash = 100000
        self.Sizer = 1

        self.cash_dict = []         # [{date:xx,cash:xx},..,..]
        self.position_dict = {}     # {instrument : [{date:xx,long:xx,short:xx},..,],..}

        self.margin_dict = {}       # {instrument : [{date:xx,margin:xx},..,],..}

        self.profit_dict = {}       # {instrument : [{date:xx,long:xx,short:xx},..,],..}

        self.return_dict = {}       # {instrument : [{date:xx,return:xx},..,}],..}
        self.total_list = []        # [{date:xx,total:xx},..,..]


    def _generate_order(self,signal):
        '''
        生成OrderEvent
        '''
        tradeid = time.time()

        info = dict(instrument = signal.instrument,
                    date = signal.date,
                    signal_type = signal.signal_type,
                    size = signal.size,
                    price = signal.price,
                    limit = signal.limit,
                    stop = signal.stop,
                    trailamount = signal.trailamount,
                    trailpercent = signal.trailpercent,
                    status = 'Created')

        order = OrderEvent(info)
        return order

    def _update_cash(self, fill):
        pass

    def _update_position(self, fill):
        pass

    def _update_profit(self, fill):
        pass

    def _update_margin(self, fill):
        pass

    def _update_return(self, fill):
        pass

    def _update_total(self, fill):
        pass



    def _update_raw_info(self):
        pass






    def _general_check(self):
        pass


    def stats(self):
        pass

    def start(self):
        pass

    def prenext(self):
        pass

    def next(self):
        pass
