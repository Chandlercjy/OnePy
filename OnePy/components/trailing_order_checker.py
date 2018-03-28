from OnePy.environment import Environment
from OnePy.variables import GlobalVariables


class TrailingOrderChecker(object):

    env = Environment()
    gvar = GlobalVariables()

    def __init__(self, signal):
        self.signal = signal
        self.ticker = signal.ticker
        self.trailingstop = signal.trailingstop
        self.trailingstop_pct = signal.trailingstop_pct
        self.latest_target_price = None
        self.target_below = None

    @property
    def is_pct(self):
        return True if self.trailingstop_pct else False

    def with_high(self, diff):
        return self.cur_high - diff

    def with_low(self, diff):
        return self.cur_low + diff

    def cur_price(self):
        return self.env.feeds[self.ticker].cur_price

    def cur_low(self):
        return self.env.feeds[self.ticker].cur_low

    def cur_high(self):
        return self.env.feeds[self.ticker].cur_high

    def set_target_direction(self, target_below=False):
        self.target_below = target_below

    def initialize_latest_target_price(self):
        if self.target_below:
            self.latest_target_price = self.cur_price - self.difference
        else:
            self.latest_target_price = self.cur_price + self.difference

    @property
    def target_price(self):

        if self.target_below:
            new = self.with_high(self.difference)
            self.latest_target_price = max(self.latest_target_price, new)
        else:
            new = self.with_low(self.difference)
            self.latest_target_price = min(self.latest_target_price, new)

        return self.latest_target_price

    @property
    def difference(self):
        if self.is_pct:
            return abs(self.trailingstop_pct*self.cur_price)

        return abs(self.trailingstop/self.signal.units)
