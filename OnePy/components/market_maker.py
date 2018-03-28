from OnePy.sys_model.bars import Bar


class MarketMaker(object):

    env = None
    gvar = None

    def update_market(self):
        try:
            for iter_bar in self.env.feeds.values():
                iter_bar.next()

            return True
        except StopIteration:
            return False

    def initialize_feeds(self):
        for key, value in self.env.readers.items():
            self.env.feeds.update({key: Bar(value)})