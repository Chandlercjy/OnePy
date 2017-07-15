from event import FillEvent, OrderEvent, events

from utils.py3 import with_metaclass
from utils.metabase import MetaParams
import time


class Fill(with_metaclass(MetaParams,object)):
    def __init__(self):
        self.cash_dict = []         # [{date:xx,cash:xx},..,..]
        self.position_dict = {}     # {instrument : [{date:xx,long:xx,short:xx},..,],..}

        self.margin_dict = {}       # {instrument : [{date:xx,margin:xx},..,],..}

        self.profit_dict = {}       # {instrument : [{date:xx,long:xx,short:xx},..,],..}

        self.return_dict = {}       # {instrument : [{date:xx,return:xx},..,}],..}
        self.total_list = []        # [{date:xx,total:xx},..,..]


    def _update_cash(self, fillevent):
        pass

    def _update_position(self, fillevent):
        pass

    def _update_profit(self, fillevent):
        pass

    def _update_margin(self, fillevent):
        pass

    def _update_return(self, fillevent):
        pass

    def _update_total(self, fillevent):
        pass


    def _update_info(self,fillevent):
        self._update_cash(fillevent)
        self._update_position(fillevent)
        self._update_profit(fillevent)
        self._update_margin(fillevent)
        self._update_return(fillevent)
        self._update_total(fillevent)
