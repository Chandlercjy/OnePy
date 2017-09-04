from OnePy.broker.brokerbase import BrokerBase
from OnePy.event import FillEvent, events


class BacktestBroker(BrokerBase):
    def __init__(self):
        super(BacktestBroker, self).__init__()

    def submit_order(self):
        """发送交易指令"""
        fillevent = FillEvent(self.orderevent.order)
        events.put(fillevent)

    def check_before(self):
        """检查钱是否足够，Order是否能执行"""

        ls = ["TakeProfitOrder", "StopLossOrder", "TralingStopLossOrder",
              "Stop", "Limit", "CloseAll"]

        o = self.orderevent
        if o.target == "Forex":
            return (self.fill.cash[-1] >
                    o.per_margin * o.units + self.fill.margin[-1] * o.direction
                    or o.exectype in ls)

        elif o.target == "Futures":
            return (self.fill.cash[-1] >
                    o.per_margin * o.units* o.price * o.mult + self.fill.margin[-1] * o.direction
                    or o.exectype in ls)

        elif o.target == "Stock":
            return self.fill.cash[-1] > o.price * o.units or o.exectype in ls

    def check_after(self):
        """检查Order发送后是否执行成功"""
        return True

    def change_status(self, status):
        """
        改变订单状态
        Status = ["Created", "Submitted", "Accepted", "Partial", "Completed",
                  "Canceled", "Expired", "Margin", "Rejected",]
        """
        self.orderevent.status = status

    def start(self):
        self.notify()
        if self.check_before():
            self.change_status("Submitted")
            self.notify()
        else:
            print("Cash is not enough! Order Canceled")

    def prenext(self):
        pass

    def next(self):
        if self.check_before() and self.check_after():
            if self.orderevent.exectype in ["Limit", "Stop"]:
                self.change_status("Pending")
            else:
                self.change_status("Filled")
            self.submit_order()
            self.notify()

    def notify(self):
        if self._notify_onoff:
            print("{d}, {i}, {s} {st} @ {p}, units: {si}, Execute: {ot}\
            ".format(d=self.orderevent.date,
                     i=self.orderevent.instrument,
                     s=self.orderevent.ordtype,
                     st=self.orderevent.status,
                     p=self.orderevent.price,
                     si=self.orderevent.units,
                     ot=self.orderevent.exectype))

