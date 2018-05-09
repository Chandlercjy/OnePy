from OnePy.sys_module.metabase_env import OnePyEnvBase


class BarBase(OnePyEnvBase):

    def __init__(self, reader):
        self._iter_data = reader.load()
        self.current_ohlc = None
        self.next_ohlc = next(self._iter_data)
        self.ticker = reader.ticker
        self._execute_mode = self.env.execute_on_close_or_next_open

    def next(self): # 更新行情
        self.current_ohlc, self.next_ohlc = self.next_ohlc, next(
            self._iter_data)

    @property
    def cur_price(self):
        return self.close

    @property
    def execute_price(self):
        if self._execute_mode == 'open':
            return self.next_ohlc['open']

        return self.close

    @property
    def date(self):
        return self.current_ohlc['date']

    @property
    def open(self):
        return self.current_ohlc['open']

    @property
    def high(self):
        return self.current_ohlc['high']

    @property
    def low(self):
        return self.current_ohlc['low']

    @property
    def close(self):
        return self.current_ohlc['close']

    @property
    def volume(self):
        return self.current_ohlc['volume']
