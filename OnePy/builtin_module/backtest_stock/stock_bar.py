from OnePy.sys_module.models.base_bar import BarBase


class BarAshares(BarBase):

    @property
    def pre_date(self) -> str:
        return self.previous_ohlc['date']

    @property
    def pre_open(self) -> float:
        return self.previous_ohlc['open']

    @property
    def pre_high(self) -> float:
        return self.previous_ohlc['high']

    @property
    def pre_low(self) -> float:
        return self.previous_ohlc['low']

    @property
    def pre_close(self) -> float:
        return self.previous_ohlc['close']

    @property
    def pre_volume(self) -> float:
        return self.previous_ohlc['volume']

    @property
    def limit_up(self):
        return self.pre_close*1.1

    @property
    def limit_down(self):
        return self.pre_close*0.9
