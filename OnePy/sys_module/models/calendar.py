
import arrow

from OnePy.sys_module.components.exceptions import BacktestFinished
from OnePy.sys_module.metabase_env import OnePyEnvBase
from OnePy.utils.easy_func import get_day_ratio


class Calendar(OnePyEnvBase):

    def __init__(self, instrument):
        if instrument == 'A_shares':
            self.is_trading_time = self._is_A_shares_trading_time
        elif instrument == 'Forex':
            self.is_trading_time = self._is_forex_trading_time

    def _is_forex_trading_time(self, now: arrow.arrow.Arrow) -> bool:
        weekday = now.isoweekday()
        date = now.format('YYYY-MM-DD')

        if weekday <= 4:
            return True

        elif weekday == 5:
            if now < arrow.get(f'{date} 22:00'):  # 夏令时为21点，冬令时为22点，但其实只要保持最大值即可。
                return True

        elif weekday == 6:
            return False

        elif weekday == 7:
            if now >= arrow.get(f'{date} 21:00'):
                return True

        return False

    def _is_A_shares_trading_time(self, now: arrow.arrow.Arrow) -> bool:
        weekday = now.isoweekday()
        date = now.format('YYYY-MM-DD')

        if self.env.sys_frequency == 'D':

            if weekday <= 5:
                return True

        else:

            if weekday <= 5:
                left_1 = arrow.get(f'{date} 09:30')
                right_1 = arrow.get(f'{date} 11:30')
                left_2 = arrow.get(f'{date} 13:00')
                right_2 = arrow.get(f'{date} 15:00')

                if left_1 <= now <= right_1 or left_2 <= now <= right_2:
                    return True

        return False

    def update_calendar(self):
        if self.env.is_live_trading:
            self.env.sys_date = arrow.utcnow().format('YYYY-MM-DD HH:mm:ss')
        else:
            self._check_todate()
            ratio = get_day_ratio(self.env.sys_frequency)
            new_sys_date = arrow.get(self.env.sys_date).shift(days=ratio)
            self.env.sys_date = new_sys_date.format('YYYY-MM-DD HH:mm:ss')

            while not self.is_trading_time(new_sys_date):
                self._check_todate()
                new_sys_date = arrow.get(self.env.sys_date).shift(days=ratio)
                self.env.sys_date = new_sys_date.format('YYYY-MM-DD HH:mm:ss')

    def _check_todate(self):
        if arrow.get(self.env.sys_date) >= arrow.get(self.env.todate):
            # TODO: 还有至少一个ticker时间超过
            raise BacktestFinished
