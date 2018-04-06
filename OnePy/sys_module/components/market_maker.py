import arrow

from OnePy.environment import Environment
from OnePy.event import EVENT, Event


class MarketMaker(object):

    env = Environment

    def update_market(self):
        try:
            self.update_bar()
            self.check_todate()
            self.update_recorder()
            self.env.event_bus.put(Event(EVENT.Market_updated))

            return True
        except StopIteration:
            self.update_recorder(final=True)

            return False

    def initialize_feeds(self):
        for key, value in self.env.readers.items():
            self.env.feeds.update({key: value.get_bar()})

    def update_recorder(self, final=False):
        for recorder in self.env.recorders.values():
            recorder.update(final)

    def update_bar(self):
        for iter_bar in self.env.feeds.values():
            iter_bar.next()

    def check_todate(self):
        if self.env.todate:
            if arrow.get(self.env.gvar.trading_date) > arrow.get(self.env.todate):
                raise StopIteration
