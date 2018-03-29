from OnePy.environment import Environment
from OnePy.event import EVENT, Event
from OnePy.sys_model.bars import Bar


class MarketMaker(object):

    env = Environment()

    def update_market(self):
        try:
            self.update_bar()
            self.update_recorder()
            self.env.event_bus.put(Event(EVENT.MARKET_UPDATED))

            return True
        except StopIteration:
            return False

    def initialize_feeds(self):
        for key, value in self.env.readers.items():
            self.env.feeds.update({key: Bar(value)})

    def update_recorder(self):
        for recorder in self.env.recorders.values():
            recorder.update()

    def update_bar(self):
        for iter_bar in self.env.feeds.values():
            iter_bar.next()
