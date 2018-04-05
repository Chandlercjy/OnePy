
from OnePy.environment import Environment
from OnePy.utils.clean import make_it_datetime, make_it_float


class Bar(object):
    env = Environment

    def __init__(self, reader):
        self._iter_data = reader.load()
        self.current_ohlc = None
        self.next_ohlc = next(self._iter_data)
        self.ticker = reader.ticker

    def next(self):
        self.current_ohlc, self.next_ohlc = self.next_ohlc, next(
            self._iter_data)
        self._update_trading_date()
        self.env.recorder.ohlc[self.ticker].append(self.current_ohlc)

    def _update_trading_date(self):
        self.env.gvar.trading_date = self.date

    @property
    def cur_price(self):
        return self.close

    @property  # type: ignore
    @make_it_float
    def execute_price(self):
        if self.env.execute_on_close_or_next_open == 'open':
            return self.next_ohlc['open']

        return self.close

    @property  # type: ignore
    def date(self):
        return self.current_ohlc['date']

    @property  # type: ignore
    @make_it_float
    def open(self):
        return self.current_ohlc['open']

    @property  # type: ignore
    @make_it_float
    def high(self):
        return self.current_ohlc['high']

    @property  # type: ignore
    @make_it_float
    def low(self):
        return self.current_ohlc['low']

    @property  # type: ignore
    @make_it_float
    def close(self):
        return self.current_ohlc['close']

    @property  # type: ignore
    @make_it_float
    def volume(self):
        return self.current_ohlc['volume']
