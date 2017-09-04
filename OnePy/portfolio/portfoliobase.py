# coding=utf8
from OnePy.event import OrderEvent, events


class PortfolioBase(object):
    def __init__(self):
        pass

    def generate_order(self):
        """生成OrderEvent"""
        order = self.signalevent.order
        events.put(OrderEvent(order))

    def start(self):
        pass

    def prenext(self):
        pass

    def next(self):
        self.generate_order()

    def run_portfolio(self, signalevent):
        self.signalevent = signalevent
        self.start()
        self.prenext()
        self.next()

    def stats(self):
        pass
