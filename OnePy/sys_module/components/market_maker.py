import arrow

from OnePy.event import EVENT, Event
from OnePy.sys_module.components.exceptions import (BacktestFinished,
                                                    BlowUpError)
from OnePy.sys_module.metabase_env import OnePyEnvBase


class MarketMaker(OnePyEnvBase):

    def update_market(self):
        try:
            self._update_bar()
            self._check_todate()
            self._update_recorder()
            self._check_blowup()
            self.env.event_bus.put(Event(EVENT.Market_updated))

        except (StopIteration, BlowUpError):
            self._update_recorder(final=True)  # 最后回测结束用close更新账户信息
            raise BacktestFinished

    def initialize(self):  # 系统初始化
        self._initialize_feeds()
        self._initialize_cleaners()

    def _initialize_feeds(self):  # 初始化行情
        for key, value in self.env.readers.items():
            self.env.feeds.update({key: value.get_bar()})

    def _initialize_cleaners(self):  # 初始化数据给cleaners处理
        for value in self.env.cleaners.values():
            value.initialize_buffer_data()

    def _update_recorder(self, final=False):  # 根据最新行情更新账户信息
        for recorder in self.env.recorders.values():
            recorder.update(final)

    def _update_bar(self):  # 更新行情
        for iter_bar in self.env.feeds.values():
            iter_bar.next()

    def _check_todate(self):  # 检查是否结束回测
        if self.env.todate:
            if arrow.get(self.env.trading_datetime) > arrow.get(self.env.todate):
                raise StopIteration

    def _check_blowup(self):  # 检查是否爆仓
        if self.env.recorder.balance.latest() < 0:
            self.env.logger.critical("The account is BLOW UP!")
            raise BlowUpError
